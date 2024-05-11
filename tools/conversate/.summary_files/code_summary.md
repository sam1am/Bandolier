Output of tree command:
```
|-- README.md
|-- __pycache__
|-- conversate_app.py
|-- database.py
|-- docs
    |-- llm_api.md
    |-- spec.md
    |-- tts.md
    |-- whisperx.md
|-- history.db
|-- llm_api.py
|-- main.py
|-- query.wav
|-- requirements.txt
|-- response.wav
|-- test.py
|-- tts_api.py
|-- whisperx_api.py

```

---

./conversate_app.py
```
import pygame
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from llm_api import process_query
from tts_api import convert_to_speech
from whisperx_api import convert_audio_to_text
from database import log_interaction

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
        self.sample_rate = 48000
        self.channels = 1
        self.duration = 5  # Recording duration in seconds

        self.input_device = 22
        

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
                        audio_file = "query.wav"
                        
                        recording = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate, channels=self.channels, device=self.input_device)
                        sd.wait()

                        # Save the recorded audio as a WAV file
                        wavfile.write(audio_file, self.sample_rate, recording)
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        # Convert audio to text using whisperx
                        pygame.draw.circle(self.screen, self.thinking_color, (self.screen_width // 2, self.screen_height // 2), 100)
                        pygame.display.flip()
                        query = convert_audio_to_text(audio_file)
                        if query == "":
                            query = "Howdy"
                        
                        # Process the query using llm_api
                        response_text = process_query(query)

                        # Extract the text content from the response
                        if isinstance(response_text, dict) and "content" in response_text:
                            response_content = response_text["content"]
                        else:
                            response_content = str(response_text)

                        # Convert the response to speech using tts_api
                        pygame.draw.circle(self.screen, self.speaking_color, (self.screen_width // 2, self.screen_height // 2), 100)
                        pygame.display.flip()
                        convert_to_speech(response_content)

                        # Log the interaction to the database
                        log_interaction(query, response_content)
            
            # Draw the idle circle
            self.screen.fill(self.background_color)
            pygame.draw.circle(self.screen, self.idle_color, (self.screen_width // 2, self.screen_height // 2), 100)
            pygame.display.flip()
```
---

./whisperx_api.py
```
import whisperx

def convert_audio_to_text(audio_file):
    model = whisperx.load_model("large-v2", "cpu", compute_type="int8")
    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, language="en", batch_size=16)
    text = ""
    for segment in result["segments"]:
        text += segment["text"]
    return text
```
---

./llm_api.py
```
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11323/v1", api_key="lm-studio")

def process_query(query):
    completion = client.chat.completions.create(
        # model="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF", #Q2 lol
        model="TheBloke/OpenHermes-2.5-Mistral-7B-16k-GGUF",
        messages=[
            {"role": "user", "content": query}
        ],
        temperature=0.7,
    )
    response_text = completion.choices[0].message
    return response_text
```
---

./main.py
```
import pygame
from conversate_app import ConversateApp

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
    main()
```
---

./database.py
```
import sqlite3

db_connection = sqlite3.connect("history.db")
db_cursor = db_connection.cursor()
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
db_connection.commit()

def log_interaction(query, response):
    db_cursor.execute("""
        INSERT INTO interactions (query, response)
        VALUES (?, ?)
    """, (query, response))
    db_connection.commit()

def close_connection():
    db_connection.close()
```
---

./tts_api.py
```
import gradio_client

tts_client = gradio_client.Client("http://localhost:7860/")

def convert_to_speech(text):
    tts_result = tts_client.predict(
        text,
        "Rogger",  # Selected speaker
        0.8,  # Speed
        "English",  # Language/Accent
        api_name="/gen_voice"
    )
    
    # tts_result is expected to be a file path
    with open(tts_result, "rb") as f:
        audio_data = f.read()
    
    with open("response.wav", "wb") as f:
        f.write(audio_data)
    # Implement logic to play the response audio
```
---
