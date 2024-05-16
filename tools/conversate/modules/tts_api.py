import gradio_client
import os
from dotenv import load_dotenv
import librosa
import soundfile as sf
import io
import nltk
from queue import Queue
from threading import Thread
import numpy as np
import nltk

load_dotenv()

nltk.download('punkt')

# Global flag to indicate TTS availability
tts_available = True

try: 
    tts_client = gradio_client.Client(os.getenv("TTS_API_URL"))
except Exception as e:
    print(f"Error connecting to TTS API. Make sure xtts2_ui is running: {e}")
    tts_available = False

def convert_to_speech(text, query_uuid, speak_callback):
    if not tts_available:
        print("TTS is unavailable. Skipping TTS conversion.")
        return None, None
    sentences = nltk.sent_tokenize(text)
    audio_queue = Queue()
    concatenation_queue = Queue()
    generation_thread = Thread(target=generate_audio, args=(sentences, query_uuid, audio_queue, concatenation_queue))
    generation_thread.start()
    playback_thread = Thread(target=playback_audio, args=(audio_queue, speak_callback))
    playback_thread.start()

    generation_thread.join()
    audio_queue.put(None)
    playback_thread.join()
    audio_data_list = []
    sample_rate = None
    while not concatenation_queue.empty():
        audio_data = concatenation_queue.get()
        if audio_data is not None:
            audio_data_list.append(audio_data[0])
            if sample_rate is None:
                sample_rate = audio_data[1]
    if len(audio_data_list) > 0:
        concatenated_audio = np.concatenate(audio_data_list)
        # Ensure the concatenated audio has the correct shape
        if concatenated_audio.ndim == 1:
            concatenated_audio = concatenated_audio.reshape(-1, 1)
        return concatenated_audio, sample_rate
    else:
        return None, None

def generate_audio(sentences, query_uuid, audio_queue, concatenation_queue):
    for sentence in sentences:
        tts_result = tts_client.predict(
            sentence,
            os.getenv("TTS_VOICE"),
            float(os.getenv("TTS_SPEED")),
            os.getenv("TTS_LANG"),
            api_name="/gen_voice"
        )
        
        with open(tts_result, "rb") as f:
            audio_data = f.read()
        data, sample_rate = librosa.load(io.BytesIO(audio_data), sr=None)
        speed_factor = float(os.getenv("TTS_SPEED", 0.5))
        stretched_data = librosa.effects.time_stretch(data, rate=1/speed_factor)
        audio_queue.put((stretched_data, sample_rate))
        concatenation_queue.put((stretched_data, sample_rate))
    
    audio_queue.put(None)
    concatenation_queue.put(None)

def playback_audio(audio_queue, speak_callback):
    while True:
        audio_data = audio_queue.get()
        if audio_data is None:
            break
        stretched_data, sample_rate = audio_data
        speak_callback(stretched_data, sample_rate)

def process_sentence(sentence, query_uuid, audio_queue):
    tts_result = tts_client.predict(
        sentence,
        os.getenv("TTS_VOICE"),
        float(os.getenv("TTS_SPEED")),
        os.getenv("TTS_LANG"),
        api_name="/gen_voice"
    )
    
    with open(tts_result, "rb") as f:
        audio_data = f.read()
    data, sample_rate = librosa.load(io.BytesIO(audio_data))
    speed_factor = float(os.getenv("TTS_SPEED", 0.5))
    stretched_data = librosa.effects.time_stretch(data, rate=1/speed_factor)
    audio_queue.put((stretched_data, sample_rate))

def playback_audio(audio_queue, speak_callback):
    while True:
        audio_data = audio_queue.get()
        if audio_data is None:
            break
        stretched_data, sample_rate = audio_data
        speak_callback(stretched_data, sample_rate)