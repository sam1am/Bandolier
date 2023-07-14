import os
import shutil
import time
import subprocess
import glob
import platform
import tempfile
from config_handler import ConfigHandler
from datetime import datetime
import tkinter as tk
import json
import dotenv

class AudioProcessor:
    def __init__(self, config_handler: ConfigHandler):
        self.config_handler = config_handler
        self.working_dir = config_handler.create_directory("workspace")
        # Load vault_dir from config_handler
        self.vault_dir = self.config_handler.config.get('vault_dir', self.config_handler.create_directory("vault"))
        self.compute_type = self.detect_platform()
    
    def detect_platform(self):
        return 'int8' if platform.system() == 'Darwin' else 'float16'

    def copy_files(self, src_path, dst_path):
        src_path = os.path.normpath(src_path)
        dst_path = os.path.normpath(dst_path)
        files = os.listdir(src_path)
        for file in files:
            if file.lower().endswith('.wav'): 
                shutil.copy(os.path.join(src_path, file), dst_path)
                print("Copied file: ", file)

    def transcribe_audio(self, file_path, dir_name):
        abs_file_path = os.path.abspath(file_path)
        start_time = time.time()
        dotenv.load_dotenv()
        hf_token = os.getenv('HF_TOKEN')

        if platform.system() == 'Windows':
            cmd = f"whisperx \"{abs_file_path}\" --diarize --hf_token {hf_token} --compute_type {self.compute_type} --language en"
        else:
            cmd = f"whisperx '{abs_file_path}' --diarize --hf_token {hf_token} --compute_type {self.compute_type} --language en"

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
        print("Deleted temp directory: ", dir_name)
        return transcription

    def clear_data(self, src_path):
        files = os.listdir(src_path)
        for file in files:
            if file.endswith('.wav') and not file.startswith('._'):
                # os.remove(os.path.join(src_path, file))
                print("Deleting wav file jk: ", file)

    def save_to_obsidian_vault(self, transcription, file_name):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #add filename.opus to the metadata
        metadata = f"---\ndataview\ntimestamp: {timestamp}\n---\n![[{file_name}.opus]]\n\n"
        with open(os.path.join(self.vault_dir, file_name + ' Transcript.md'), 'w') as f:
            f.write(f"# Transcription of {file_name}\n\n{metadata}{transcription}")

    def process_folders(self, text_box, folder_listbox):
        for folder in self.config_handler.config.get('folder_list', []):
            folder = os.path.normpath(folder)
        text_box.configure(state='normal')  # Enable the text box
        text_box.insert(tk.END, "Starting Process...\n")
        for folder in self.config_handler.config.get('folder_list', []):
            text_box.insert(tk.END, f"Processing folder: {folder}\n")
            if os.path.exists(folder):
                text_box.insert(tk.END, f"Copying files from {folder} to {self.working_dir}...\n")
                self.copy_files(folder, self.working_dir)
                files = os.listdir(self.working_dir)
                if files:
                    text_box.insert(tk.END, f"Copied {len(files)} files to {self.working_dir}.\n")
                else:
                    text_box.insert(tk.END, f"No files copied to {self.working_dir}.\n")

                for file in files:
                    print("Processing file: ", file)
                    if file.lower().endswith('.wav') and not file.startswith('._'):
                        if file.lower().endswith('.wav'):  # make sure we only process .wav files
                            file_path = os.path.join(self.working_dir, file)
                            with tempfile.TemporaryDirectory() as temp_dir:
                                transcription = self.transcribe_audio(file_path, temp_dir)
                            self.clear_data(folder)
                            file_name = os.path.splitext(file)[0]
                            self.save_to_obsidian_vault(transcription, file_name)
                            # command = f"ffmpeg -i {file_path} -c:a libopus -b:a 32k {os.path.join(self.vault_dir, file_name + '.opus')}"
                            #command = f"ffmpeg -i \"{file_path}\" -c:a libopus -b:a 32k {os.path.join(self.working_dir, file_name + '.opus')}"
                            
                            file_path_escaped = file_path.replace('"', '\\"')
                            # output_path_escaped = os.path.join(self.working_dir, file_name + '.opus').replace('"', '\\"')

                            output_path_escaped = os.path.join(self.vault_dir, file_name + '.opus').replace('"', '\\"')


                            print("Saving Opus to : ", output_path_escaped)

                            command = f'ffmpeg -i "{file_path_escaped}" -c:a libopus -b:a 16k "{output_path_escaped}"'
                            print("Running ffmpeg command: ", command)
                            process = subprocess.Popen(
                                command,
                                shell=True,
                                cwd=self.working_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                            )
                            stdout, stderr = process.communicate()
                            if process.returncode != 0:
                                print(f"ffmpeg command failed with exit code {process.returncode}")
                                print(f"Standard error output:\n{stderr}")
                                return json.dumps({"error": stderr}), 500
                            else:
                                print(stdout)
                            print("Deleting wav file: ", file_path)
                            os.remove(os.path.join(self.working_dir, file))
                            for file in os.listdir(self.working_dir):
                                os.remove(os.path.join(self.working_dir, file))


                            text_box.insert(tk.END, f"Processed {file_name} and saved transcription to Obsidian vault.\n")
                    if file.startswith('._'):
                        print("Deleting file: ", file)
                        os.remove(os.path.join(self.working_dir, file))
                     
            else:
                text_box.insert(tk.END, f"Folder {folder} not found.\n")
        text_box.configure(state='disabled')  # Disable the text box once all text has been inserted
