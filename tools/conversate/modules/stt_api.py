import whisperx
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

def convert_audio_to_text(audio_file):
    model = whisperx.load_model(os.getenv("STT_MODEL"), os.getenv("STT_DEVICE"), compute_type=os.getenv("STT_COMPUTE_TYPE"))

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, language="en", batch_size=16)
    text = ""
    for segment in result["segments"]:
        text += segment["text"]
    return text