import json
import os

from openai import OpenAI

MODEL = "gpt-4o-mini"

_client = None


def _get_client():
    global _client

    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    return _client


SYSTEM_PROMPT = (
    "You are a supportive multilingual pronunciation coach. Respond ONLY with a JSON "
    "object with exactly these keys: \"feedback\" (a short, encouraging 1-3 sentence "
    "assessment), \"phonemes\" (an array of 1-2 short, specific sound/phoneme tips), and "
    "\"practice\" (an array of 1-2 short practice suggestions)."
)


def generate_feedback(transcript, target_text=None, score=None):

    if target_text:

        user_content = (
            f"Target phrase: \"{target_text}\"\n"
            f"What the speech-to-text engine heard: \"{transcript}\"\n"
            f"Text-similarity score between target and transcript, 0 to 1 "
            f"(1 = identical text; not a measure of accent quality): {score}\n\n"
            "Give feedback on how closely the learner's speech matched the target "
            "phrase, calling out likely mispronounced or missed words."
        )

    else:

        user_content = (
            f"What the speech-to-text engine heard: \"{transcript}\"\n\n"
            "No target phrase was given (free/open practice). Give general feedback on "
            "the clarity and fluency suggested by this transcript."
        )

    try:

        response = _get_client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        data = json.loads(response.choices[0].message.content)

        feedback = data.get("feedback", "No feedback available.")
        phonemes = data.get("phonemes", [])
        practice = data.get("practice", [])

        return feedback, phonemes, practice

    except Exception as e:

        print("LLM feedback generation failed:", e)

        return (
            "AI feedback is temporarily unavailable. Please try again in a moment.",
            [],
            [],
        )
