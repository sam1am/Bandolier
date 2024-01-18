import sys
import os
import yaml
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

# Helper function to load contents from a YAML file
def load_yaml_file(filename):
    with open(filename, 'r') as f:
        return yaml.safe_load(f)

class PoetroidWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Poetroid')
        self.setGeometry(100, 100, 800, 480)  # Arbitrarily positioned on the screen for now

        # Initialize categories, prompts, and models from YAML files
        self.categories = load_yaml_file('./categories.yaml')
        self.prompts = load_yaml_file('./prompts.yaml')
        self.models = load_yaml_file('./models.yaml')
        self.current_category_index = 0
        self.current_prompt_index = 0
        self.current_model_index = 0
        self.print_enabled = False
        self.selected_panel = 'left'
        
        # Initialize UI components
        self.initUI()

    def initUI(self):
        # Main layout
        self.main_widget = QWidget(self)
        self.main_layout = QHBoxLayout(self.main_widget)
        
        # Left panel
        self.left_panel = QLabel(self)
        self.left_panel.setFixedSize(300, 300)
        self.load_category_image()

        # Right panel
        self.right_panel = QLabel(self)
        self.right_panel.setFixedSize(300, 300)
        self.load_prompt_image()

        # Top title bar
        self.title_bar = QLabel('Poetroid', self)
        self.title_bar.setAlignment(Qt.AlignCenter)
        
        # Bottom model bar
        self.model_bar = QLabel(self.models['models'][self.current_model_index]['name'], self)
        self.model_bar.setAlignment(Qt.AlignCenter)

        # Layout configuration
        self.vbox_left = QVBoxLayout()
        self.vbox_left.addWidget(self.title_bar)
        self.vbox_left.addWidget(self.left_panel)

        self.vbox_right = QVBoxLayout()
        self.vbox_right.addWidget(self.model_bar)
        self.vbox_right.addWidget(self.right_panel)

        self.main_layout.addLayout(self.vbox_left)
        self.main_layout.addLayout(self.vbox_right)

        self.update_panel_borders()
        self.setCentralWidget(self.main_widget)
        self.show()

    def load_category_image(self):
        category = self.categories['categories'][self.current_category_index]
        pixmap = QPixmap(os.path.join('./imgs', category['imagefilename']))
        self.left_panel.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))

    def load_prompt_image(self):
        prompt = self.prompts['prompts'][self.current_prompt_index]
        emoji_code = ord(prompt['emoji'])
        emoji_pixmap = QPixmap(os.path.join('./imgs', f'emoji_{emoji_code}.png'))
        self.right_panel.setPixmap(emoji_pixmap.scaled(300, 300, Qt.KeepAspectRatio))

    def update_panel_borders(self):
        if self.selected_panel == 'left':
            self.left_panel.setStyleSheet('border: 3px solid yellow')
            self.right_panel.setStyleSheet('')
        else:
            self.left_panel.setStyleSheet('')
            self.right_panel.setStyleSheet('border: 3px solid yellow')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_I:
            self.print_enabled = not self.print_enabled
            # TODO: Set print icon color based on state
        elif event.key() == Qt.Key_L:
            if self.selected_panel == 'left':
                self.current_category_index = (self.current_category_index + 1) % len(self.categories['categories'])
                self.load_category_image()
            else:
                self.current_prompt_index = (self.current_prompt_index + 1) % len(self.prompts['prompts'])
                self.load_prompt_image()
        elif event.key() == Qt.Key_J:
            if self.selected_panel == 'left':
                self.current_category_index = (self.current_category_index - 1) % len(self.categories['categories'])
                self.load_category_image()
            else:
                self.current_prompt_index = (self.current_prompt_index - 1) % len(self.prompts['prompts'])
                self.load_prompt_image()
        elif event.key() == Qt.Key_K:
            self.selected_panel = 'right' if self.selected_panel == 'left' else 'left'
            self.update_panel_borders()
        elif event.key() == Qt.Key_O:
            self.current_model_index = (self.current_model_index + 1) % len(self.models['models'])
            self.model_bar.setText(self.models['models'][self.current_model_index]['name'])

        super().keyPressEvent(event)

# Main application execution
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PoetroidWindow()
    sys.exit(app.exec_())
