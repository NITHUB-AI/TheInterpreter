# import libraries models:
import os
import re
import requests
import subprocess
import time
from dotenv import load_dotenv
# s2t API
import openai
# t2st
import torch

load_dotenv()

MODE = os.getenv("MODE").upper()

if MODE == "2STEP":
    # load models locally
    import whisper
    from seamless_communication.models.inference import Translator
    import torchaudio
elif MODE == "API_2STEP":
    # use gradio client
    from gradio_client import Client

HEADER = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}


if MODE == "2STEP":
    # openai whisper
    model = whisper.load_model("large")

    # facebook seamlessm4t
    translator = Translator("seamlessM4T_large", vocoder_name_or_card="vocoder_36langs", device=torch.device("cpu"))

def convert_audio(input_file, target_sr=16000):
    # Load the audio file
    filename = re.split(r'\.|\\|/', input_file)[-2]
    output_file = f"{filename}_{target_sr}_{time.time()}.wav"
    subprocess.call(f'ffmpeg -i {input_file} -ac 1 -ar {target_sr} {output_file}', shell=True)
    sr = 16000 if target_sr == 48000 else 48000
    return output_file, sr

def transcribe(file_path, api="openai"):
    assert api in ["hf", "openai"], "Invalid API parameter."
    if MODE == "2STEP":
        result = model.transcribe(file_path, language='English', temperature=0)
    else:
        if api == "openai":
            audio_file= open(file_path, "rb")
            result = openai.Audio.transcribe("whisper-1", audio_file, api_key=os.getenv("OPENAI_API_KEY"))
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