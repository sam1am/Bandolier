import tkinter as tk
from tkinter import filedialog, Label, Button, Frame
import tkinter.scrolledtext as st
from ttkthemes import ThemedTk
from config_handler import ConfigHandler
from audio_processing import AudioProcessor
import os

class App:
    def __init__(self):
        self.config_handler = ConfigHandler()
        self.audio_processor = AudioProcessor(self.config_handler)

        self.create_app_interface()

    def create_app_interface(self):
        root = ThemedTk(theme="arc")
        root.title("Assammilator")
        root.geometry("600x400")
        root.minsize(600, 400)
        root.call('tk', 'scaling', 2.0)

        frame1 = self.create_frame(root)
        frame2 = self.create_frame(root)
        frame3 = self.create_frame(root)
        frame4 = self.create_frame(root, "bottom")

        

        self.vault_label = self.create_label(frame1, "Vault:\n" + '...' + self.audio_processor.vault_dir[-50:], 'left')
        folders_label = self.create_label(frame2, "Folders to Process:", 'top')
        self.folder_listbox = tk.Listbox(frame2, width=50, height=10)
        self.folder_listbox.pack(fill='both')
        compute_type_label = self.create_label(frame1, "Compute Type:\n" + self.audio_processor.compute_type, 'bottom')

        self.text_box = st.ScrolledText(frame3, height=3)
        self.text_box.configure(state='disabled')
        self.text_box.pack(fill='both', expand=True)

        add_button = self.create_button(frame4, "Add Folder", self.add_folder, 'left')
        set_button = self.create_button(frame4, "Set Vault", self.set_vault, 'left')
        start_button = self.create_button(frame4, "Start", self.start_processing, 'left')

        for folder in self.config_handler.config.get('folder_list', []):
            self.folder_listbox.insert(tk.END, folder)

        root.mainloop()

    def create_frame(self, root, side=None):
        frame = Frame(root, padx=5, pady=5)
        frame.pack(fill='x', side=side) if side else frame.pack(fill='x')
        return frame

    def create_label(self, frame, text, side):
        label = Label(frame, text=text)
        label.pack(side=side)
        return label

    def create_button(self, frame, text, command, side):
        button = Button(frame, text=text, command=command)
        button.pack(side=side)
        return button

    def add_folder(self):
        folder = os.path.normpath(filedialog.askdirectory())
        if folder:
            if 'folder_list' not in self.config_handler.config:
                self.config_handler.config['folder_list'] = []
            self.config_handler.config['folder_list'].append(folder)

            self.folder_listbox.insert(tk.END, folder)
            self.config_handler.save_config()


    def set_vault(self):
        self.audio_processor.vault_dir = os.path.normpath(filedialog.askdirectory())
        if not os.path.exists(self.audio_processor.vault_dir):
            os.makedirs(self.audio_processor.vault_dir)
        self.config_handler.config['vault_dir'] = self.audio_processor.vault_dir
        # Also update the vault directory in the ConfigHandler instance
        self.config_handler.vault_dir = self.audio_processor.vault_dir
        self.config_handler.save_config()
        print("Vault set to: ", self.audio_processor.vault_dir)
        self.vault_label.config(text="Vault:\n" + '...' + self.audio_processor.vault_dir[-50:])  # Update the vault label


    def start_processing(self):
        self.audio_processor.process_folders(self.text_box, self.folder_listbox)

if __name__ == "__main__":
    App()
