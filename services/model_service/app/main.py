import os
import subprocess
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import joblib
import pandas as pd

from app.transcription import transcribe_audio
from app.llm_feedback import generate_feedback

app = FastAPI()

MODEL_PATH = os.path.abspath("model.pkl")
DATA_PATH = os.path.abspath("../../feature_store.csv")


def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None


model = load_model()


def extract_features(transcript, duration):
    words = transcript.split()
    num_words = len(words)

    speech_rate = num_words / duration if duration > 0 else 0
    avg_word_length = (
        sum(len(w) for w in words) / num_words if num_words > 0 else 0
    )

    return {
        "num_words": num_words,
        "speech_rate": speech_rate,
        "avg_word_length": avg_word_length
    }


def save_features(features):
    df = pd.DataFrame([features])

    if os.path.exists(DATA_PATH):
        df.to_csv(DATA_PATH, mode="a", header=False, index=False)
    else:
        df.to_csv(DATA_PATH, index=False)


def should_retrain(threshold=10):
    if not os.path.exists(DATA_PATH):
        return False

    df = pd.read_csv(DATA_PATH)
    return len(df) % threshold == 0


@app.post("/analyze")
async def analyze(audio: UploadFile = File(...)):
    global model

    file_path = f"temp_{audio.filename}"

    with open(file_path, "wb") as f:
        f.write(await audio.read())

    transcript = transcribe_audio(file_path)
    features = extract_features(transcript, duration=3.5)

    if model:
        score = model.predict([[
            features["num_words"],
            features["speech_rate"],
            features["avg_word_length"]
        ]])[0]
        score = float(max(0, min(1, score)))
    else:
        import random
        score = round(random.uniform(0.4, 0.9), 2)

    features["pronunciation_score"] = score
    save_features(features)

    if should_retrain():
        subprocess.run(["python", "mlops/train/train_model.py"])
        model = load_model()

    feedback, phonemes, _ = generate_feedback(transcript, score)

    os.remove(file_path)

    return {
        "transcript": transcript,
        "score": score,
        "feedback": feedback,
        "phonemes": phonemes
    }


# -----------------------------
# PRACTICE GENERATION
# -----------------------------
class PracticeRequest(BaseModel):
    target_language: str
    native_language: str


@app.post("/generate-practice")
def generate_practice(req: PracticeRequest):

    lang = req.target_language.lower()

    if lang == "german":
        sentences = [
            {"text": "Hallo, ich lerne Deutsch.", "phonetic": "HAL-lo ikh LER-ne DOYCH"},
            {"text": "Meine Muttersprache ist Englisch.", "phonetic": "MY-ne MUT-ter-shpra-khe ist ENG-lish"}
        ]

    elif lang == "japanese":
        sentences = [
            {"text": "こんにちは、私は日本語を勉強しています。",
             "phonetic": "Konnichiwa, watashi wa nihongo o benkyou shiteimasu"},
            {"text": "ゆっくり話してください。",
             "phonetic": "Yukkuri hanashite kudasai"}
        ]

    elif lang == "chinese":
        sentences = [
            {"text": "你好，我在学习中文。",
             "phonetic": "Nǐ hǎo, wǒ zài xuéxí zhōngwén"},
            {"text": "请说慢一点。",
             "phonetic": "Qǐng shuō màn yīdiǎn"}
        ]

    else:
        sentences = [
            {"text": "Hello, I am learning a language.", "phonetic": "standard pronunciation"},
            {"text": "Please speak slowly.", "phonetic": "clear slow speech"}
        ]

    return {"sentences": sentences}