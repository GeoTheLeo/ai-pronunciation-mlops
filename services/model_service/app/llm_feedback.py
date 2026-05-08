import random

def generate_feedback(transcript, score):

    text = transcript.lower()

    # -----------------------------
    # BASIC FEEDBACK
    # -----------------------------
    if score > 0.75:
        feedback = "Great pronunciation. Your speech is clear and natural."
    elif score > 0.5:
        feedback = "Good effort. Some sounds can be more precise."
    else:
        feedback = "Focus on clarity and slower pronunciation."

    # -----------------------------
    # LANGUAGE-AWARE PHONEMES
    # -----------------------------
    phoneme_map = {
        "german": [
            "Practice the 'ch' sound (as in 'ich')",
            "Focus on umlauts: ä, ö, ü",
            "Pay attention to 'r' pronunciation"
        ],
        "spanish": [
            "Roll the 'r' sound",
            "Work on clear vowel sounds (a, e, i, o, u)",
            "Avoid English-style diphthongs"
        ],
        "french": [
            "Practice nasal vowels (on, an, en)",
            "Focus on silent endings",
            "Work on the French 'r'"
        ],
        "russian": [
            "Focus on hard vs soft consonants",
            "Practice rolled 'r'",
            "Work on vowel reduction"
        ],
        "english": [
            "Work on 'th' sounds",
            "Practice stress patterns",
            "Focus on consonant clarity"
        ]
    }

    # -----------------------------
    # INFER LANGUAGE (SIMPLE HEURISTIC)
    # -----------------------------
    if any(word in text for word in ["ich", "nicht", "hallo"]):
        lang = "german"
    elif any(word in text for word in ["hola", "gracias"]):
        lang = "spanish"
    elif any(word in text for word in ["bonjour"]):
        lang = "french"
    elif any(word in text for word in ["здравствуйте"]):
        lang = "russian"
    else:
        lang = "english"

    phonemes = random.sample(phoneme_map[lang], 2)

    # -----------------------------
    # PRACTICE (OPTIONAL LIGHT USE)
    # -----------------------------
    practice = [
        "Repeat the sentence slowly",
        "Focus on difficult sounds",
        "Practice with rhythm"
    ]

    return feedback, phonemes, practice