import gradio_client
import os
from dotenv import load_dotenv

load_dotenv()

tts_client = gradio_client.Client(os.getenv("TTS_API_URL"))

def convert_to_speech(text):
    tts_result = tts_client.predict(
        text,
        os.getenv("TTS_VOICE"),
        0.8,  # Speed
        os.getenv("TTS_LANG"),
        api_name="/gen_voice"
    )
    
    # tts_result is expected to be a file path
    with open(tts_result, "rb") as f:
        audio_data = f.read()
    
    with open("./workspace/response.wav", "wb") as f:
        f.write(audio_data)
    # Implement logic to play the response audio
