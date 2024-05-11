import whisperx
import pyautogui
import json
import datetime
from openai import OpenAI
from pynput import keyboard
import sounddevice as sd
from scipy.io.wavfile import write
import os
import time
import numpy as np

# Configure OpenAI client
client = OpenAI(
    base_url="https://api.nuzu.ai/v1",
    api_key="lookatmeimanapikey",
)

# Configure JSON schema for the language model response
json_schema = {
    "type": "object",
    "properties": {
        "thought": {"type": "string"},
        "commands": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "value": {"type": "string"}
                },
                "required": ["action", "value"]
            }
        }
    },
    "required": ["thought", "commands"]
}

# Configure recording settings
sample_rate = 44100

# Initialize variables
recording = False
audio_data = []
input_mode = 'voice'  # Default input mode is voice

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header():
    clear_screen()
    print("=" * 40)
    print("       AI Keyboard Assistant")
    print("=" * 40)
    print("Input Mode: ", end="")
    if input_mode == 'voice':
        print("Voice")
    else:
        print("Text")
    print("=" * 40)

def display_instructions():
    print("Instructions:")
    print("1. Press and hold the Command key to start recording.")
    print("2. Release the Command key to stop recording and process the audio.")
    print("3. Press 'Alt' to switch between voice and text entry modes.")
    print("4. Press 'Ctrl+C' to exit the program.")
    print("=" * 40)

def start_recording():
    global recording, audio_data
    recording = True
    audio_data = []
    print("Recording started...")

def stop_recording():
    global recording
    recording = False
    print("Recording stopped.")

    # Save the recorded audio as a WAV file
    audio_file = "recorded_audio.wav"
    write(audio_file, sample_rate, np.array(audio_data))

    # Transcribe the recorded audio using whisperx
    transcribe_audio(audio_file)

def transcribe_audio(audio_file):
    print("Transcribing audio...")
    device = "cuda"
    batch_size = 16
    compute_type = "float16"

    model = whisperx.load_model("large-v2", device, compute_type=compute_type)
    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)

    # Extract the transcribed text
    transcribed_text = result["text"]

    # Query the language model with instructions
    query_language_model(transcribed_text)

def query_language_model(input_text):
    print("Querying language model...")
    system_prompt = """You are an AI keyboard assistant. You take aribtrary text or commands and translate them into a list of keyboard actions. If you receive arbitrary text, return it as the formatted text to be typed, correcting any spelling errors. If you receive commands, respond with the keystrokes or keypresses as instructed.
    Respond only with a JSON object containing the following fields and nothing else:
    - thought: A brief thought or explanation of your response.
    - commands: An array of objects, each representing a keyboard command. Each object should have the following fields:
      - action: The type of action to perform (e.g., "type", "press", "hotkey").
      - value: The value associated with the action (e.g., the text to type, the key to press, or the comma-separated list of keys for a hotkey combination).

    Examples:
    - Query is "Hello, world!". For typing text use: {"action": "type", "value": "Hello, world!"}
    - Query is "Enter". For pressing a single key: {"action": "press", "value": "enter"}
    - Query is "command space". For pressing a key combination: {"action": "hotkey", "value": "command,space"}

    Note: For key combinations, provide the keys as a comma-separated list in the "value" field. Key names should correspond to pyautogui key names.
    """

    completion = client.chat.completions.create(
        model="casperhansen/llama-3-8b-instruct-awq",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ],
        extra_body={
            "stop_token_ids": [128009],
            "response_format": {"type": "json_object"},
            "guided_json": json_schema
        }
    )

    # Extract the JSON response from the language model
    json_response = completion.choices[0].message.content.strip()
    response_data = json.loads(json_response)

    # print the response data out
    print(json_response)

   

    # Execute the keyboard commands
    execute_commands(response_data["commands"])
    #hit enter to continue
    # input("Press Enter to continue...")

    # Log the interaction and results
    log_interaction(input_text, json_response, response_data["commands"])
     

def execute_commands(commands):
    print("Executing commands...")
    for command in commands:
        action = command.get("action")
        value = command.get("value")

        if action == "type":
            if value:
                pyautogui.typewrite(value)
            else:
                print("Invalid value for 'type' action.")
        elif action == "press":
            if value:
                pyautogui.press(value)
            else:
                print("Invalid value for 'press' action.")
        elif action == "hotkey":
            if value:
                keys = value.split(",")
                if len(keys) == 1:
                    pyautogui.press(keys[0])
                elif len(keys) == 2:
                    pyautogui.keyDown(keys[0])
                    pyautogui.press(keys[1])
                    pyautogui.keyUp(keys[0])
                else:
                    print("Invalid number of keys for 'hotkey' action.")
            else:
                print("Invalid value for 'hotkey' action.")
        else:
            print(f"Invalid action: {action}")
        time.sleep(0.5)

    print("Commands executed successfully.")


def log_interaction(input_text, json_response, commands):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Input Text: {input_text}\n"
    log_entry += f"{timestamp} - Language Model Response: {json_response}\n"
    log_entry += f"{timestamp} - Executed Commands: {commands}\n\n"

    with open("interaction_log.txt", "a") as log_file:
        log_file.write(log_entry)

def switch_input_mode():
    global input_mode
    if input_mode == 'voice':
        input_mode = 'text'
        print("Switched to text entry mode.")
    else:
        input_mode = 'voice'
        print("Switched to voice entry mode.")

    display_header()
    display_instructions()

def on_press(key):
    global recording
    # if key == keyboard.Key.cmd:  # Change this to the desired PTT key
    #     start_recording()

def on_release(key):
    global recording
    # if key == keyboard.Key.cmd:  # Change this to the desired PTT key
    #     stop_recording()
    if key == keyboard.Key.alt:
        switch_input_mode()

def main():
    global audio_data

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    display_header()
    display_instructions()

    while True:
        if recording:
            audio_chunk = sd.rec(int(sample_rate * 0.1), channels=1, dtype='int16')
            sd.wait()
            audio_data.extend(audio_chunk)

        if input_mode == 'text':
            input_text = input("Enter your command: ")
            query_language_model(input_text)
            time.sleep(1)
            display_header()
            display_instructions()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting the program.")