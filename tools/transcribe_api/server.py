from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from pydub import AudioSegment
import os
import subprocess
import datetime
import glob
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import time
import shutil
import logging
from pydub.utils import mediainfo

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = generate_password_hash("236be17ac7b9c7b5865a7e582a29a7ff")

# Configure logging
logging.basicConfig(filename='transcription.log', level=logging.INFO,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(ROOT_DIR, 'static')

@app.route("/")
def home():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route("/transcribe", methods=["POST"])
def transcribe():
    # Get the uploaded file
    start_time = time.time()
    file = request.files["file"]
    print("Got file: ", file)
    end_time = time.time()
    processing_time = end_time - start_time
    print("File uploaded in: ", processing_time)
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # Create a unique directory
    base_dir = "k:\\qnoteworkspace\\"
    dir_name = os.path.join(base_dir, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

    os.makedirs(dir_name, exist_ok=True)
    print("Created directory: ", dir_name)

    # Save the file to the new directory with its original format
    original_file_path = os.path.join(dir_name, secure_filename(file.filename))      
    file.save(original_file_path)

    # After saving the original file
    audio_info = mediainfo(original_file_path)
    audio_length = audio_info["duration"]
    
    # Convert the audio file to wav, low bit rate
    print("Converting to wav...")
    converted_file_path = original_file_path.rsplit('.', 1)[0] + '.wav'
    audio = AudioSegment.from_file(original_file_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(converted_file_path, format='wav')
    print("converted to wav complete")

    # Get the absolute path of the file
    abs_file_path = os.path.abspath(converted_file_path)

    start_time = time.time()
    
    # Run the whisperx command
    print("Processing file: ", abs_file_path)
    hf_token = os.getenv("HF_TOKEN")
    cmd = f"python -m whisperx {abs_file_path} --diarize --device cuda --hf_token {hf_token} --language en"
    print("Running whisperx command: " + cmd)
    # debug process
    process = subprocess.Popen(
        cmd,
        shell=True,
        cwd=dir_name,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())
    returncode = process.poll()

    if returncode is not None:
        # Process finished
        stdout, stderr = process.communicate()
        if returncode != 0:
            # There was an error
            return jsonify({"error": stderr}), 500

    end_time = time.time()
    processing_time = end_time - start_time
    print("Transcription completed in: ", processing_time )

    # Find the .vtt file
    vtt_files = glob.glob(os.path.join(dir_name, "*.vtt"))
    print("Found .vtt files: ", vtt_files)
    if not vtt_files:
        return jsonify({"error": "No .vtt file found"}), 500

    # Read the .vtt file ignoring the first two lines and return its contents
    with open(vtt_files[0], "r") as f:
        lines = f.readlines()[2:]
        transcription = ''.join(lines)

    num_words = len(transcription.split())
    success = returncode == 0
    log_message = f"File: {file.filename}, , Processing Time: {processing_time} Audio Length: {audio_length}, " \
                  f"Words Transcribed: {num_words}, Success: {success}"
    logging.info(log_message)

    # Delete the working folder
    try:
        shutil.rmtree(dir_name)
        print(f"Deleted the working directory: {dir_name}")
    except Exception as e:
        print(f"Error while deleting directory {dir_name}: {e}")

    return jsonify({"transcription": transcription})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
