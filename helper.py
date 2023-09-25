from dotenv import load_dotenv
from gradio_client import Client
import requests
import os
import re
# audio conversion
import openai
import soundfile as sf
import subprocess

load_dotenv()

headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}

def convert_audio(input_file, target_sr=16000):
    # Load the audio file
    filename = re.split(r'\.|\\|/', input_file)[-2]
    output_file = f"{filename}_{target_sr}.wav"
    subprocess.call(f'ffmpeg -i {input_file} -ac 1 -ar {target_sr} {output_file}', shell=True)
    sr = 16000 if target_sr == 48000 else 48000
    return output_file, sr

def transcribe(file_path, api=False):
    if api:
        audio_file= open(file_path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file, api_key=os.getenv("OPENAI_API_KEY"))
    else:
        API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v2"

        with open(file_path, "rb") as f:
            data = f.read()
        response = requests.post(API_URL, headers=headers, data=data)
        transcript = response.json()['text']

    return transcript

def seamless_t2st(transcript, translated_audio):
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