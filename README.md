# The Interpreter: An English-to-French Speech Translator

## 🌍 Overview

Welcome to **The Interpreter**! Our demo showcases the power of cutting-edge machine learning models to convert spoken words from one language directly into another, ensuring seamless communication across language barriers. It is powered by state-of-the-art models ensuring high translation fidelity.
  

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- FFmpeg for audio processing

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
4. Add your [OpenAI](https://platform.openai.com/) and [Huggingface](https://huggingface.co/) API Keys to a `.env` file in the project directory in the form:
   ```
   OPENAI_API_KEY=<YOUR_API_KEY>
   HF_API_KEY=<YOUR_API_KEY>
   ```

### Usage

Run the application to interprete an audio file:
   ```sh
   python interpreter.py audio_path.m4a
   ```

## 🛠️ Technologies Used
  
- **OpenAI's Whisper**: As the backbone for audio transcription.
  
- **Facebooks SeamlessM4T**: For translation and speech generation.