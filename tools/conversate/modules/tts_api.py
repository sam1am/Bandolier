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
    
    # Create a queue to store the audio data
    audio_queue = Queue()
    
    # Create a separate thread for playback
    playback_thread = Thread(target=playback_audio, args=(audio_queue, speak_callback))
    playback_thread.start()
    
    # Create a list to store the thread objects
    threads = []
    
    # Process each sentence in a separate thread
    for sentence in sentences:
        thread = Thread(target=process_sentence, args=(sentence, query_uuid, audio_queue))
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Signal the end of processing
    audio_queue.put(None)
    
    # Wait for the playback thread to complete
    playback_thread.join()
    
    # Create a list to store the audio data
    audio_data_list = []
    
    # Retrieve the audio data from the queue
    while not audio_queue.empty():
        audio_data = audio_queue.get()
        if audio_data is not None:
            audio_data_list.append(audio_data[0])
    
    # Concatenate the audio data
    concatenated_audio = np.concatenate(audio_data_list)
    
    return concatenated_audio, audio_data_list[0][1]  # Return sample rate from the first audio data

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