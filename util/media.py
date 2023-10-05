import os
import subprocess
from .files import generate_filename


# Extracts the audio and video streams from a video and return their file locations.
def extract_audio_and_video_parts(video_file: str, output_dir: str) -> tuple: #[str | None, str | None]:
    # generate file paths for the audio and video streams
    out_audio = os.path.join(output_dir, generate_filename(extension='.mp3'))
    out_video = os.path.join(output_dir, generate_filename(extension='.mp4'))

    # extract audio
    cmd = (FfmpegCommand()
           .input(video_file)
           .arg('q:a', 0)
           .arg('map', 'a')
           .output(out_audio)
           .build())
    audio_retcode = subprocess.call(cmd, shell=True)
    print(cmd)

    # extract video
    cmd = (FfmpegCommand()
           .input(video_file)
           .arg('an', None)
           .output(out_video)
           .build())
    video_retcode = subprocess.call(cmd, shell=True)
    print(cmd)

    return None if audio_retcode != 0 else out_audio, None if video_retcode != 0 else out_video


# Combines an audio and video source into a single video file.
def stitch_audio_and_video(audio_file: str, video_file: str, output_file: str) -> bool:
    cmd = (FfmpegCommand()
           .input(video_file)
           .input(audio_file)
           .arg('c:v', 'copy')
           .arg('c:a', 'copy')
           .output(output_file)
           .build())
    print(cmd)
    retcode = subprocess.call(cmd, shell=True)
    return True if retcode == 0 else False


class FfmpegCommand:
    def __init__(self) -> None:
        self._inputs = []
        self._args = []
        self._out = ""

    def input(self, inp: str):
        self._inputs.append(inp)
        return self

    def arg(self, key: str, value: any):
        self._args.append((key, value))
        return self

    def output(self, out: str):
        self._out = out
        return self

    def build(self):
        inputs = self._build_inputs()
        args = self._build_args()
        return f'ffmpeg -loglevel error {inputs} {args} {self._out}'

    def _build_inputs(self):
        inputs = []
        for inp in self._inputs:
            inputs.append(f'-i {inp}')
        return " ".join(inputs)

    def _build_args(self):
        args = []
        for k, v in self._args:
            if v is None:
                args.append(f'-{k}')
            else:
                args.append(f'-{k} {v}')
        return " ".join(args)
