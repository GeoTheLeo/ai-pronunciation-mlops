from fastapi import FastAPI, UploadFile, File
import tempfile
import os
import joblib
import subprocess
import pandas as pd

app = FastAPI()

MODEL_PATH = "model.pkl"
DATA_PATH = "feature_store.csv"
BASELINE_PATH = "baseline.csv"


# -----------------------------
# LOAD MODEL
# -----------------------------
def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None


model = load_model()


# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
def extract_features(transcript, duration):
    words = transcript.split()
    num_words = len(words)
    speech_rate = num_words / duration if duration > 0 else 0
    avg_word_length = sum(len(w) for w in words) / num_words if num_words > 0 else 0

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
# DRIFT DETECTION
# -----------------------------
def detect_drift(threshold=0.5):
    if not os.path.exists(DATA_PATH) or not os.path.exists(BASELINE_PATH):
        return False

    baseline = pd.read_csv(BASELINE_PATH)
    current = pd.read_csv(DATA_PATH)

    for col in ["speech_rate", "avg_word_length"]:
        if abs(current[col].mean() - baseline[col].mean()) > threshold:
            return True

    return False


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
def health():
    return {"status": "model service running"}


# -----------------------------
# MAIN ENDPOINT
# -----------------------------
@app.post("/analyze")
async def analyze(audio: UploadFile = File(...)):
    global model

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(await audio.read())
        temp_path = temp_audio.name

    transcript = "I want to practice Spanish, my native language is English."
    duration = 3.5

    features = extract_features(transcript, duration)

    # Drift detection
    try:
        if detect_drift():
            print("Drift detected → retraining...")
            subprocess.run(["python", "train_model.py"])

            if os.path.exists(MODEL_PATH):
                model = joblib.load(MODEL_PATH)
    except Exception as e:
        print("Drift error:", e)

    # Prediction
    if model:
        X = [[
            features["num_words"],
            features["speech_rate"],
            features["avg_word_length"]
        ]]
        score = float(model.predict(X)[0])
    else:
        score = 0.5

    features["pronunciation_score"] = score
    save_features(features)

    os.remove(temp_path)

    return {
        "transcript": transcript,
        "pronunciation_score": score,
        "cefr_level": "B2",
        "feedback": "AI-evaluated pronunciation"
    }