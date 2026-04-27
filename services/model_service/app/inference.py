from typing import Dict

def score_pronunciation(transcript: str) -> Dict:
    """
    Very simple placeholder scoring logic.
    Remember to replace later with phoneme / alignment model.
    """
    score = 1.0 if len(transcript.strip()) > 0 else 0.0

    if score > 0.9:
        cefr = "C1"
    elif score > 0.75:
        cefr = "B2"
    elif score > 0.6:
        cefr = "B1"
    else:
        cefr = "A2"

    return {
        "transcript": transcript,
        "pronunciation_score": score,
        "cefr_level": cefr
    }


def generate_feedback(transcript: str, score: float) -> str:
    """
    Human-readable coaching feedback.
    This is what turns the project into a PRODUCT.
    """

    if score > 0.9:
        return (
            "Excellent pronunciation!! Your clarity is strong. "
            "Focus on natural rhythm and intonation to sound even more native."
        )

    elif score > 0.75:
        return (
            "Good pronunciation overall! Improve vowel length - short or long - and note those stress patterns! "
            "Pay attention to syllable emphasis in longer words."
        )

    elif score > 0.6:
        return (
            "Understandable, but needs improvement. Work on consonant articulation "
            "and a more consistent speech rhythm."
        )

    else:
        return (
            "Pronunciation needs work. Slow down your speech and focus on individual "
            "sounds (phonemes). Practice basic word clarity first, and you're well on your way!"
        )