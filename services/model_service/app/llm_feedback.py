from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_feedback(transcript, score):
    # -----------------------------
    # ADAPTIVE DIFFICULTY
    # -----------------------------
    if score < 0.4:
        level = "beginner"
    elif score < 0.7:
        level = "intermediate"
    else:
        level = "advanced"

    prompt = f"""
You are an expert pronunciation coach.

User said:
"{transcript}"

Score: {score}

LEVEL: {level}

1. Give short feedback (max 3 sentences)
2. Identify 1–2 pronunciation issues (phoneme-level if possible)
3. Generate 5 practice sentences appropriate for {level}

FORMAT:

FEEDBACK:
...

PHONEMES:
- issue 1
- issue 2

PRACTICE:
1. ...
2. ...
3. ...
4. ...
5. ...
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content

    feedback = ""
    phonemes = []
    practice = []

    try:
        parts = content.split("PRACTICE:")
        before = parts[0]
        practice_block = parts[1]

        feedback_part = before.split("PHONEMES:")[0]
        phoneme_part = before.split("PHONEMES:")[1]

        feedback = feedback_part.replace("FEEDBACK:", "").strip()

        phonemes = [
            line.strip("- ").strip()
            for line in phoneme_part.split("\n")
            if line.strip().startswith("-")
        ]

        practice = [
            line.split(".", 1)[1].strip()
            for line in practice_block.split("\n")
            if line.strip() and line[0].isdigit()
        ]

    except Exception:
        feedback = content

    return feedback, phonemes, practice