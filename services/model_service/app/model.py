import whisper

class PronunciationModel:
    def __init__(self):
        print("Loading Whisper model...")
        self.model = whisper.load_model("base")

    def transcribe(self, audio_path: str):
        result = self.model.transcribe(audio_path)
        return result["text"]