Output of tree command:
```
|-- README.md
|-- docs
    |-- llm_api.md
    |-- spec.md
    |-- tts.md
    |-- whisperx.md
|-- env_example
|-- main.py
|-- modules
    |-- __init__.py
    |-- __pycache__
    |-- conversate_app.py
    |-- database.py
    |-- llm_api.py
    |-- stt_api.py
    |-- tts_api.py
|-- requirements.txt
|-- test.py
|-- voices
    |-- brimley1.wav
    |-- max1.wav
|-- workspace

```

---

./main.py
```
import pygame
from modules.conversate_app import ConversateApp

def main():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Conversate")

    # Create an instance of ConversateApp
    app = ConversateApp(screen)

    # Run the application
    app.run()

    # Clean up
    pygame.quit()

if __name__ == "__main__":
    main()```
---

./modules/stt_api.py
```
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
    return text```
---

./modules/llm_api.py
```
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(base_url=os.getenv("LLM_API_URL"), api_key=os.getenv("LLM_API_KEY"))

def process_query(query):
    completion = client.chat.completions.create(
        model="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
        messages=[
            {"role": "system", "content": "You are a helpful assistant named Billy Bob."},
            {"role": "user", "content": query}
        ],
        temperature=0.7,
    )
    response_text = completion.choices[0].message
    
    # Extract the text content from the response
    if hasattr(response_text, "content"):
        response_content = response_text.content
    else:
        response_content = str(response_text)
    
    return response_content```
---

./modules/database.py
```
import sqlite3

db_connection = sqlite3.connect("history.db")
db_cursor = db_connection.cursor()
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        query_uuid TEXT,
        query_audio_file TEXT,
        query_text TEXT,
        response_text TEXT,
        response_audio_file TEXT
    )
""")
db_connection.commit()

def log_interaction(query_uuid, query_audio_file, query_text, response_text, response_audio_file):
    db_cursor.execute("""
        INSERT INTO interactions (query_uuid, query_audio_file, query_text, response_text, response_audio_file)
        VALUES (?, ?, ?, ?, ?)
    """, (query_uuid, query_audio_file, query_text, response_text, response_audio_file))
    db_connection.commit()

def close_connection():
    db_connection.close()```
---

./modules/conversate_app.py
```
import pygame
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from .llm_api import process_query
from .tts_api import convert_to_speech
from .stt_api import convert_audio_to_text
from .database import log_interaction
import os
from dotenv import load_dotenv
import soundfile as sf
import time
import uuid

load_dotenv()

class ConversateApp:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.background_color = (230, 230, 230)
        self.idle_color = (0, 0, 255)
        self.listening_color = (255, 165, 0)
        self.thinking_color = (128, 0, 128)
        self.speaking_color = (0, 255, 0)

        # Set up the audio recording parameters
        self.sample_rate = int(os.getenv("SAMPLE_RATE", 48000))
        self.channels = 1
        self.duration = 5  # Recording duration in seconds

        self.input_device = int(os.getenv("SOUND_INPUT_DEVICE", 22))
        # set to default device
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Start recording
                        pygame.draw.circle(self.screen, self.listening_color, (self.screen_width // 2, self.screen_height // 2), 100)
                        pygame.display.flip()
                        query_uuid = str(uuid.uuid4())
                        query_audio_file = f"./workspace/queries/{query_uuid}.wav"
                        
                        recording = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate, channels=self.channels, device=self.input_device)
                        sd.wait()

                        # Save the recorded audio as a WAV file
                        wavfile.write(query_audio_file, self.sample_rate, recording)
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        start_time = time.time()

                        # Convert audio to text using stt_api
                        pygame.draw.circle(self.screen, self.thinking_color, (self.screen_width // 2, self.screen_height // 2), 100)
                        pygame.display.flip()
                        stt_start_time = time.time()
                        query_text = convert_audio_to_text(query_audio_file)
                        stt_time = time.time() - stt_start_time
                        print(f"STT ... {stt_time} seconds")
                        if query_text == "":
                            query_text = "Howdy"
                        
                        print(f"Query: {query_text}")

                        # Process the query using llm_api
                        inference_start_time = time.time()
                        response_text = process_query(query_text)
                        inference_time = time.time() - inference_start_time
                        print(f"Inference ... {inference_time} seconds")
                        
                        # Convert the response to speech using tts_api
                        pygame.draw.circle(self.screen, self.speaking_color, (self.screen_width // 2, self.screen_height // 2), 100)
                        pygame.display.flip()
                        tts_start_time = time.time()
                        response_audio_file = convert_to_speech(response_text, query_uuid)
                        tts_time = time.time() - tts_start_time
                        print(f"TTS ... {tts_time} seconds")

                        total_time = time.time() - start_time
                        print(f"Turn completed in {total_time} seconds")

                        # Play the audio file using sounddevice
                        data, sample_rate = sf.read(response_audio_file)
                        sd.play(data, sample_rate, device=self.input_device)
                        sd.wait()

                        # Log the interaction to the database
                        log_interaction(query_uuid, query_audio_file, query_text, response_text, response_audio_file)
            
            # Draw the idle circle
            self.screen.fill(self.background_color)
            pygame.draw.circle(self.screen, self.idle_color, (self.screen_width // 2, self.screen_height // 2), 100)
            pygame.display.flip()```
---

./modules/tts_api.py
```
import gradio_client
import os
from dotenv import load_dotenv

load_dotenv()

tts_client = gradio_client.Client(os.getenv("TTS_API_URL"))

def convert_to_speech(text, query_uuid):
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
    
    response_audio_file = f"./workspace/responses/{query_uuid}.wav"
    with open(response_audio_file, "wb") as f:
        f.write(audio_data)
    
    return response_audio_file```
---
