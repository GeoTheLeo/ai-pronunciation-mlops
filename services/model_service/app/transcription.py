from openai import OpenAI
import os

# Initialize client using environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio(file_path):
    """
    Transcribe audio using OpenAI Whisper API.
    This avoids heavy local models and works in cloud environments.
    """

    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file
            )

        return transcript.text

    except Exception as e:
        return f"Transcription error: {str(e)}"