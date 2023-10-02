import sys
sys.path.append("./vits")

from helper import convert_audio, transcribe, seamless_t2st, MODE
from util.media import extract_audio_and_video_parts, stitch_audio_and_video
from util.files import generate_filename
import argparse
import re
import os
import time
import tempfile
import logging
logging.getLogger().setLevel(logging.ERROR)


if MODE == "3STEP":
    from helper import helsinki_mms_t2st

def speech_to_speech(file_path):
    print(f"Starting in {MODE} mode...")
    target_sr = 16000

    with tempfile.NamedTemporaryFile('wb+', suffix='.mp3', delete=True) as tempf:
        print(f"Resampling file to {target_sr}...")
        converted_file_path, sampling_rate = convert_audio(file_path, tempf.name, target_sr)
        
        print("Transcribing audio file...")
        en_text = transcribe(converted_file_path)
    print(en_text)

    print("translating text and generating speech...")
    with tempfile.NamedTemporaryFile('wb+', suffix='.mp3', delete=True) as tempf:
        if "2STEP" in MODE:
            translated_text, translated_audio = seamless_t2st(en_text, tempf.name)
        else:
            translated_text, translated_audio = helsinki_mms_t2st(en_text, tempf.name)

        print(f"Resampling file to {sampling_rate}...")
        file_name = re.split(r'/|\\|\.', file_path)[-2]
        translated_audio, _ = convert_audio(translated_audio, f"fr_{file_name}_{int(time.time())}.mp3", target_sr=sampling_rate)
    print("End.")

    return translated_text, translated_audio


def video_to_video(file_path: str) -> str:
    with tempfile.TemporaryDirectory() as tempdir:
        # grab audio and video streams
        audio, video = extract_audio_and_video_parts(file_path, tempdir)

        # translate audio
        translated_text, translated_audio = speech_to_speech(audio)
        print("Translated text:", translated_text)

        # combine audio and video
        out_file = generate_filename(extension='.mp4')
        success = stitch_audio_and_video(translated_audio, video, out_file)

        return None if not success else out_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process an audio file.')
    parser.add_argument('audio_path', type=str, help='Path to the audio file')
    

    args = parser.parse_args()
    
    a = time.time()
    translated_text, translated_audio = speech_to_speech(args.audio_path)
    print(time.time() - a)
    print(translated_text)
    print(translated_audio)