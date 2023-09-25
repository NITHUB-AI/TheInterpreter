# import libraries models:
import os
import re
import subprocess
from dotenv import load_dotenv
load_dotenv()

MODE = os.getenv("MODE")

# s2t API
import openai
# t2st
import torch

if MODE == "2STEP":
    # s2t OS
    import whisper
    from seamless_communication.models.inference import Translator
    import torchaudio

if MODE == "2STEP":
    # openai whisper
    model = whisper.load_model("large")

    # facebook seamlessm4t
    translator = Translator("seamlessM4T_large", vocoder_name_or_card="vocoder_36langs", device=torch.device("cpu"))

def convert_audio(input_file, target_sr=16000):
    # Load the audio file
    filename = re.split(r'\.|\\|/', input_file)[-2]
    output_file = f"{filename}_{target_sr}.wav"
    subprocess.call(f'ffmpeg -i {input_file} -ac 1 -ar {target_sr} {output_file}', shell=True)
    sr = 16000 if target_sr == 48000 else 48000
    return output_file, sr

def transcribe(file_path, api="openai"):
    assert api in ["hf", "openai"], "Invalid API parameter."
    if MODE == "2STEP":
        result = model.transcribe(file_path, language='English', temperature=0)
    else:
        audio_file= open(file_path, "rb")
        result = openai.Audio.transcribe("whisper-1", audio_file, api_key=os.getenv("OPENAI_API_KEY"))
    transcript = result["text"]
    return transcript

def seamless_t2st(transcript, translated_audio):
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
    return translated_text, translated_audio