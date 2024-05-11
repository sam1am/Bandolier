import gradio_client
import os
from dotenv import load_dotenv
import librosa
import soundfile as sf
import io

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
    
    # Load the audio data using librosa
    data, sample_rate = librosa.load(io.BytesIO(audio_data))
    
    # Modify the playback speed
    speed_factor = float(os.getenv("TTS_SPEED", 0.5))
    
    # Time stretch the audio while preserving pitch
    stretched_data = librosa.effects.time_stretch(data, rate=1/speed_factor)
    
    # Save the stretched audio to the response file
    response_audio_file = f"./workspace/responses/{query_uuid}.wav"
    sf.write(response_audio_file, stretched_data, sample_rate)
    
    return response_audio_file