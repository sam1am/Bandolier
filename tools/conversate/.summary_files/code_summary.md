Output of tree command:
```
|-- README.md
|-- __pycache__
    |-- conversate_app.cpython-311.pyc
    |-- llm_api.cpython-311.pyc
    |-- tts_api.cpython-311.pyc
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
|-- requirements.txt
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

        self.input_device = 15
        

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

./requirements.txt
```
pygame 
openai 
sounddevice 
gradio_client 
numpy
git+https://github.com/m-bain/whisperx.git```
---

./llm_api.py
```
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def process_query(query):
    completion = client.chat.completions.create(
        model="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
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

./test.py
```
import sounddevice as sd                                                                                                                                            
    # Display all available devices and their information                             
print("Available audio devices and their configurations:")                        
print(sd.query_devices())                                                         
                                                                                    
# Attempt to print the default device's supported configurations                  
default_device_index = sd.default.device['input']                                 
default_device_info = sd.query_devices(default_device_index, 'input')             
print("Default input device info:")                                               
print(default_device_info)```
---

./tts_api.py
```
import gradio_client

tts_client = gradio_client.Client("http://localhost:7861/")

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

./docs/tts.md
```
API documentation
http://127.0.0.1:7860/
5 API endpoints

Use the gradio_client Python library or the @gradio/client Javascript package to query the demo via API.

copy
$ pip install gradio_client
Named Endpoints
api_name: /update_dropdown
copy
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
							api_name="/update_dropdown"
)
print(result)
Return Type(s)
# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]] representing output in 'Select Speaker' Dropdown component
api_name: /handle_recorded_audio
copy
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
		https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav,	# filepath  in 'Record Your Voice' Audio component
		Rogger,	# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]]  in 'Select Speaker' Dropdown component
		"Hello!!",	# str  in 'Add new Speaker' Textbox component
							api_name="/handle_recorded_audio"
)
print(result)
Return Type(s)
# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]] representing output in 'Select Speaker' Dropdown component
api_name: /handle_recorded_audio_1
copy
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
		https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav,	# filepath  in 'Record Your Voice' Audio component
		"Hello!!",	# str  in 'Add new Speaker' Textbox component
							api_name="/handle_recorded_audio_1"
)
print(result)
Return Type(s)
# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]] representing output in 'Select Speaker' Dropdown component
api_name: /handle_recorded_audio_2
copy
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
		https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav,	# filepath  in 'Record Your Voice' Audio component
		"Hello!!",	# str  in 'Add new Speaker' Textbox component
							api_name="/handle_recorded_audio_2"
)
print(result)
Return Type(s)
# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]] representing output in 'Select Speaker' Dropdown component
api_name: /gen_voice
copy
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
		"Hello!!",	# str  in 'Speechify this Text' Textbox component
		Rogger,	# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]]  in 'Select Speaker' Dropdown component
		0.1,	# float (numeric value between 0.1 and 1.99) in 'Speed' Slider component
		Arabic,	# Literal[Arabic, Chinese, Czech, Dutch, English, French, German, Hungarian, Italian, Japanese, Korean, Polish, Portuguese, Russian, Spanish, Turkish]  in 'Language/Accent' Dropdown component
							api_name="/gen_voice"
)
print(result)```
---

./docs/whisperx.md
```
WhisperX

GitHub stars GitHub issues GitHub license ArXiv paper Twitter

whisperx-arch

This repository provides fast automatic speech recognition (70x realtime with large-v2) with word-level timestamps and speaker diarization.

    ⚡️ Batched inference for 70x realtime transcription using whisper large-v2
    🪶 faster-whisper backend, requires <8GB gpu memory for large-v2 with beam_size=5
    🎯 Accurate word-level timestamps using wav2vec2 alignment
    👯‍♂️ Multispeaker ASR using speaker diarization from pyannote-audio (speaker ID labels)
    🗣️ VAD preprocessing, reduces hallucination & batching with no WER degradation

Whisper is an ASR model developed by OpenAI, trained on a large dataset of diverse audio. Whilst it does produces highly accurate transcriptions, the corresponding timestamps are at the utterance-level, not per word, and can be inaccurate by several seconds. OpenAI's whisper does not natively support batching.

Phoneme-Based ASR A suite of models finetuned to recognise the smallest unit of speech distinguishing one word from another, e.g. the element p in "tap". A popular example model is wav2vec2.0.

Forced Alignment refers to the process by which orthographic transcriptions are aligned to audio recordings to automatically generate phone level segmentation.

Voice Activity Detection (VAD) is the detection of the presence or absence of human speech.

Speaker Diarization is the process of partitioning an audio stream containing human speech into homogeneous segments according to the identity of each speaker.
New🚨

    1st place at Ego4d transcription challenge 🏆
    WhisperX accepted at INTERSPEECH 2023
    v3 transcript segment-per-sentence: using nltk sent_tokenize for better subtitlting & better diarization
    v3 released, 70x speed-up open-sourced. Using batched whisper with faster-whisper backend!
    v2 released, code cleanup, imports whisper library VAD filtering is now turned on by default, as in the paper.
    Paper drop🎓👨‍🏫! Please see our ArxiV preprint for benchmarking and details of WhisperX. We also introduce more efficient batch inference resulting in large-v2 with *60-70x REAL TIME speed.

Setup ⚙️
Tested for PyTorch 2.0, Python 3.10 (use other versions at your own risk!)

GPU execution requires the NVIDIA libraries cuBLAS 11.x and cuDNN 8.x to be installed on the system. Please refer to the CTranslate2 documentation.
1. Create Python3.10 environment

conda create --name whisperx python=3.10

conda activate whisperx
2. Install PyTorch, e.g. for Linux and Windows CUDA11.8:

conda install pytorch==2.0.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c pytorch -c nvidia

for non-nvidia (cpu only):
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

See other methods here.
3. Install this repo

pip install git+https://github.com/m-bain/whisperx.git

If already installed, update package to most recent commit

pip install git+https://github.com/m-bain/whisperx.git --upgrade

If wishing to modify this package, clone and install in editable mode:

$ git clone https://github.com/m-bain/whisperX.git
$ cd whisperX
$ pip install -e .

You may also need to install ffmpeg, rust etc. Follow openAI instructions here https://github.com/openai/whisper#setup.
Speaker Diarization

To enable Speaker Diarization, include your Hugging Face access token (read) that you can generate from Here after the --hf_token argument and accept the user agreement for the following models: Segmentation and Speaker-Diarization-3.1 (if you choose to use Speaker-Diarization 2.x, follow requirements here instead.)

    Note
    As of Oct 11, 2023, there is a known issue regarding slow performance with pyannote/Speaker-Diarization-3.0 in whisperX. It is due to dependency conflicts between faster-whisper and pyannote-audio 3.0.0. Please see this issue for more details and potential workarounds.

Usage 💬 (command line)
English

Run whisper on example segment (using default params, whisper small) add --highlight_words True to visualise word timings in the .srt file.

whisperx examples/sample01.wav

Result using WhisperX with forced alignment to wav2vec2.0 large:
sample01.mp4

Compare this to original whisper out the box, where many transcriptions are out of sync:
sample_whisper_og.mov

For increased timestamp accuracy, at the cost of higher gpu mem, use bigger models (bigger alignment model not found to be that helpful, see paper) e.g.

whisperx examples/sample01.wav --model large-v2 --align_model WAV2VEC2_ASR_LARGE_LV60K_960H --batch_size 4

To label the transcript with speaker ID's (set number of speakers if known e.g. --min_speakers 2 --max_speakers 2):

whisperx examples/sample01.wav --model large-v2 --diarize --highlight_words True

To run on CPU instead of GPU (and for running on Mac OS X):

whisperx examples/sample01.wav --compute_type int8

Other languages

The phoneme ASR alignment model is language-specific, for tested languages these models are automatically picked from torchaudio pipelines or huggingface. Just pass in the --language code, and use the whisper --model large.

Currently default models provided for {en, fr, de, es, it, ja, zh, nl, uk, pt}. If the detected language is not in this list, you need to find a phoneme-based ASR model from huggingface model hub and test it on your data.
E.g. German

whisperx --model large-v2 --language de examples/sample_de_01.wav

sample_de_01_vis.mov

See more examples in other languages here.
Python usage 🐍

import whisperx
import gc 

device = "cuda" 
audio_file = "audio.mp3"
batch_size = 16 # reduce if low on GPU mem
compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)

# 1. Transcribe with original whisper (batched)
model = whisperx.load_model("large-v2", device, compute_type=compute_type)

# save model to local path (optional)
# model_dir = "/path/"
# model = whisperx.load_model("large-v2", device, compute_type=compute_type, download_root=model_dir)

audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)
print(result["segments"]) # before alignment

# delete model if low on GPU resources
# import gc; gc.collect(); torch.cuda.empty_cache(); del model

# 2. Align whisper output
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

print(result["segments"]) # after alignment

# delete model if low on GPU resources
# import gc; gc.collect(); torch.cuda.empty_cache(); del model_a

# 3. Assign speaker labels
diarize_model = whisperx.DiarizationPipeline(use_auth_token=YOUR_HF_TOKEN, device=device)

# add min/max number of speakers if known
diarize_segments = diarize_model(audio)
# diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)

result = whisperx.assign_word_speakers(diarize_segments, result)
print(diarize_segments)
print(result["segments"]) # segments are now assigned speaker IDs

Demos 🚀

Replicate (large-v3 Replicate (large-v2 Replicate (medium)

If you don't have access to your own GPUs, use the links above to try out WhisperX.
Technical Details 👷‍♂️

For specific details on the batching and alignment, the effect of VAD, as well as the chosen alignment model, see the preprint paper.

To reduce GPU memory requirements, try any of the following (2. & 3. can affect quality):

    reduce batch size, e.g. --batch_size 4
    use a smaller ASR model --model base
    Use lighter compute type --compute_type int8

```
---

./docs/llm_api.md
```
# Example: reuse your existing OpenAI setup
from openai import OpenAI

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

completion = client.chat.completions.create(
  model="model-identifier",
  messages=[
    {"role": "system", "content": "Always answer in rhymes."},
    {"role": "user", "content": "Introduce yourself."}
  ],
  temperature=0.7,
)

print(completion.choices[0].message)```
---

./docs/spec.md
```
Conversate is an application that allows you to have a simple voice conversation with a locally running AI model. The flow is as follows: 

A simple user interface with a solid color background and a large circle of a complimtary color in the center. 
The color of the circle will indicate its status: orange for listening, purple for thinking, green for speaking, and blue for idle.
The spacebar will work like a PTT key: pressing it down will start the recording and releasing it will stop the recording. Recordings under 1 second will be discarded. 
The user's audio query will be converted to text using whisperx (see whisperx.md)
The query will be sent to a local language model api (see llm_api.md)
The response from the api will be spoken out loud using our tts api (see tts_api.md)
All interactions will be logged to a local sqlite database file called history

Ask any questions along the way.

Once everything is set up and ready to test, go ahead and start it up!

Create a readme file with an overview of the final project. ```
---
