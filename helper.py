# import libraries models:
import os
import json
import re
import requests
import subprocess
from util.media import FfmpegCommand
from util.files import generate_filename
from dotenv import load_dotenv
# s2t API
import openai
# t2st
import torch

load_dotenv()

MODE = os.getenv("MODE").upper()
print(MODE)

if MODE == "2STEP":
    # load models locally
    import whisper
    from seamless_communication.models.inference import Translator
    import torchaudio
elif MODE == "API_2STEP":
    # use gradio client
    from gradio_client import Client
elif MODE == "3STEP":
    import scipy
    from TTS.api import TTS
    # from transformers import VitsModel, AutoTokenizer

HEADER = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}
HELSINKI_API_URL = "https://nithub-ai-helsinki-opus-mt-en-fr.hf.space/api/predict"
openai.api_key = os.getenv("OPENAI_API_KEY")

if MODE == "2STEP":
    # openai whisper
    model = whisper.load_model("large")
    # facebook seamlessm4t
    translator = Translator("seamlessM4T_large", vocoder_name_or_card="vocoder_36langs", device=torch.device("cpu"))

if MODE == "3STEP":
    model = ... # VitsModel.from_pretrained("facebook/mms-tts-fra")
    tokenizer = ... # AutoTokenizer.from_pretrained("facebook/mms-tts-fra")

    # Init TTS with the target model name
    mms_tts = ... # TTS(model_name="tts_models/fra/fairseq/vits")
    css10_tts = TTS(model_name='tts_models/fr/css10/vits')


def get_duration(input_filename):
    out = subprocess.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", input_filename])
    ffprobe_data = json.loads(out)
    duration_seconds = float(ffprobe_data["format"]["duration"])
    return duration_seconds

def convert_audio(input_file, output_file, target_sr=16000):
    # Load the audio file
    subprocess.call(f'ffmpeg -loglevel error -y -i {input_file} -ac 1 -ar {target_sr} {output_file}', shell=True)
    sr = 16000 if target_sr == 48000 else 48000
    return output_file, sr

def transcribe(file_path, prompt='', api="openai"):
    assert api in ["hf", "openai"], "Invalid API parameter."
    if MODE == "2STEP":
        result = model.transcribe(file_path, language='English', temperature=0, prompt=prompt)
    else:
        if api == "openai":
            audio_file= open(file_path, "rb")
            result = openai.Audio.transcribe(
                "whisper-1", audio_file, 
                api_key=os.getenv("OPENAI_API_KEY"), language='en'
            )
        else:
            API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v2"
            with open(file_path, "rb") as f:
                data = f.read()
            response = requests.post(API_URL, headers=HEADER, data=data)
            result = response.json()

    transcript = result["text"]
    return transcript

def seamless_t2st(transcript, translated_audio):
    if MODE == "2STEP":
        translated_text, wav, sr = translator.predict(
            transcript,
            "t2st", 'fra', src_lang='eng'
        )
        wav = wav[0].cpu()

        torchaudio.save(
            translated_audio,
            wav,
            sample_rate=sr,
        )
    else:
        client = Client("https://facebook-seamless-m4t.hf.space/")
        result = client.predict(
                        "T2ST (Text to Speech translation)",	# str (Option from: ['S2ST (Speech to Speech translation)', 'S2TT (Speech to Text translation)', 'T2ST (Text to Speech translation)', 'T2TT (Text to Text translation)', 'ASR (Automatic Speech Recognition)'])				
                        "file",	# str in 'Audio source' Radio component
                        "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav",
                        "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav",
                        f"{transcript}[END]",
                        "English",
                        "French",
                        api_name="/run"
        )
        translated_audio, translated_text = result
    return translated_text, translated_audio

def helsinki_t2t(en_transcript):
    payload = {"data": [en_transcript], "session_hash": ""}
    response = requests.post(HELSINKI_API_URL, headers=HEADER, json=payload)
    # print(response.json())
    fr_sentence = response.json()["data"][0]
    return fr_sentence

def openai_t2t(en_transcript):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
        "role": "system",
        "content": "You will be provided with a sentence in English, and your task is to translate it into French accurately and exactly."
        },
        {
        "role": "user",
        "content": en_transcript
        },
    ],
    temperature=0,
    max_tokens=512,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    )
    fr_sentence = response["choices"][0]["message"]["content"]
    return fr_sentence

def facebook_mms_tts(fr_sentence, translated_audio):
    inputs = tokenizer(fr_sentence, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform
    scipy.io.wavfile.write(translated_audio, rate=model.config.sampling_rate, data=output.numpy()[0])

def coqui_tts(fr_sentence, translated_audio, model_id='css10'):
    assert model_id in ["css10", "mms"], "Invalid API parameter."
    model = css10_tts if model_id == 'css10' else mms_tts
    model.tts_to_file(
        text=fr_sentence, 
        file_path=translated_audio,
    )

def text_to_speech_translation(en_transcript, translated_audio, t2t='openai'):
    assert t2t in ["hf", "openai"], "Invalid API parameter."
    if t2t == 'hf':
        translated_text = helsinki_t2t(en_transcript)
    else:
        translated_text = openai_t2t(en_transcript)
    # facebook_mms_tts(translated_text, translated_audio)
    coqui_tts(translated_text, translated_audio)
    return translated_text, translated_audio

def split_video(video_path, save_dir):

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    file_name = re.split(r'/|\\|\.', video_path)[-2]
    cmd = (FfmpegCommand()
           .input(video_path)
           .arg('y', None)
           .arg('map', '0')
           .arg('segment_time', '00:00:30')
           .arg('reset_timestamps', '1')
           .arg('f', 'segment')
           .arg('c', 'copy')
           .output(f"{save_dir}/{file_name}%03d.mp4")
           .build())

    retcode = subprocess.call(cmd, shell=True)
    print(retcode)
    return save_dir, file_name if retcode == 0 else None

def merge_video(file_name, chunk_dir, prefix='fr'):
    # merge translated videos together
    video_list = generate_filename(extension='.txt')
    subprocess.call(f"""for f in {chunk_dir}/*.mp4; do echo "file '$f'" >> {video_list}; done""", shell=True)
    out_video = f"{prefix}_{file_name}.mp4"
    cmd = (FfmpegCommand()
            .arg('f', "concat")
            .arg('safe', 0)
            .arg('i', video_list)
            .arg('c', 'copy')
            .output(out_video)
            .build())

    retcode = subprocess.call(cmd, shell=True)
    return out_video if retcode == 0 else None