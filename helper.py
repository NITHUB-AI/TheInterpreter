import os
from dotenv import load_dotenv
import librosa
import soundfile as sf
# s2t API
import openai
# t2t
import requests

# mms-tts
import subprocess
import locale

locale.getpreferredencoding = lambda do_setlocale=True: "UTF-8"

import re
import glob
import json
import tempfile
import math
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader
import numpy as np
import commons
import utils
import argparse
import subprocess
from data_utils import TextAudioLoader, TextAudioCollate, TextAudioSpeakerLoader, TextAudioSpeakerCollate
from models import SynthesizerTrn
from scipy.io.wavfile import write

load_dotenv()

HELSINKI_API_URL = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-fr"
headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}

def download(lang, tgt_dir="./"):
  lang_fn, lang_dir = os.path.join(tgt_dir, lang+'.tar.gz'), os.path.join(tgt_dir, lang)
  cmd = ";".join([
        f"wget https://dl.fbaipublicfiles.com/mms/tts/{lang}.tar.gz -O {lang_fn}",
        f"tar zxvf {lang_fn}"
  ])
  if not os.path.exists(lang):
    print(f"Download model for language: {lang}")
    subprocess.check_output(cmd, shell=True)
  print(f"Model checkpoints in {lang_dir}: {os.listdir(lang_dir)}")
  return lang_dir

LANG = "fra"
ckpt_dir = download(LANG)

def preprocess_char(text, lang=None):
    """
    Special treatement of characters in certain languages
    """
    print(lang)
    if lang == 'ron':
        text = text.replace("ț", "ţ")
    return text

class TextMapper(object):
    def __init__(self, vocab_file):
        self.symbols = [x.replace("\n", "") for x in open(vocab_file, encoding="utf-8").readlines()]
        self.SPACE_ID = self.symbols.index(" ")
        self._symbol_to_id = {s: i for i, s in enumerate(self.symbols)}
        self._id_to_symbol = {i: s for i, s in enumerate(self.symbols)}

    def text_to_sequence(self, text, cleaner_names):
        '''Converts a string of text to a sequence of IDs corresponding to the symbols in the text.
        Args:
        text: string to convert to a sequence
        cleaner_names: names of the cleaner functions to run the text through
        Returns:
        List of integers corresponding to the symbols in the text
        '''
        sequence = []
        clean_text = text.strip()
        for symbol in clean_text:
            symbol_id = self._symbol_to_id[symbol]
            sequence += [symbol_id]
        return sequence

    def uromanize(self, text, uroman_pl):
        iso = "xxx"
        with tempfile.NamedTemporaryFile() as tf, \
             tempfile.NamedTemporaryFile() as tf2:
            with open(tf.name, "w") as f:
                f.write("\n".join([text]))
            cmd = f"perl " + uroman_pl
            cmd += f" -l {iso} "
            cmd +=  f" < {tf.name} > {tf2.name}"
            os.system(cmd)
            outtexts = []
            with open(tf2.name) as f:
                for line in f:
                    line =  re.sub(r"\s+", " ", line).strip()
                    outtexts.append(line)
            outtext = outtexts[0]
        return outtext

    def get_text(self, text, hps):
        text_norm = self.text_to_sequence(text, hps.data.text_cleaners)
        if hps.data.add_blank:
            text_norm = commons.intersperse(text_norm, 0)
        text_norm = torch.LongTensor(text_norm)
        return text_norm

    def filter_oov(self, text):
        val_chars = self._symbol_to_id
        txt_filt = "".join(list(filter(lambda x: x in val_chars, text)))
        print(f"text after filtering OOV: {txt_filt}")
        return txt_filt

def preprocess_text(txt, text_mapper, hps, uroman_dir=None, lang=None):
    # print("txt: ", txt)
    txt = preprocess_char(txt, lang=lang)
    is_uroman = hps.data.training_files.split('.')[-1] == 'uroman'
    if is_uroman:
        with tempfile.TemporaryDirectory() as tmp_dir:
            if uroman_dir is None:
                cmd = f"git clone git@github.com:isi-nlp/uroman.git {tmp_dir}"
                print(cmd)
                subprocess.check_output(cmd, shell=True)
                uroman_dir = tmp_dir
            uroman_pl = os.path.join(uroman_dir, "bin", "uroman.pl")
            print(f"uromanize")
            txt = text_mapper.uromanize(txt, uroman_pl)
            print(f"uroman text: {txt}")
    txt = txt.lower()
    txt = text_mapper.filter_oov(txt)
    return txt

# if torch.cuda.is_available():
#     device = torch.device("cuda")
# else:
device = torch.device("cpu")

print(f"Run inference with {device}")
vocab_file = f"{ckpt_dir}/vocab.txt"
config_file = f"{ckpt_dir}/config.json"
assert os.path.isfile(config_file), f"{config_file} doesn't exist"
hps = utils.get_hparams_from_file(config_file)
text_mapper = TextMapper(vocab_file)
net_g = SynthesizerTrn(
    len(text_mapper.symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    **hps.model)
net_g.to(device)
_ = net_g.eval()

g_pth = f"{ckpt_dir}/G_100000.pth"
print(f"load {g_pth}")

_ = utils.load_checkpoint(g_pth, net_g, None)

def convert_audio(input_file, target_sr=16000):
    filename = re.split(r'\.|\\|/', input_file)[-2]
    output_file = f"{filename}_{target_sr}.wav"
    subprocess.call(f'ffmpeg -i {input_file} -ac 1 -ar {target_sr} {output_file}', shell=True)
    sr = 16000 if target_sr == 48000 else 48000
    # # Load the audio file
    # y, sr = librosa.load(input_file, sr=None, mono=True)

    # # Resample the audio to 16000 Hz if necessary
    # if sr != target_sr:
    #     y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)

    # # Save the audio in WAV format
    # filename = re.split(r'\.|\\|/', input_file)[-2]
    # output_file = f"{filename}_{target_sr}.wav"
    # sf.write(output_file, y, target_sr)
    return output_file, sr

def transcribe(file_path, api=False):
    if api:
        audio_file= open(file_path, "rb")
        result = openai.Audio.transcribe("whisper-1", audio_file, api_key=os.getenv("OPENAI_API_KEY"))
    else:
        API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v2"

        with open(file_path, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)
        result = response.json()
    transcript = result['text']

    return transcript

def helsinki_t2t(en_transcript):
    payload = {"inputs": en_transcript}
    response = requests.post(HELSINKI_API_URL, headers=headers, json=payload)
    print(response.json())
    fr_sentence = response.json()[0]["translation_text"]
    return fr_sentence

def mms_tts(txt, translated_audio):
    # print(f"text: {txt}")
    txt = preprocess_text(txt, text_mapper, hps, lang=LANG)
    stn_tst = text_mapper.get_text(txt, hps)
    with torch.no_grad():
        x_tst = stn_tst.unsqueeze(0).to(device)
        x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).to(device)
        hyp = net_g.infer(
            x_tst, x_tst_lengths, noise_scale=.667,
            noise_scale_w=0.8, length_scale=1.0
        )[0][0,0].cpu().float().numpy()

    sf.write(translated_audio, hyp, hps.data.sampling_rate)
    return translated_audio

def helsinki_mms_t2st(en_transcript, translated_audio):
    translated_text = helsinki_t2t(en_transcript)
    mms_tts(translated_text, translated_audio)
    return translated_text, translated_audio