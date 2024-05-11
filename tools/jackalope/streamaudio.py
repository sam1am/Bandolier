import cv2
import ffmpeg
import tempfile
from pydub import AudioSegment
from pydub.utils import mediainfo

def capture_audio(rtsp_url: str):
    """Capture audio from RTSP stream."""
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.aac').name

    # Use ffmpeg to capture audio from the RTSP stream
    stream = ffmpeg.input(rtsp_url)
    audio = stream.audio
    ffmpeg.output(audio, output_file, format='aac').run()

    return output_file

def calculate_audio_level(audio_file: str):
    """Calculate and return the audio level from an audio file."""
    # Load the audio file using pydub
    audio = AudioSegment.from_file(audio_file, format='aac')

    # Calculate the audio level
    return audio.dBFS

if __name__ == "__main__":
    RTSP_URL = "rtsp://192.168.81.75:8086"

    # Step 1: Capture the audio from rtsp stream
    audio_file = capture_audio(RTSP_URL)

    # Step 2: Calculate the audio level
    audio_level = calculate_audio_level(audio_file)
    print(f"Audio Level: {audio_level} dBFS")
