def transcribe_audio(file_path):
    """
    Demo-safe transcription (no external dependency)
    Always returns a valid transcript
    """
    try:
        # You can customize this if needed
        return "This is a demo transcription for pronunciation analysis."
    except Exception as e:
        return "Audio could not be transcribed."