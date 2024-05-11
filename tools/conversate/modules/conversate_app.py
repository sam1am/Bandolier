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
            pygame.display.flip()