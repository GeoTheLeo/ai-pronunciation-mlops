import random

def generate_feedback(transcript, score):

    text = transcript.lower()

    # -----------------------------
    # GENERAL FEEDBACK
    # -----------------------------
    if score > 0.75:

        feedback = (
            "Great pronunciation. "
            "Your speech sounds natural."
        )

    elif score > 0.5:

        feedback = (
            "Good effort. "
            "Focus on clearer articulation."
        )

    else:

        feedback = (
            "Try speaking more slowly "
            "and clearly."
        )

    # -----------------------------
    # TRANSCRIPT-AWARE FEEDBACK
    # -----------------------------
    phonemes = []

    # GERMAN
    if any(word in text for word in [
        "guten",
        "deutsch",
        "ich",
        "bitte"
    ]):

        if "ich" in text:
            phonemes.append(
                "Practice the German 'ch' sound in 'ich'"
            )

        if "r" in text:
            phonemes.append(
                "Focus on German rolling 'r' sounds"
            )

        phonemes.append(
            "Practice clean umlaut pronunciation"
        )

    # FRENCH
    elif any(word in text for word in [
        "bonjour",
        "français",
        "voudrais"
    ]):

        phonemes.append(
            "Practice French nasal vowels"
        )

        phonemes.append(
            "Soften hard consonants"
        )

        phonemes.append(
            "Focus on French rhythm and flow"
        )

    # SPANISH
    elif any(word in text for word in [
        "hola",
        "español",
        "puede"
    ]):

        phonemes.append(
            "Practice rolling Spanish 'r' sounds"
        )

        phonemes.append(
            "Keep vowels short and clear"
        )

        phonemes.append(
            "Reduce English-style diphthongs"
        )

    # PORTUGUESE
    elif any(word in text for word in [
        "olá",
        "português",
        "você"
    ]):

        phonemes.append(
            "Practice Portuguese nasal vowels"
        )

        phonemes.append(
            "Focus on smooth consonant transitions"
        )

        phonemes.append(
            "Work on Portuguese rhythm patterns"
        )

    # RUSSIAN
    elif any(word in text for word in [
        "русский",
        "здравствуйте"
    ]):

        phonemes.append(
            "Differentiate hard and soft consonants"
        )

        phonemes.append(
            "Practice Russian stress placement"
        )

        phonemes.append(
            "Strengthen rolling 'r' sounds"
        )

    # JAPANESE
    elif any(word in text for word in [
        "こんにちは",
        "日本語"
    ]):

        phonemes.append(
            "Keep vowel timing even"
        )

        phonemes.append(
            "Use softer consonant transitions"
        )

        phonemes.append(
            "Focus on pitch consistency"
        )

    # CHINESE
    elif any(word in text for word in [
        "你好",
        "中文"
    ]):

        phonemes.append(
            "Practice tonal consistency"
        )

        phonemes.append(
            "Focus on syllable timing"
        )

        phonemes.append(
            "Avoid clipped consonant endings"
        )

    # FALLBACK
    else:

        phonemes.append(
            "Focus on pronunciation clarity"
        )

        phonemes.append(
            "Practice smoother speech rhythm"
        )

        phonemes.append(
            "Slow down difficult sounds"
        )

    # -----------------------------
    # PRACTICE TIPS
    # -----------------------------
    practice = [
        "Repeat difficult phrases slowly",
        "Practice consistently",
        "Focus on rhythm and articulation"
    ]

    return (
        feedback,
        random.sample(
            phonemes,
            min(2, len(phonemes))
        ),
        practice
    )