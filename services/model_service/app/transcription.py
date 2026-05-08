import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def transcribe_audio(file_path):

    try:

        with open(file_path, "rb") as audio_file:

            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        return transcript.text

    except Exception as e:

        print("Transcription failed:", e)

        return "Transcription unavailable."