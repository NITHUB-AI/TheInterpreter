import tempfile
import os
from util.media import extract_audio_and_video_parts, stitch_audio_and_video
from util.files import get_audio_bytes

script_dir = os.path.dirname(__file__)
dump_dir = os.path.join(script_dir, 'dump')
files_dir = os.path.join(script_dir, 'files')
test_video = os.path.join(files_dir, 'test_video.mp4')


def test_audio_and_video_extraction():
    only_audio, only_video = extract_audio_and_video_parts(
        test_video, dump_dir)
    print(only_audio, only_video)

    res = stitch_audio_and_video(only_audio, only_video, os.path.join(dump_dir, 'out.mp4'))
    print(res)


if __name__ == "__main__":
    test_audio_and_video_extraction()
