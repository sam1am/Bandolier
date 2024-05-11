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

        self.input_device = int(os.getenv("SOUND_DEVICE", 22))
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
                        
                        print(f"Query: {query}")

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
