import streamlit as st
from web.translate_audio import translate_audio
from web.translate_video import translate_video

st.title("The Interpreter: An English-to-French Speech Translator")
st.write("Welcome to The Interpreter! Our demo showcases the power of " +
         "cutting-edge machine learning models to convert spoken words " +
         "from one language directly into another, ensuring seamless " +
         "communication across language barriers. It is powered by " +
         "state-of-the-art models ensuring high translation fidelity.")

st.subheader("Let's begin")

options = ["Translate video", "Translate audio ❌"]
selected_option = st.selectbox("Select an option:", options)

if selected_option == "Translate audio":
    translate_audio()
elif selected_option == "Translate video":
    translate_video()
