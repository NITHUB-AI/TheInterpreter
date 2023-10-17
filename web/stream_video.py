import os
import pathlib
import streamlit as st
import tempfile
import time
from interpreter import video_to_video
from helper import split_video, get_duration
# introducing
import subprocess
import threading
from collections import deque 

# Queue to hold video chunks
video_queue = deque()

# Global flag to control streaming
streaming_active = False

def get_video_download(video_file):
    with open(video_file, 'rb') as video:
        return video.read()
    
def translate_video_chunks(save_dir, chunk_dir):
    sorted_en_chunks = sorted(os.listdir(save_dir))
    for vchunk in sorted_en_chunks:
        tchunk = video_to_video(f'{save_dir}/{vchunk}', chunk_dir)
        video_queue.append(f"{chunk_dir}/{tchunk}")

def stream_video():
    global streaming_active  # Declare the global flag

    video_file = st.file_uploader(
        label="Select a video file to transcribe and translate",
        type=["mp4", "avi", "mov"],
        accept_multiple_files=False)
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        start_button = st.button("Start Streaming")
    with col2:
        stop_button = st.button("Stop Streaming")

    # Update the global flag when buttons are pressed
    if start_button:
        streaming_active = True
    if stop_button:
        streaming_active = False

    if video_file:
        ext = pathlib.Path(video_file.name).suffix
        with tempfile.NamedTemporaryFile(suffix=ext) as tmp_file:
            tmp_file.write(video_file.read())

            with tempfile.TemporaryDirectory() as tempdir:
                video_file = tmp_file.name
                save_dir = f'{tempdir}/vchunks'
                chunk_dir = f'{tempdir}/trans_chunks'

                _ = split_video(video_file, save_dir)

                # Create and start the thread, passing the directories as arguments
                translation_thread = threading.Thread(
                    target=translate_video_chunks, args=(save_dir, chunk_dir)
                )
                translation_thread.start()

                st.markdown("Watch the live video on https://www.youtube.com/@fortuneadekogbe4438/streams.")# st.video("https://youtube.com/live/YPVkUZCA_SU")

                while True:
                    if streaming_active and video_queue:
                        video_path = video_queue.popleft()
                        print(f"Streaming {video_path}...")
                        start = time.time()
                        stream_key = "tqsz-8vgc-pjqm-pgqh-2cuy"
                        command = (f'ffmpeg -loglevel error -re -i {video_path} -c:v libx264 -preset medium -crf 22 '
                                   f'-c:a aac -f flv rtmp://a.rtmp.youtube.com/live2/{stream_key}')
                        subprocess.run(command, shell=True)
                        print(time.time() - start)
