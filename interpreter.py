import sys
sys.path.append("./vits")

from helper import convert_audio, transcribe, seamless_t2st, MODE
import argparse
import re
import os
import time
import logging
logging.getLogger().setLevel(logging.ERROR)


if MODE == "3STEP":
    from helper import helsinki_mms_t2st

def speech_to_speech(file_path):
    print(f"Starting in {MODE} mode...")
    target_sr = 16000

    print(f"Resampling file to {target_sr}...")
    converted_file_path, sampling_rate = convert_audio(file_path, target_sr)
    
    print("Transcribing audio file...")
    en_text = transcribe(converted_file_path)
    print(en_text)
    print("translating text and generating speech...")
    file_name = re.split(r'/|\\|\.', file_path)[-2]
    if "2STEP" in MODE:
        translated_text, translated_audio = seamless_t2st(en_text, f"fr_{file_name}.wav")
    else:
        translated_text, translated_audio = helsinki_mms_t2st(en_text, f"fr_{file_name}.wav")

    print(f"Resampling file to {sampling_rate}...")
    translated_audio, _ = convert_audio(translated_audio, target_sr=sampling_rate)
    
    print("Cleaning up...")
    for file in os.listdir():
        if file[-3:] == "wav" and file != translated_audio:
            os.remove(file)
    print("End.")

    return translated_text, translated_audio

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process an audio file.')
    parser.add_argument('audio_path', type=str, help='Path to the audio file')
    

    args = parser.parse_args()
    
    a = time.time()
    translated_text, translated_audio = speech_to_speech(args.audio_path)
    print(time.time() - a)
    print(translated_text)
    print(translated_audio)