import os
import shutil
import time
import subprocess
import glob
import logging
from unsilence import Unsilence
from dotenv import load_dotenv
import json
import platform
import tempfile
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

load_dotenv()

WORKING_DIR = os.path.join(os.getcwd(), "workspace")
VAULT_DIR = '/Users/johngarfield/Library/Mobile Documents/iCloud~md~obsidian/Documents/OBSIDIAN/Transcriptions'

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

config = load_config()
folder_list = config.get('folder_list', [])
print("Loaded config: ", config)
VAULT_DIR = config.get('vault_dir', VAULT_DIR)

root = tk.Tk()

text_box = tk.Text(root, width=50, height=10)
folder_listbox = tk.Listbox(root, width=50, height=10)

# populate the listbox with the saved folders
for folder in folder_list:
    folder_listbox.insert(tk.END, folder)
    # folder_list.insert(tk.END, folder)


def detect_platform():
    if platform.system() == 'Darwin':
        return 'int8'
    else:
        return 'float16'

def copy_files(src_path, dst_path):
    files = os.listdir(src_path)
    for file in files:
        if file.endswith('.wav'):
            shutil.copy(os.path.join(src_path, file), dst_path)

def transcribe_audio(file_path, dir_name, compute_type):
    abs_file_path = os.path.abspath(file_path)
    start_time = time.time()
    print("Processing file: ", abs_file_path)
    hf_token = os.getenv("HF_TOKEN")
    cmd = f"whisperx '{abs_file_path}' --diarize --hf_token {hf_token} --compute_type {compute_type} --language en"
    
    process = subprocess.Popen(
        cmd,
        shell=True,
        cwd=dir_name,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Whisperx command failed with exit code {process.returncode}")
        print(f"Standard error output:\n{stderr}")
        return json.dumps({"error": stderr}), 500
    else:
        print(stdout)
    end_time = time.time()
    processing_time = end_time - start_time
    print("Transcription completed in: ", processing_time )
    vtt_files = glob.glob(os.path.join(dir_name, "*.vtt"))
    print("Found .vtt files: ", vtt_files)
    if not vtt_files:
        return json.dumps({"error": "No .vtt files found"}), 500
    with open(vtt_files[0], "r") as f:
        lines = f.readlines()[2:]
        transcription = ''.join(lines)

    shutil.rmtree(dir_name)
    return transcription

def clear_data(src_path):
    files = os.listdir(src_path)
    for file in files:
        if file.endswith('.wav') and not file.startswith('._'):
            os.remove(os.path.join(src_path, file))


def save_to_obsidian_vault(transcription, file_name):
    with open(os.path.join(VAULT_DIR, file_name + '.md'), 'w') as f:
        f.write(f"# Transcription of {file_name}\n\n{transcription}")



def add_folder():
    folder = filedialog.askdirectory()
    folder_list.append(folder)
    folder_listbox.insert(tk.END, folder)
    save_config({'folder_list': folder_list, 'vault_dir': VAULT_DIR})

def set_vault():
    global VAULT_DIR
    VAULT_DIR = filedialog.askdirectory()
    save_config({'folder_list': folder_list, 'vault_dir': VAULT_DIR})


def start_processing():
    text_box.insert(tk.END, "Starting Process...")
    compute_type = detect_platform()
    for folder in folder_list:
        if os.path.exists(folder):
            copy_files(folder, WORKING_DIR)
            for file in os.listdir(WORKING_DIR):
                if file.endswith('.wav'):  # make sure we only process .wav files
                    file_path = os.path.join(WORKING_DIR, file)
                    with tempfile.TemporaryDirectory() as temp_dir:
                        transcription = transcribe_audio(file_path, temp_dir, compute_type)
                    clear_data(folder)
                    file_name = os.path.splitext(file)[0]
                    save_to_obsidian_vault(transcription, file_name)
                    text_box.insert(tk.END, f"Processed {file_name} and saved transcription to Obsidian vault.")
        else:
            text_box.insert(tk.END, f"Folder {folder} not found.")
    text_box.insert(tk.END, "Finished Processing.")

add_button = tk.Button(root, text="Add Folder", command=add_folder)
set_button = tk.Button(root, text="Set Vault", command=set_vault)
start_button = tk.Button(root, text="Start", command=start_processing)

add_button.pack()
set_button.pack()
start_button.pack()
folder_listbox.pack()
text_box.pack()

root.mainloop()
