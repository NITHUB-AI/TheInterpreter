import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import subprocess
from util.media import FfmpegCommand
from util.files import generate_filename
import tempfile
from interpreter import speech_to_speech


def remove_noise(file_path, output_file):
    cmd = (FfmpegCommand()
           .input(file_path)
           .arg("af", "highpass=200,lowpass=3000,afftdn")
           .output(output_file)
           .build())
    print(cmd)
    ret = subprocess.check_call(cmd, shell=True)
    return ret == 0


def run(audio_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        denoised_audio_path = os.path.join(
            tmpdir, generate_filename(extension=".mp3"))
        if not remove_noise(audio_path, denoised_audio_path):
            return False

        audio = AudioSegment.from_mp3(denoised_audio_path)

        audio_segments = detect_nonsilent(
            audio, min_silence_len=1000, silence_thresh=-45)

        max_slice_size_ms = 2 * 1000

        if not audio_segments:
            # it was all silence
            return True

        first_audio_start, _ = audio_segments[0]
        if first_audio_start != 0:
            # there's silence at the beginning of the audio. let's add it back
            process_audio_slice(AudioSegment.silent(
                first_audio_start, audio.frame_rate), True)

        for j in range(len(audio_segments)):
            start, end = audio_segments[j]
            audio_seg = audio[start:end]

            # ensure we're not processing too large chunks
            for i in range(0, len(audio_seg), max_slice_size_ms):
                audio_slice = audio_seg[i: i+max_slice_size_ms]
                process_audio_slice(audio_slice)

            # add removed silence if we're not at the end
            if j < len(audio_segments) - 1:
                next_audio_start, _ = audio_segments[j+1]
                process_audio_slice(AudioSegment.silent(
                    next_audio_start - end, audio.frame_rate), True)

        _, last_audio_end = audio_segments[-1]
        if last_audio_end != len(audio):
            # there's silence at the end of the audio. let's add it back
            process_audio_slice(AudioSegment.silent(
                len(audio) - last_audio_end, audio.frame_rate
            ), True)

aa = AudioSegment.empty()
def process_audio_slice(seg: AudioSegment, is_silence=False):
    global aa
    if is_silence:
        aa = aa + seg
        return
    
    with tempfile.NamedTemporaryFile(suffix=".mp3") as tmpfile:
        seg.export(tmpfile.name)
        _, translated_audio = speech_to_speech(tmpfile.name)
        aa = aa + AudioSegment(translated_audio)
        

if __name__ == "__main__":
    run("audio.mp3")
    aa.export("exported.mp3")
