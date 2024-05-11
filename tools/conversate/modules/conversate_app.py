import pygame
import pygame.mixer as mixer
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from .llm_api import process_query
from .tts_api import convert_to_speech
from .stt_api import convert_audio_to_text
from .database import log_interaction, get_last_messages
import os
from dotenv import load_dotenv
import soundfile as sf
import time
import uuid

load_dotenv()

mixer.init()

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

        # self.input_device = int(os.getenv("SOUND_INPUT_DEVICE", 22))
        self.input_device = None
        self.output_device = None
        
        self.typing_mode = False
        self.input_text = ""
        self.font = pygame.font.Font(None, 36)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.typing_mode:
                        # Start recording
                        pygame.draw.circle(self.screen, self.listening_color, (self.screen_width // 2, self.screen_height // 2), 100)
                        pygame.display.flip()
                        query_uuid = str(uuid.uuid4())
                        query_audio_file = f"./workspace/queries/{query_uuid}.wav"
                        
                        recording = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate, channels=self.channels, device=self.input_device)
                        sd.wait()

                        # Save the recorded audio as a WAV file
                        wavfile.write(query_audio_file, self.sample_rate, recording)
                    elif event.key == pygame.K_RETURN:
                        if not self.typing_mode:
                            self.typing_mode = True
                            self.input_text = ""
                        else:
                            self.typing_mode = False
                            query_text = self.input_text.strip()
                            if query_text:
                                self.process_query(query_text)
                    elif self.typing_mode:
                        if event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            self.input_text += event.unicode
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE and not self.typing_mode:
                        query_text = convert_audio_to_text(query_audio_file)
                        if query_text == "":
                            query_text = "Howdy"
                        self.process_query(query_text, query_audio_file, query_uuid)
            
            # Draw the idle circle and text input box
            self.screen.fill(self.background_color)
            pygame.draw.circle(self.screen, self.idle_color, (self.screen_width // 2, self.screen_height // 2), 100)
            
            if self.typing_mode:
                input_surface = self.font.render(self.input_text, True, (0, 0, 0))
                input_rect = input_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(input_surface, input_rect)
            
            pygame.display.flip()
    
    def process_query(self, query_text, query_audio_file="", query_uuid=None):
        start_time = time.time()
        if not query_uuid:
            query_uuid = str(uuid.uuid4())
        
        print(f"Query: {query_text}")

        # Retrieve the last X messages from the log
        num_messages = int(os.getenv("MESSAGE_HISTORY", 5))
        message_history = get_last_messages(num_messages)
        
        # Process the query using llm_api with message history
        pygame.draw.circle(self.screen, self.thinking_color, (self.screen_width // 2, self.screen_height // 2), 100)
        pygame.display.flip()
        inference_start_time = time.time()
        response_text = process_query(query_text, message_history)
        inference_time = time.time() - inference_start_time
        print(f"Response: {response_text}")
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
        # sd.default.latency = 'low'  # Adjust latency if needed
        # sd.default.blocksize = 4096  # Adjust block size if needed
        sound = mixer.Sound(response_audio_file)
        sound.play()

        # Wait for the audio to finish  
        while mixer.get_busy():
            pygame.time.delay(100)

        # sd.play(data, sample_rate, device=self.input_device)
        # sd.wait()

        # Log the interaction to the database
        log_interaction(query_uuid, query_audio_file, query_text, response_text, response_audio_file)