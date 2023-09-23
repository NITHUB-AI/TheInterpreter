from helper import convert_audio, transcribe, seamless_t2st

def speech_to_speech(file_path):
    print("Start...")
    target_sr = 16000
    print(f"Resampling file to {target_sr}...")
    converted_file_path, sampling_rate = convert_audio(file_path, target_sr)
    print("Transcribing audio file...")
    en_text = transcribe(converted_file_path)
    file_name = file_path.split('/')[-1][:-4]
    print("translating text and generating speech...")
    translated_text, translated_audio = seamless_t2st(en_text, f"fr_{file_name}.wav", sampling_rate)
    print(f"Resampling file to {sampling_rate}...")
    translated_audio, _ = convert_audio(translated_audio, target_sr=sampling_rate)
    print("End.")
    return translated_text, translated_audio

if __name__ == "__main__":
    translated_text, translated_audio = speech_to_speech("data/trial_eng.m4a")
    print(translated_text)
    print(translated_audio)