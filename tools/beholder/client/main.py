import sys
import cv2
import os
import io
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

# API Endpoints
API_ENDPOINT_BEHOLD = "https://roast.wayr.app/behold"
API_ENDPOINT_INFER = "https://roast.wayr.app/infer"

# Create the main application window
class WebcamWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open webcam")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(50)

    def initUI(self):
        layout = QVBoxLayout(self)
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)
        self.capture_button = QPushButton('Take Photo', self)
        self.capture_button.clicked.connect(self.capture_photo)
        layout.addWidget(self.capture_button)
        self.result_text_edit = QTextEdit(self)
        self.result_text_edit.setReadOnly(True)
        layout.addWidget(self.result_text_edit)
        self.setLayout(layout)
        self.setWindowTitle('Webcam capture and API interaction')
        self.show()

    def update_image(self):
        ret, frame = self.cap.read()
        if ret:
            height, width, channel = frame.shape
            bytes_per_line = channel * width
            qImg = QImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), width, height, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(qImg))

    def capture_photo(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        self.result_text_edit.setText("Thinking...")
        _, buffer = cv2.imencode('.jpg', frame)
        io_buf = io.BytesIO(buffer)
        response_behold = requests.post(
            API_ENDPOINT_BEHOLD,
            files={'file': io_buf},
            data={'prompt': 'describe this image in as much detail as possible. Be as verbose as possible.'}
        )
        if response_behold.status_code == 200:
            behold_data = response_behold.json()
            description = behold_data['response']
            response_infer = requests.post(
                API_ENDPOINT_INFER,
                params={
                    'prompt': 'write an esoteric scripture based on the following scene description: ' + description,
                    'model': 'hermes-trismegistus-mistral',
                    }
            )
            if response_infer.status_code == 200:
                infer_data = response_infer.json()
                poem = infer_data['response']
                self.result_text_edit.setText(poem)
                if os.path.exists("/dev/usb/lp0"):
                    with open("/dev/usb/lp0", "w") as printer:
                        printer.write(poem + "\n\n\n\n\n")
            else:
                self.result_text_edit.setText(f"Failed to get poem from /infer endpoint. Status code: {response_infer.status_code}")
        else:
            self.result_text_edit.setText(f"Failed to send image to /behold endpoint. Status code: {response_behold.status_code}")

    def closeEvent(self, event):
        self.cap.release()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    webcam_widget = WebcamWidget()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
