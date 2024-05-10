import whisperx

def convert_audio_to_text(audio_file):
    model = whisperx.load_model("large-v2", "cpu", compute_type="int8")
    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, language="en", batch_size=16)
    text = ""
    for segment in result["segments"]:
        text += segment["text"]
    return text
