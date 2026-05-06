import streamlit as st
import tempfile
import os
import pandas as pd
import random
import sys
import joblib
import subprocess

# -----------------------------
# FIX IMPORT PATH
# -----------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), "services", "model_service"))

from app.llm_feedback import generate_feedback
from app.transcription import transcribe_audio

# -----------------------------
# PATHS
# -----------------------------
DATA_PATH = "feature_store.csv"
MODEL_PATH = "model.pkl"

# -----------------------------
# LOAD MODEL
# -----------------------------
def load_model():
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            print("Model load failed:", e)
            return None
    return None

model = load_model()

# -----------------------------
# RETRAIN TRIGGER
# -----------------------------
def should_retrain(threshold=20):
    if not os.path.exists(DATA_PATH):
        return False

    df = pd.read_csv(DATA_PATH)
    return len(df) % threshold == 0


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI Pronunciation Coach", layout="wide")

st.title("AI Pronunciation Coach (MLOps Demo)")

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
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("Upload your speech (.wav)", type=["wav"])

# -----------------------------
# MAIN PROCESSING
# -----------------------------
if uploaded_file is not None:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(uploaded_file.read())
        temp_path = temp_audio.name

    with st.spinner("Processing audio..."):
        try:
            transcript = transcribe_audio(temp_path)

            duration = 3.5
            features = extract_features(transcript, duration)

            # -----------------------------
            # MODEL-BASED SCORING
            # -----------------------------
            if model is not None:
                try:
                    score = model.predict([[
                        features["num_words"],
                        features["speech_rate"],
                        features["avg_word_length"]
                    ]])[0]

                    score = float(max(0, min(1, score)))

                except Exception as e:
                    print("Prediction failed:", e)
                    score = round(random.uniform(0.4, 0.9), 2)
            else:
                score = round(random.uniform(0.4, 0.9), 2)

            confidence = round(random.uniform(0.7, 0.95), 2)

            feedback, phonemes, practice = generate_feedback(transcript, score)

            features["pronunciation_score"] = score
            save_features(features)

            # -----------------------------
            # RETRAIN TRIGGER
            # -----------------------------
            if should_retrain():
                try:
                    subprocess.run(
                        ["python", "mlops/train/train_model.py"],
                        check=True
                    )
                    model = load_model()
                    print("Model retrained and reloaded")
                except Exception as e:
                    print("Retraining failed:", e)

        except Exception as e:
            st.error(f"Processing failed: {e}")
            os.remove(temp_path)
            st.stop()

    os.remove(temp_path)

    # -----------------------------
    # DISPLAY RESULTS
    # -----------------------------
    st.subheader("Transcript")
    st.write(transcript)

    col1, col2 = st.columns(2)
    col1.metric("Score", round(score, 2))
    col2.metric("Confidence", confidence)

    st.subheader("Feedback")
    st.write(feedback)

    st.subheader("Phoneme Feedback")
    for p in phonemes:
        st.write(f"- {p}")

    st.subheader("Practice Sentences")
    for s in practice:
        st.write(f"- {s}")

# -----------------------------
# ANALYTICS
# -----------------------------
st.divider()
st.subheader("Score Trend")

if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)

    if not df.empty:
        df = df.reset_index(drop=True)
        df["step"] = df.index + 1
        st.line_chart(df.set_index("step")["pronunciation_score"])
    else:
        st.write("No data yet.")
else:
    st.write("No data yet.")