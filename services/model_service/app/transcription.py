import whisper
import os

# Load once (important for performance)
model = whisper.load_model("base")


def transcribe_audio(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError("Audio file not found")

    result = model.transcribe(file_path)

    return result["text"].strip()