# The Interpreter: An English-to-French Speech Translator

## 🌍 Overview

Welcome to **The Interpreter**! Our demo showcases the power of cutting-edge machine learning models to convert spoken words from one language directly into another, ensuring seamless communication across language barriers. It is powered by state-of-the-art models ensuring high translation fidelity.
  

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- FFmpeg for audio processing

### MODES

The Interpreter can be run in 3 possible modes which are `2STEP`, `API_2STEP` and `3STEP`.

1. `2STEP`: In this mode, you download all models used on initialization and load them locally. You also perform the speech to speech translation in 2 steps, first you transcribe the input speech into text and in the second step, you translate and transcribe the text into the output speech.

2. `API_2STEP`: In this mode, you use all models via API calls. It uses the same models in the `2STEP` mode and is considerably faster than it since the models are already loaded. It also requires less RAM on startup. However, exposing the interpreter via an API endpoint in `2STEP` mode could take away the speed advantage in deployment.

3. `3STEP`: In this mode, you break down the speech to speech translation into 3 steps. First, you transcribe the input speech, then you translate the text and finally, you synthesize the output speech. The models for the first 2 steps are loaded via APIs to reduce latency and RAM consumption in loading and initializing them. The model for the third step is however loaded and initialized locally since it requires minimal RAM and is relatively fast.

### Installation

1. Clone the repo:
   ```sh
   git clone https://github.com/NITHUB-AI/TheInterpreter.git
   ```

2. Navigate to the project directory:
   ```sh
   cd TheInterpreter
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Add the `MODE` you wish to use, your [OpenAI](https://platform.openai.com/) and [Huggingface](https://huggingface.co/) API Keys to a `.env` file in the project directory in the form below.:
   ```
   OPENAI_API_KEY=<YOUR_API_KEY>
   HF_API_KEY=<YOUR_API_KEY>
   MODE=3STEP
   STREAM_KEY=<YOUTUBE_STREAM_KEY>
   ```

### Usage

Run the application to interprete an audio file:
   ```sh
   python interpreter.py audio_path.m4a
   ```

Run the streamlit web app:
```sh
streamlit run webapp.py
```

## 🛠️ Technologies Used
  
- **OpenAI's Whisper**: As the backbone for audio translation.
  
- **Facebooks SeamlessM4T**: For translation and speech generation.