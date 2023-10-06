# import sys
# sys.path.append("./vits")

from helper import convert_audio, transcribe, seamless_t2st, get_duration, MODE
from util.media import extract_audio_and_video_parts, stitch_audio_and_video, FfmpegCommand
from util.files import generate_filename
import argparse
import re
import os
import subprocess
import time
import tempfile
import logging
logging.getLogger().setLevel(logging.ERROR)


if MODE == "3STEP":
    from helper import text_to_speech_translation

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
            translated_text, translated_audio = text_to_speech_translation(en_text, tempf.name)

        print(f"Resampling file to {sampling_rate}...")
        file_name = re.split(r'/|\\|\.', file_path)[-2] # .split('.')[-2]
        translated_audio, _ = convert_audio(translated_audio, f"{file_name}_fr.mp3", target_sr=sampling_rate)
    print("End.")

    return translated_text, translated_audio


def video_to_video(file_path: str, save_dir='test/trans_chunks') -> str:
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    with tempfile.TemporaryDirectory() as tempdir:
        # grab audio and video streams
        audio, video = extract_audio_and_video_parts(file_path, tempdir)

        # translate audio
        translated_text, translated_audio = speech_to_speech(audio)
        print("Translated text:", translated_text)

        # slow down playback speed
        playback_speed = 0.75
        original_duration = get_duration(audio)
        translated_duration = get_duration(translated_audio)
        
        if translated_duration / original_duration <= playback_speed:
            adjusted_audio = os.path.join(tempdir, generate_filename(extension='.mp3'))
            cmd = (FfmpegCommand()
            .input(translated_audio)
            .arg('filter:a', f'"atempo={playback_speed}"')
            .output(adjusted_audio)            
            .build())

            subprocess.call(cmd, shell=True)
        # elif translated_duration > original_duration:
        #   # truncate video length.
        #     ...
        else:
            adjusted_audio = translated_audio

        # combine audio and video
        out_file = generate_filename(extension='.mp4')
        success = stitch_audio_and_video(adjusted_audio, video, f"{save_dir}/{out_file}")

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