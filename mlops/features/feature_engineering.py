def extract_features(transcript: str, audio_duration: float):
    words = transcript.split()

    return {
        "num_words": len(words),
        "speech_rate": len(words) / max(audio_duration, 1),
        "avg_word_length": sum(len(w) for w in words) / max(len(words), 1),
    }