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

tts_client = gradio_client.Client(os.getenv("TTS_API_URL"))
nltk.download('punkt')

def convert_to_speech(text, query_uuid, speak_callback):
    # Split the text into sentences
    sentences = nltk.sent_tokenize(text)
    
    # Create queues for audio playback and concatenation
    audio_queue = Queue()
    concatenation_queue = Queue()
    
    # Create a separate thread for audio generation
    generation_thread = Thread(target=generate_audio, args=(sentences, query_uuid, audio_queue, concatenation_queue))
    generation_thread.start()
    
    # Create a separate thread for audio playback
    playback_thread = Thread(target=playback_audio, args=(audio_queue, speak_callback))
    playback_thread.start()
    
    # Wait for the audio generation thread to complete
    generation_thread.join()
    
    # Signal the end of processing to the playback thread
    audio_queue.put(None)
    
    # Wait for the playback thread to complete
    playback_thread.join()
    
    # Retrieve the audio data from the concatenation queue
    audio_data_list = []
    sample_rate = None
    while not concatenation_queue.empty():
        audio_data = concatenation_queue.get()
        if audio_data is not None:
            audio_data_list.append(audio_data[0])
            if sample_rate is None:
                sample_rate = audio_data[1]
    
    # Check if any audio data was generated
    if len(audio_data_list) > 0:
        # Concatenate the audio data
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
        
        # tts_result is expected to be a file path
        with open(tts_result, "rb") as f:
            audio_data = f.read()
        
        # Load the audio data using librosa
        data, sample_rate = librosa.load(io.BytesIO(audio_data), sr=None)
        
        # Modify the playback speed
        speed_factor = float(os.getenv("TTS_SPEED", 0.5))
        
        # Time stretch the audio while preserving pitch
        stretched_data = librosa.effects.time_stretch(data, rate=1/speed_factor)
        
        # Add the stretched audio data to both queues
        audio_queue.put((stretched_data, sample_rate))
        concatenation_queue.put((stretched_data, sample_rate))
    
    # Signal the end of processing to both queues
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
    
    # tts_result is expected to be a file path
    with open(tts_result, "rb") as f:
        audio_data = f.read()
    
    # Load the audio data using librosa
    data, sample_rate = librosa.load(io.BytesIO(audio_data))
    
    # Modify the playback speed
    speed_factor = float(os.getenv("TTS_SPEED", 0.5))
    
    # Time stretch the audio while preserving pitch
    stretched_data = librosa.effects.time_stretch(data, rate=1/speed_factor)
    
    # Add the stretched audio data to the queue
    audio_queue.put((stretched_data, sample_rate))

def playback_audio(audio_queue, speak_callback):
    while True:
        audio_data = audio_queue.get()
        if audio_data is None:
            break
        stretched_data, sample_rate = audio_data
        speak_callback(stretched_data, sample_rate)