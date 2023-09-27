import ffmpeg
import os
from .files import generate_filename

# Extracts the audio and video streams from a video and return their file locations.
def extract_audio_and_video_parts(video_file: str, output_dir: str) -> tuple[str, str]:
    # generate file paths for the audio and video streams
    out_audio = os.path.join(output_dir, generate_filename(extension='.wav'))
    out_video = os.path.join(output_dir, generate_filename(extension='.mp4'))

    inp = ffmpeg.input(video_file)
    audio = ffmpeg.output(inp.audio, out_audio)
    video = ffmpeg.output(inp.video, out_video)

    return audio, video

# Combines an audio and video source into a single video file.
def stitch_audio_and_video(audio_file: str, video_file: str, output_file: str) -> str:
    audio = ffmpeg.input(audio_file)
    video = ffmpeg.input(video_file)
    return ffmpeg.output(audio, video, output_file)