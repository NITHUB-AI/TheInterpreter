import sys
sys.path.append("./vits")

import os
import pathlib
import streamlit as st
import tempfile
import time
from interpreter import video_to_video
from helper import split_video, merge_video

def get_video_download(video_file):
    with open(video_file, 'rb') as audio:
        return audio.read()


def translate_video():
    video_file = st.file_uploader(
        label="Select a video file to transcribe and translate",
        type=["mp4", "avi", "mov"],
        accept_multiple_files=False)

    if video_file:
        ext = pathlib.Path(video_file.name).suffix
        with tempfile.NamedTemporaryFile(suffix=ext) as tmp_file:
            tmp_file.write(video_file.read())
            
            a = time.time()
            with tempfile.TemporaryDirectory() as tempdir:
                video_file = tmp_file.name
                save_dir = f'{tempdir}/vchunks'
                chunk_dir = f'{tempdir}/trans_chunks'
                _, video_name = split_video(video_file, save_dir)


                # translate video chunks
                for i, vchunk in enumerate(sorted(os.listdir(save_dir))):
                    start = time.time()
                    video_to_video(f'{save_dir}/{vchunk}', chunk_dir)
                    end = time.time() - start
                    st.write(f'Translated chunk {i+1} in {end}s.')

                # merge translated videos together
                translated_video = merge_video(video_name, chunk_dir, prefix='fr')

            time_spent = time.time() - a

            if not translate_video:
                st.write("We could not process your video, sorry.")
                return

            st.subheader("Results")
            st.write(f"It took {time_spent}s to process your video")

            st.download_button(
                label="Here's your translated video",
                data=get_video_download(translated_video),
                file_name=translated_video,
                # the produced audio is an mp4 file. this should be changed if the
                # video mimetype changes
                mime="video/mp4",
                key="video_download_btn"
            )
