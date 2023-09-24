# import libraries models:

import os
# audio conversion
import librosa
import soundfile as sf
# s2t API
from dotenv import load_dotenv
import openai
# s2t OS
#import whisper
# t2st
import torch
from seamless_communication.models.inference import Translator
import torchaudio

load_dotenv()
# load models:
# openai whisper
model = ... # whisper.load_model("large")

# facebook seamlessm4t
translator = Translator("seamlessM4T_large", vocoder_name_or_card="vocoder_36langs", device=torch.device("cpu"))

def convert_audio(input_file, target_sr=16000):
    # Load the audio file
    y, sr = librosa.load(input_file, sr=None, mono=True)

    # Resample the audio to {target_sr} Hz if necessary
    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)

    # Save the audio in WAV format
    output_file = f'{input_file[:-4]}_{target_sr}.wav'
    sf.write(output_file, y, target_sr)
    return output_file, sr

def transcribe(file_path, api=False):
    if api:
        audio_file= open(file_path, "rb")
        result = openai.Audio.transcribe("whisper-1", audio_file, api_key=os.getenv("OPENAI_API_KEY"))
    else:
        result = model.transcribe(file_path, language='English', temperature=0)
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