def score_pronunciation(transcript: str) -> dict:
    # Placeholder scoring logic (we’ll improve later)
    score = min(len(transcript) / 50, 1.0)

    cefr_level = "C1" if score > 0.7 else "B2"

    return {
        "transcript": transcript,
        "pronunciation_score": score,
        "cefr_level": cefr_level
    }