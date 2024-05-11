# app.py
import tkinter as tk
from main_screen import MainScreen
from capture_screen import CaptureScreen

class PoetroidApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('POETROID')
        self.geometry('480x800')

        self.screen_manager = {}
        self._build_screens()

    def _build_screens(self):
        self.screen_manager['main'] = MainScreen(self)
        self.screen_manager['capture'] = CaptureScreen(self)

        self.screen_manager['main'].pack(fill='both', expand=True)
        self.show_screen('main')

    def show_screen(self, name):
        screen = self.screen_manager.get(name)
        if screen:
            screen.tkraise()  # Bring the screen to the front

    def run(self):
        self.mainloop()

if __name__ == '__main__':
    app = PoetroidApp()
    app.run()
