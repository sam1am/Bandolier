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
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk

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

def detect_platform():
    if platform.system() == 'Darwin':
        return 'int8'
    else:
        return 'float16'

config = load_config()
folder_list = config.get('folder_list', [])
print("Loaded config: ", config)
VAULT_DIR = config.get('vault_dir', VAULT_DIR)

compute_type = detect_platform()

root = tk.Tk()
root.title("Awesome Transcriber")
root.geometry("600x400")

style = ttk.Style()
style.theme_use('clam')  # A theme that can be styled to be somewhat similar to Material Design

style.configure('TButton', font=('Helvetica', 10), background='lightgrey')
style.configure('TLabel', font=('Helvetica', 12), background='white')
style.configure('TFrame', background='white')

frame1 = ttk.Frame(root)
frame1.pack(fill='x')

frame2 = ttk.Frame(root)
frame2.pack(fill='x')

frame3 = ttk.Frame(root)
frame3.pack(fill='both', expand=True)

frame4 = ttk.Frame(root)
frame4.pack(fill='x')

vault_label = ttk.Label(frame1, text="Vault: " + VAULT_DIR)
compute_type_label = ttk.Label(frame1, text="Compute Type: " + compute_type)  # New label to display compute type
folder_listbox = tk.Listbox(frame2, width=50, height=10)
vault_label.pack(side='left')
compute_type_label.pack(side='left')  # Pack the new label

for folder in folder_list:
    folder_listbox.insert(tk.END, folder)

text_box = tk.Text(frame3)
text_box.configure(state='disabled') # Make the text box uneditable


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
    vault_label.config(text="Vault: "+VAULT_DIR)


def start_processing():
    text_box.insert(tk.END, "Starting Process...")
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

add_button = ttk.Button(frame4, text="Add Folder", command=add_folder)
set_button = ttk.Button(frame4, text="Set Vault", command=set_vault)
start_button = ttk.Button(frame4, text="Start", command=start_processing)

vault_label.pack(side='left')
folder_listbox.pack(fill='both', expand=True)
text_box.pack(fill='both', expand=True)
add_button.pack(side='left')
set_button.pack(side='left')
start_button.pack(side='left')

root.mainloop()
