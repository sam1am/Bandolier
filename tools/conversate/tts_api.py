import gradio_client

tts_client = gradio_client.Client("http://localhost:7861/")

def convert_to_speech(text):
    tts_result = tts_client.predict(
        text,
        "Rogger",  # Selected speaker
        0.8,  # Speed
        "English",  # Language/Accent
        api_name="/gen_voice"
    )
    
    # tts_result is expected to be a file path
    with open(tts_result, "rb") as f:
        audio_data = f.read()
    
    with open("response.wav", "wb") as f:
        f.write(audio_data)
    # Implement logic to play the response audio
