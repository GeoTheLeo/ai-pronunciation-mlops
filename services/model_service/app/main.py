from fastapi import FastAPI, UploadFile, File
import tempfile
import os
import joblib

from mlops.features.feature_engineering import extract_features
from mlops.features.feature_store import save_features

app = FastAPI()

# -----------------------------
# LOAD TRAINED MODEL
# -----------------------------
MODEL_PATH = "mlops/models/model.pkl"

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None


@app.get("/")
def health():
    return {"status": "model service running"}


@app.post("/analyze")
async def analyze(audio: UploadFile = File(...)):

    # Save audio temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(await audio.read())
        temp_path = temp_audio.name

    # -----------------------------
    # MOCK TRANSCRIPT (replace later with ASR)
    # -----------------------------
    transcript = "I want to practice Spanish, my native language is English."

    # -----------------------------
    # MOCK DURATION
    # -----------------------------
    audio_duration = 3.5

    # -----------------------------
    # FEATURE ENGINEERING
    # -----------------------------
    features = extract_features(transcript, audio_duration)

    # -----------------------------
    # REAL MODEL PREDICTION
    # -----------------------------
    if model:
        X = [[
            features["num_words"],
            features["speech_rate"],
            features["avg_word_length"]
        ]]
        pronunciation_score = float(model.predict(X)[0])
    else:
        pronunciation_score = 0.5  # fallback

    # -----------------------------
    # SAVE FEATURES
    # -----------------------------
    features["pronunciation_score"] = pronunciation_score
    save_features(features)

    # -----------------------------
    # CEFR MAPPING
    # -----------------------------
    if pronunciation_score > 0.8:
        cefr_level = "C1"
    elif pronunciation_score > 0.6:
        cefr_level = "B2"
    else:
        cefr_level = "B1"

    # -----------------------------
    # FEEDBACK
    # -----------------------------
    feedback = "AI-evaluated pronunciation is based on your speech features."

    os.remove(temp_path)

    return {
        "transcript": transcript,
        "pronunciation_score": pronunciation_score,
        "cefr_level": cefr_level,
        "feedback": feedback
    }