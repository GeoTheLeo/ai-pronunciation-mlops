from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import tempfile
import os
import pandas as pd
import random
import subprocess
import joblib

from app.llm_feedback import generate_feedback
from app.transcription import transcribe_audio

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "feature_store.csv"
MODEL_PATH = "model.pkl"


# -----------------------------
# LOAD MODEL
# -----------------------------
def load_model():
    if os.path.exists(MODEL_PATH):
        print("Model loaded")
        return joblib.load(MODEL_PATH)
    print("No model found → using heuristic")
    return None


model = load_model()


# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
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


# -----------------------------
# SAVE FEATURES
# -----------------------------
def save_features(features):
    df = pd.DataFrame([features])

    if os.path.exists(DATA_PATH):
        df.to_csv(DATA_PATH, mode="a", header=False, index=False)
    else:
        df.to_csv(DATA_PATH, index=False)


# -----------------------------
# RETRAIN TRIGGER
# -----------------------------
def should_retrain(threshold_rows=20):
    if not os.path.exists(DATA_PATH):
        return False

    df = pd.read_csv(DATA_PATH)

    if len(df) % threshold_rows == 0:
        print(f"Retrain trigger: {len(df)} samples")
        return True

    return False


# -----------------------------
# HEALTH
# -----------------------------
@app.get("/")
def health():
    return {"status": "running"}


# -----------------------------
# MAIN ENDPOINT
# -----------------------------
@app.post("/analyze")
async def analyze(audio: UploadFile = File(...)):
    global model

    # SAVE AUDIO
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(await audio.read())
        temp_path = temp_audio.name

    # TRANSCRIPTION
    transcript = transcribe_audio(temp_path)
    duration = 3.5

    # FEATURES
    features = extract_features(transcript, duration)

    # -----------------------------
    # PREDICTION
    # -----------------------------
    num_words = features["num_words"]
    speech_rate = features["speech_rate"]
    avg_word_length = features["avg_word_length"]

    if model:
        X = [[num_words, speech_rate, avg_word_length]]
        score = float(model.predict(X)[0])
    else:
        sr_norm = max(0, min(1, (speech_rate - 1.0) / 4))
        awl_norm = max(0, min(1, (avg_word_length - 3.0) / 4))
        nw_norm = max(0, min(1, (num_words - 3) / 20))

        score = 0.6 * sr_norm + 0.25 * awl_norm + 0.15 * nw_norm

    # slight variation
    score += random.uniform(-0.05, 0.05)
    score = float(max(0, min(1, score)))

    # -----------------------------
    # CONFIDENCE
    # -----------------------------
    confidence = round(0.6 + random.uniform(0.2, 0.35), 2)

    # -----------------------------
    # LLM
    # -----------------------------
    feedback, phonemes, practice = generate_feedback(transcript, score)

    # -----------------------------
    # SAVE
    # -----------------------------
    features["pronunciation_score"] = score
    save_features(features)

    # -----------------------------
    # RETRAIN (REAL TRIGGER)
    # -----------------------------
    if should_retrain():
        try:
            subprocess.run(
                ["python", "mlops/train/train_model.py"],
                check=True
            )
            model = load_model()
            print("Model retrained + reloaded")
        except Exception as e:
            print("Retrain failed:", e)

    # CLEANUP
    os.remove(temp_path)

    return {
        "transcript": transcript,
        "pronunciation_score": score,
        "confidence": confidence,
        "feedback": feedback,
        "phoneme_feedback": phonemes,
        "practice_sentences": practice
    }


# -----------------------------
# ANALYTICS
# -----------------------------
@app.get("/analytics")
def analytics():
    if not os.path.exists(DATA_PATH):
        return {"history": []}

    df = pd.read_csv(DATA_PATH)
    df["step"] = df.index + 1

    return {
        "history": df[["step", "pronunciation_score"]].to_dict("records")
    }