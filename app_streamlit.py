import streamlit as st
import requests
import tempfile
import os
import pandas as pd
import numpy as np
from scipy.io import wavfile
from streamlit_mic_recorder import mic_recorder

API_URL = "https://ai-pronunciation-mlops.onrender.com/analyze"
PRACTICE_URL = "https://ai-pronunciation-mlops.onrender.com/generate-practice"
DATA_PATH = "feature_store.csv"

st.set_page_config(page_title="AI Pronunciation Coach", layout="wide")
st.title("AI Pronunciation Coach")

# -----------------------------
# LANGUAGE SETUP
# -----------------------------
target_language = st.selectbox(
    "Target Language",
    [
        "German",
        "English",
        "Spanish",
        "French",
        "Portuguese",
        "Russian",
        "Japanese",
        "Chinese"
    ]
)

native_language = st.selectbox(
    "Native Language",
    ["English"]
)

if st.button("Generate Practice"):
    response = requests.post(
        PRACTICE_URL,
        json={
            "target_language": target_language,
            "native_language": native_language
        }
    )
    st.session_state["practice"] = response.json()["sentences"]

# -----------------------------
# AUDIO PROCESSING
# -----------------------------
def process_audio(file_bytes):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(file_bytes)
        path = f.name

    # PLAYBACK
    st.audio(file_bytes, format="audio/wav")

    # WAVEFORM
    try:
        rate, data = wavfile.read(path)
        if len(data.shape) > 1:
            data = data[:, 0]
        st.line_chart(data[:2000])
    except:
        pass

    # SEND TO BACKEND
    with open(path, "rb") as f:
        res = requests.post(API_URL, files={"audio": f})

    result = res.json()

    st.write("Transcript:", result["transcript"])
    st.write("Score:", result["score"])
    st.write("Feedback:", result["feedback"])

    for p in result["phonemes"]:
        st.write("-", p)

    os.remove(path)

# -----------------------------
# PRACTICE FLOW
# -----------------------------
if "practice" in st.session_state:

    for i, item in enumerate(st.session_state["practice"]):
        st.write(f"{i+1}. {item['text']}")
        st.caption(item["phonetic"])

        audio = mic_recorder(key=f"p{i}")

        if audio:
            process_audio(audio["bytes"])

# -----------------------------
# FREE MIC
# -----------------------------
st.subheader("Try your own sentence")

audio = mic_recorder(key="free")

if audio:
    process_audio(audio["bytes"])

# -----------------------------
# ANALYTICS
# -----------------------------
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    if not df.empty:
        df["step"] = range(len(df))
        st.line_chart(df.set_index("step")["pronunciation_score"])