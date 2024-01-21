import tkinter as tk
from PIL import Image, ImageTk
import os
import yaml
import threading
import cv2
import base64
import requests
import time
import logging 

class MainScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure_layout()

        self.current_category_index = 0
        self.current_item_index = 0
        self.focus_on_category = False
        self.printing_enabled = True
        self.capture_initiated = False

        self.load_configuration()
        self.update_ui()  # Call update_ui to ensure UI is correctly initialized

        # Bind keyboard events
        self.master.bind('<t>', self.toggle_focus_event)
        self.master.bind('<p>', self.toggle_printing_event)
        self.master.bind('<j>', lambda event: self.navigate_items(-1))
        self.master.bind('<l>', lambda event: self.navigate_items(1))
        # get s down and release events and start the capture screen
        self.master.bind('<s>', self.shutter_key_down)


    def configure_layout(self):
        self.master.title('POETROID')
        self.pack(fill=tk.BOTH, expand=True)

        self.title_bar = tk.Label(self, text='POETROID', font=('Arial', 24))
        self.title_bar.pack(side=tk.TOP, fill=tk.X)

        self.category_panel = tk.Frame(self, borderwidth=2, relief='solid')
        self.category_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.category_emoji = tk.Label(self.category_panel, font=('Arial', 100))
        self.category_emoji.pack()

        self.item_panel = tk.Frame(self, borderwidth=2, relief='solid')
        self.item_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.item_image_label = tk.Label(self.item_panel)
        self.item_image_label.pack()

        self.controls_panel = tk.Frame(self)
        self.controls_panel.pack(side=tk.BOTTOM, fill=tk.X)

        self.printer_icon = tk.Label(self.controls_panel, text='Print', font=('Arial', 16))
        self.printer_icon.pack(side=tk.LEFT)

    def load_configuration(self):
        with open('./categories.yaml', 'r') as file:
            self.categories = yaml.safe_load(file)['categories']
        with open('./models.yaml', 'r') as file:
            self.models = yaml.safe_load(file)['models']

    def update_ui(self):
        emoji_name = self.categories[self.current_category_index]['emoji']
        self.category_emoji['text'] = emoji_name

        item = self.categories[self.current_category_index]['prompts'][self.current_item_index]
        img_path = os.path.join('./imgs', item['imagefilename'])
        self.update_image(img_path)
        self.printer_icon['text'] = 'Print Enabled' if self.printing_enabled else 'Print Disabled'

    def update_image(self, img_path):
        img = Image.open(img_path)
        photo = ImageTk.PhotoImage(img)
        self.item_image_label.photo = photo  # Keep a reference to avoid garbage collection
        self.item_image_label.config(image=photo)

    def toggle_focus(self):
        self.focus_on_category = not self.focus_on_category

    def toggle_category(self, direction):
        num_categories = len(self.categories)
        self.current_category_index = (self.current_category_index + direction) % num_categories
        self.current_item_index = 0
        self.update_ui()

    def toggle_item(self, direction):
        num_items = len(self.categories[self.current_category_index]['prompts'])
        self.current_item_index = (self.current_item_index + direction) % num_items
        self.update_ui()

    def toggle_printing(self):
        self.printing_enabled = not self.printing_enabled
        self.update_ui()
    
    def toggle_focus_event(self, event):
        self.toggle_focus()

    def toggle_printing_event(self, event):
        self.toggle_printing()

    def navigate_items(self, direction):
        if self.focus_on_category:
            self.toggle_category(direction)
        else:
            self.toggle_item(direction)
    
    # trigger capture screen when held for three seconds
    def shutter_key_down(self, event):
        if not self.capture_initiated:
            self.capture_initiated = True
            self.master.bind('<KeyRelease-s>', self.shutter_key_up)
            self.master.after(3000, self.show_capture_screen)

    def shutter_key_up(self, event):
        self.master.unbind('<KeyRelease-s>')
        self.master.after_cancel(self.show_capture_screen)
        time.sleep(1)
        self.capture_initiated = False
    
    def show_capture_screen(self, event=None):
        self.master.unbind('<KeyRelease-s>')
        self.capture_screen = CaptureScreen(self.master)
        self.capture_screen.start_processing()

    
class CaptureScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.status_label = tk.Label(self, text='Thinking...')
        self.status_label.pack()
        self.pack()

    def start_processing(self):
        self.status_label.config(text='Thinking...')
        thread = threading.Thread(target=self.capture_and_process_image)
        thread.start()
    
    def find_working_camera_index(null):
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                cap.release()
                print(f"Found working camera at index {index}")
                return index
            cap.release()
            index += 1
            if index > 10:  # Prevent an infinite loop by setting a limit on the indices to check
                raise IOError("No working camera found within index range 0-10.")

    
    def capture_and_process_image(self):
        camera_indices = [1, 2]
        frame = None
        for camera_index in camera_indices:
            cap = cv2.VideoCapture(camera_index)
            ret, frame = cap.read()
            cap.release()
            if ret:
                break  # We found a working camera index, so we can break out of the loop

        if frame is None:
            self.status_label['text'] = 'Failed to capture image from any known camera index.'
            return

        ret, frame = cap.read()
        cap.release()
        if not ret:
            # Logger.error('Capture: Failed to capture image from stream')
            self.status_label.text = 'Failed to capture image.'
            return
        encoded_image = base64.b64encode(frame).decode('utf-8')

        # Construct the prompt
        main_screen = self.manager.get_screen('main')
        category_index = main_screen.current_category_index
        item_index = main_screen.current_item_index
        prompt = main_screen.categories[category_index]['prompts'][item_index]['prompt']
        
        # Send the request to the API
        try:
            response = requests.post(
                "https://roast.wayr.app/behold",
                json={
                    "prompt": prompt,
                    "image": encoded_image.decode('utf-8')
                },
                timeout=10
            )
            response.raise_for_status()
            response_data = response.json()
            self.display_response(response_data['response'])
        except requests.RequestException as e:
            # Logger.error(f'Capture: Failed to send request or receive valid response: {e}')
            self.status_label.text = 'Failed to get response.'

    def display_response(self, response_text):
        self.status_label.text = response_text

        # Handle printing
        main_screen = self.manager.get_screen('main')
        if main_screen.printing_enabled:
            try:
                with open('/dev/usb/lp0', 'w') as printer:
                    printer.write(response_text + '\n\n\n\n\n')
            except IOError as e:
                # Logger.error(f'Print: Failed to print to /dev/usb/lp0: {e}')
                self.status_label.text = 'Failed to print.'
        
        # Add a button to go back to the main screen
        go_back_button = Button(text='Go back', size_hint_y=0.1)
        go_back_button.bind(on_press=self.go_back_to_main)
        self.add_widget(go_back_button)

    def go_back_to_main(self):
        self.destroy()  # Remove the capture screen from view
        self.master.main_screen.update_ui()

class PoetroidApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('480x800')
        self.main_screen = MainScreen(self)
        # self.capture_screen = CaptureScreen(self)  # You can toggle this screen when you need to capture and process images.

if __name__ == '__main__':
    app = PoetroidApp()
    app.mainloop()