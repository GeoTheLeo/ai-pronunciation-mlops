from fastapi import FastAPI, UploadFile, File
import tempfile
import os
import joblib
import subprocess

from mlops.features.feature_engineering import extract_features
from mlops.features.feature_store import save_features
from mlops.monitoring.drift import detect_drift

app = FastAPI()

# -----------------------------
# LOAD MODEL
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

    global model

    # -----------------------------
    # SAVE AUDIO
    # -----------------------------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(await audio.read())
        temp_path = temp_audio.name

    # -----------------------------
    # MOCK TRANSCRIPT
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
    # DRIFT DETECTION + RETRAIN
    # -----------------------------
    try:
        if detect_drift():
            print("⚠️ Drift detected → retraining model...")

            subprocess.run(["python", "-m", "mlops.train.train_model"])

            # Reload updated model
            if os.path.exists(MODEL_PATH):
                model = joblib.load(MODEL_PATH)

    except Exception as e:
        print("Drift check failed:", e)

    # -----------------------------
    # MODEL PREDICTION
    # -----------------------------
    if model:
        X = [[
            features["num_words"],
            features["speech_rate"],
            features["avg_word_length"]
        ]]
        pronunciation_score = float(model.predict(X)[0])
    else:
        pronunciation_score = 0.5

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
    feedback = "AI-evaluated pronunciation based on your speech feature - this time! Keep going!"

    # -----------------------------
    # CLEANUP
    # -----------------------------
    os.remove(temp_path)

    return {
        "transcript": transcript,
        "pronunciation_score": pronunciation_score,
        "cefr_level": cefr_level,
        "feedback": feedback
    }