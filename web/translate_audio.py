import os
import streamlit as st
import tempfile
import time
from interpreter import speech_to_speech


def get_audio_download(audio_file):
    with open(audio_file, 'rb') as audio:
        return audio.read()


def translate_audio():
    audio_file = st.file_uploader(
        label="Select an audio file to transcribe and translate",
        type=["m4a", "wav", "mp3", "ogg"],
        accept_multiple_files=False)

    if audio_file:
        temp_dir = tempfile.mkdtemp()
        tmp_filepath = os.path.join(temp_dir, audio_file.name)
        with open(tmp_filepath, 'wb') as tmp_file:
            tmp_file.write(audio_file.read())

        a = time.time()
        translated_text, translated_audio = speech_to_speech(tmp_filepath)
        time_spent = time.time() - a

        st.subheader("Results")
        st.write(f"It took {time_spent}s to process your audio")

        st.download_button(
            label="Here's your translated audio",
            data=get_audio_download(translated_audio),
            file_name=translated_audio,
            # the produced audio is a wav file. this should be changed if the
            # audio mimetype changes
            mime="audio/wav",
            key="audio_download_btn"
        )
