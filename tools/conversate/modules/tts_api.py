import gradio_client
import os
from dotenv import load_dotenv

load_dotenv()

tts_client = gradio_client.Client(os.getenv("TTS_API_URL"))

def convert_to_speech(text, query_uuid):
    tts_result = tts_client.predict(
        text,
        os.getenv("TTS_VOICE"),
        float(os.getenv("TTS_SPEED")),
        os.getenv("TTS_LANG"),
        api_name="/gen_voice"
    )
    
    # tts_result is expected to be a file path
    with open(tts_result, "rb") as f:
        audio_data = f.read()
    
    response_audio_file = f"./workspace/responses/{query_uuid}.wav"
    with open(response_audio_file, "wb") as f:
        f.write(audio_data)
    
    return response_audio_file