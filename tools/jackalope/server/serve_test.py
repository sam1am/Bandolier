
from fastapi import FastAPI, HTTPException, Request
from pydub import AudioSegment
import base64
import os
import uuid
from typing import Any
import whisperx

app = FastAPI()

@app.post("/upload_voice_command")
async def upload_audio(request: Request):
    workspace_dir = './workspace'
    os.makedirs(workspace_dir, exist_ok=True)

    try:
        # Extract the base64 encoded audio from the request
        data = await request.json()
        audio_base64 = data['file']
        audio_bytes = base64.b64decode(audio_base64)

        # Handle the raw audio bytes
        audio_path = os.path.join(workspace_dir, f"{uuid.uuid4()}.wav")
        
        # Assuming the audio is 9-bit packed in 16-bit, let's go directly to 16-bit for broader compatibility
        audio_segment = AudioSegment(audio_bytes, sample_width=2, frame_rate=44100, channels=1)
        audio_segment.export(audio_path, format="wav")
        
        text = whisper_to_text(audio_path)
        return {"message": "Audio processed successfully", "filename": os.path.basename(audio_path), "text": text}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error processing the audio data")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error processing the audio data")

def whisper_to_text(audio_path: str) -> str:
    print("Converting audio to text")
    device = "cuda" 
    batch_size = 16 # reduce if low on GPU mem
    compute_type = "float16"
    model = whisperx.load_model("tiny", device, compute_type=compute_type)

    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=batch_size)
    print(result["segments"]) # before alignment

    return result["segments"]

