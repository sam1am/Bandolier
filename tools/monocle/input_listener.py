# input_listener.py
from pynput import keyboard
from datetime import datetime
import asyncio

class InputListener:
    def __init__(self, display_queue, note_manager, loop):
        self.update_display_callback = display_queue  # Assuming this is the intended use
        self.note_manager = note_manager
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.display_queue = display_queue  # Ensure this attribute is correctly initialized
        self.lines = [">"]
        self.title = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        self.current_note_id = None
        self.loop = loop

    
    def start(self):
        self.listener.start()
    
    def on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                self.lines[-1] += key.char
            elif key == keyboard.Key.space:
                self.lines[-1] += ' '
            elif key == keyboard.Key.backspace:
                if self.lines[-1] and self.lines[-1] != ">":
                    self.lines[-1] = self.lines[-1][:-1]
                elif len(self.lines) > 1:
                    self.lines.pop()
            elif key == keyboard.Key.enter:
                if len(self.lines) > 1 and not self.lines[-1]:
                    if self.lines[0] != ">":
                        note_content = '\n'.join(self.lines[:-1])
                        self.note_manager.save_note(self.current_note_id, self.title, note_content)
                    self.lines = [">"]
                    self.title = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                    self.current_note_id = None
                else:
                    self.lines.append("")
            elif key == keyboard.Key.left:
                note = self.note_manager.fetch_note(self.current_note_id, 'previous')
                if note:
                    self.current_note_id, self.title, content = note
                    self.lines = content.split('\n') + [""]
            elif key == keyboard.Key.right:
                note = self.note_manager.fetch_note(self.current_note_id, 'next')
                if note:
                    self.current_note_id, self.title, content = note
                    self.lines = content.split('\n') + [""]
                else:
                    self.current_note_id = None
                    self.title = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                    self.lines = [">"]
            else:
                return

            self.display_queue.put(('\n'.join(self.lines), self.title))
        except Exception as e:
            print(f"Error in InputListener: {e}")
