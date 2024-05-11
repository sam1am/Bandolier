import os
from dotenv import load_dotenv
import time
import uuid
import io
import re
import json

import pygame
import pygame.mixer as mixer
import sounddevice as sd
import soundfile as sf
import numpy as np
import scipy.io.wavfile as wavfile
from threading import Thread

from .llm_api import process_query
from .tts_api import convert_to_speech
from .stt_api import convert_audio_to_text
from .database import log_interaction, get_last_messages

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

        # self.input_device = int(os.getenv("SOUND_INPUT_DEVICE", 22))
        self.input_device = None
        self.output_device = None
        
        self.typing_mode = False
        self.input_text = ""
        self.font = pygame.font.Font(None, 36)

        self.recording = False
        self.recorded_frames = []

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.typing_mode:
                        # Start recording
                        self.recording = True
                        self.recorded_frames = []
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
                        # Stop recording and process the query
                        self.recording = False
                        pygame.draw.circle(self.screen, self.thinking_color, (self.screen_width // 2, self.screen_height // 2), 100)
                        pygame.display.flip()
                        query_uuid = str(uuid.uuid4())
                        query_audio_file = f"./workspace/queries/{query_uuid}.wav"
                        recording = np.concatenate(self.recorded_frames, axis=0)
                        wavfile.write(query_audio_file, self.sample_rate, recording)
                        query_text = convert_audio_to_text(query_audio_file)
                        if query_text == "":
                            # query_text = "Howdy"
                            print("I didn't hear you.")
                            pass
                        self.process_query(query_text, query_audio_file, query_uuid)
                            
            # Draw the idle circle and text input box
            self.screen.fill(self.background_color)
            if self.recording:
                circle_color = self.listening_color
            else:
                circle_color = self.idle_color
            pygame.draw.circle(self.screen, circle_color, (self.screen_width // 2, self.screen_height // 2), 100)
            
            if self.typing_mode:
                input_surface = self.font.render(self.input_text, True, (0, 0, 0))
                input_rect = input_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(input_surface, input_rect)
            
            pygame.display.flip()

            # Record audio while the spacebar is held down
            if self.recording:
                frame = sd.rec(1024, samplerate=self.sample_rate, channels=self.channels, device=self.input_device)
                sd.wait()
                self.recorded_frames.append(frame)
    
    def process_query(self, query_text, query_audio_file="", query_uuid=None):
        start_time = time.time()
        if not query_uuid:
            query_uuid = str(uuid.uuid4())
        
        print(f"Query: {query_text}")

        # Retrieve the last X messages from the log
        num_messages = int(os.getenv("MESSAGE_HISTORY", 10))
        message_history = get_last_messages(num_messages)
        
        # Process the query using llm_api with message history
        pygame.draw.circle(self.screen, self.thinking_color, (self.screen_width // 2, self.screen_height // 2), 100)
        pygame.display.flip()
        inference_start_time = time.time()
        response_text = process_query(query_text, message_history)


        # Extract the JSON object from the response using regular expressions
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        response_json = None
        if json_match:
            json_string = json_match.group()
            try:
                response_json = json.loads(json_string)
                if "short_answer" in response_json:
                    short_answer = response_json["short_answer"]
                else:
                    print("'short_answer' key not found in the JSON response. Falling back to full answer!")
            except json.JSONDecodeError:
                print("Invalid JSON format. Falling back to full answer!")

        inference_time = time.time() - inference_start_time
        print(f"Inference ... {inference_time} seconds")
        
        # Convert the response to speech using tts_api
        pygame.draw.circle(self.screen, self.speaking_color, (self.screen_width // 2, self.screen_height // 2), 100)
        pygame.display.flip()
        tts_start_time = time.time()
        response_audio_file = f"./workspace/responses/{query_uuid}.wav"
        # concatenated_audio, sample_rate = convert_to_speech(response_text, query_uuid, self.speak_audio)
        # ifresponse_json exist and there is a short answer, use it, if not, use the fuill response text
        if response_json:
            # if short_answer key exists:
            if "short_answer" in response_json:
                concatenated_audio, sample_rate = convert_to_speech(response_json["short_answer"], query_uuid, self.speak_audio)
        else:
            concatenated_audio, sample_rate = convert_to_speech(response_text, query_uuid, self.speak_audio)
        sf.write(response_audio_file, concatenated_audio, sample_rate)
        tts_time = time.time() - tts_start_time
        print(f"TTS ... {tts_time} seconds")


        total_time = time.time() - start_time
        print(f"Turn completed in {total_time} seconds")

        # Log the interaction to the database
        log_interaction(query_uuid, query_audio_file, query_text, response_text, response_audio_file)


    def speak_audio(self, audio_data, sample_rate):
        # Create a BytesIO object from the audio data
        audio_bytes = io.BytesIO()
        sf.write(audio_bytes, audio_data, sample_rate, format='wav')
        audio_bytes.seek(0)

        # Load the audio data using Pygame mixer
        sound = mixer.Sound(audio_bytes)

        # Play the audio
        channel = sound.play()

        # Wait for the playback to finish
        while mixer.get_busy():
            pygame.time.delay(100)

