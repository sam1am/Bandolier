import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.logger import Logger
import yaml
import os
import cv2
import base64
import requests
import threading

kivy.require('2.0.0')

Window.size = (480, 800)

class CustomBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        self.selected = False
        super(CustomBoxLayout, self).__init__(**kwargs)

    def on_size(self, *args):
        self.update_border()

    def on_pos(self, *args):
        self.update_border()

    def update_border(self):
        with self.canvas.before:
            self.canvas.before.clear()
            if self.selected:
                Color(1, 1, 0)  # Yellow color
                Line(rectangle=(self.x + 1, self.y + 1, self.width - 2, self.height - 2), width=2)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.title_bar = BoxLayout(size_hint_y=None, height=50)
        self.title_label = Label(text='POETROID', size_hint_x=0.9, halign='left', valign='middle', font_name='seguiemj')
        self.title_label.bind(size=self.title_label.setter('text_size'))
        self.printer_icon = Label(text='\N{Printer}', font_size='48sp', size_hint_x=0.1, font_name='seguiemj', halign='right', valign='middle')
        self.title_bar.add_widget(self.title_label)
        self.title_bar.add_widget(self.printer_icon)
        self.layout.add_widget(self.title_bar)

        self.category_panel = CustomBoxLayout(size_hint_y=0.45)
        self.category_emoji = Label(font_size='300sp', font_name='seguiemj')
        self.category_panel.add_widget(self.category_emoji)
        self.layout.add_widget(self.category_panel)

        self.item_panel = CustomBoxLayout(size_hint_y=0.45, padding=10)
        self.item_image = Image()
        self.item_panel.add_widget(self.item_image)
        self.layout.add_widget(self.item_panel)

        self.current_category_index = 0
        self.current_item_index = 0
        self.focus_on_category = False  # Set the initial focus to True
        self.printing_enabled = True

        self.add_widget(self.layout)
        self.load_configuration()
        self.update_ui()  # Call update_ui to ensure UI is correctly initialized

        # Key bindings
        self._keyboard = Window.request_keyboard(self.close_keyboard, self)
        self._keyboard.bind(on_key_down=self.on_keyboard_down)

    def load_configuration(self):
        with open('./categories.yaml', 'r') as file:
            self.categories = yaml.safe_load(file)['categories']
        with open('./models.yaml', 'r') as file:
            self.models = yaml.safe_load(file)['models']

    def update_ui(self):
        for panel in [self.category_panel, self.item_panel]:
            panel.selected = False

        # Update the emoji and image based on current focus
        if self.focus_on_category:
            self.category_panel.selected = True
            emoji_name = self.categories[self.current_category_index]['emoji']
            self.category_emoji.text = chr(int(emoji_name, 16))
        else:
            self.item_panel.selected = True
            item = self.categories[self.current_category_index]['prompts'][self.current_item_index]
            img_path = os.path.join('./imgs', item['imagefilename'])
            self.item_image.source = img_path
            self.item_image.reload()  # Force refresh the image

        # Update border highlighting
        self.item_panel.update_border()
        self.category_panel.update_border()

        # Update the printer icon opacity
        self.printer_icon.opacity = 1 if self.printing_enabled else 0


    def close_keyboard(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self.on_keyboard_down)
            self._keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        if key == 't':
            self.focus_on_category = not self.focus_on_category
            self.update_ui()  # Update UI when toggling focus
        elif key in ('j', 'l'):
            if self.focus_on_category:
                previous_category_index = self.current_category_index
                num_categories = len(self.categories)
                self.current_category_index = (self.current_category_index + (1 if key == 'l' else -1)) % num_categories
                if previous_category_index != self.current_category_index:
                    self.current_item_index = 0  # Reset item index when changing categories
            else:
                num_items = len(self.categories[self.current_category_index]['prompts'])
                self.current_item_index = (self.current_item_index + (1 if key == 'l' else -1)) % num_items
            self.update_ui()  # Update UI after changing categories or items
        elif key == 'p':
            self.printing_enabled = not self.printing_enabled
            self.update_ui()  # Update the UI to reflect the change in printing status
        return True

class CaptureScreen(Screen):
    def __init__(self, **kwargs):
        super(CaptureScreen, self).__init__(**kwargs)

        self.status_label = Label(text='Thinking...', size_hint_y=1)
        self.add_widget(self.status_label)

        self.thinking = False

    def start_processing(self):
        self.status_label.text = 'Thinking...'
        self.thinking = True
        thread = threading.Thread(target=self.capture_and_process_image)
        thread.start()

    def capture_and_process_image(self):
        stream_url = 'rtsp://192.168.81.37:8554/mjpeg/1'
        cap = cv2.VideoCapture(stream_url)
        # Flush the buffer to grab the latest frame
        for _ in range(30):
            cap.grab()
        ret, frame = cap.read()
        cap.release()
        if not ret:
            Logger.error('Capture: Failed to capture image from stream')
            self.status_label.text = 'Failed to capture image.'
            return
        
        # Prepare image for POST request
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            Logger.error('Capture: Failed to encode image to JPEG')
            self.status_label.text = 'Failed to encode image.'
            return
        encoded_image = base64.b64encode(buffer).tobytes()

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
            Logger.error(f'Capture: Failed to send request or receive valid response: {e}')
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
                Logger.error(f'Print: Failed to print to /dev/usb/lp0: {e}')
        
        # Add a button to go back to the main screen
        go_back_button = Button(text='Go back', size_hint_y=0.1)
        go_back_button.bind(on_press=self.go_back_to_main)
        self.add_widget(go_back_button)

    def go_back_to_main(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'main'

class PoetroidApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.main_screen = MainScreen(name='main')
        self.capture_screen = CaptureScreen(name='capture')
        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.capture_screen)
        return self.screen_manager

if __name__ == '__main__':
    PoetroidApp().run()
