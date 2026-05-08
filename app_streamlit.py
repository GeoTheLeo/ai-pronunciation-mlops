import streamlit as st
import requests
import tempfile
import os
import pandas as pd
import numpy as np
from scipy.io import wavfile
from streamlit_mic_recorder import mic_recorder

# -----------------------------
# API CONFIG
# -----------------------------
API_URL = "https://ai-pronunciation-mlops.onrender.com/analyze"

PRACTICE_URL = "https://ai-pronunciation-mlops.onrender.com/generate-practice"

DATA_PATH = "feature_store.csv"

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Pronunciation Coach",
    layout="wide"
)

st.title("AI Pronunciation Coach")

# -----------------------------
# LANGUAGE SELECTION
# -----------------------------
target_language = st.selectbox(
    "Target Language",
    [
        "German",
        "French",
        "Spanish",
        "Portuguese",
        "Russian",
        "Japanese",
        "Chinese"
    ]
)

native_language = st.selectbox(
    "Native Language",
    [
        "English"
    ]
)

# -----------------------------
# GENERATE PRACTICE
# -----------------------------
if st.button("Generate Practice Sentences"):

    try:

        response = requests.post(
            PRACTICE_URL,
            json={
                "target_language": target_language,
                "native_language": native_language
            }
        )

        if response.status_code == 200:

            data = response.json()

            if "sentences" in data:

                st.session_state["practice"] = data["sentences"]

            else:

                st.error(f"Unexpected API response: {data}")

        else:

            st.error(f"API Error: {response.text}")

    except Exception as e:

        st.error(f"Connection failed: {e}")

# -----------------------------
# AUDIO PROCESSING
# -----------------------------
def process_audio(file_bytes):

    # -----------------------------
    # SAVE TEMP AUDIO
    # -----------------------------
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_audio:

        temp_audio.write(file_bytes)

        temp_path = temp_audio.name

    # -----------------------------
    # PLAYBACK
    # -----------------------------
    st.audio(file_bytes, format="audio/wav")

    # -----------------------------
    # WAVEFORM
    # -----------------------------
    try:

        try:

            rate, data = wavfile.read(temp_path)

            if len(data.shape) > 1:
                data = data[:, 0]

            signal = data

        except Exception:

            signal = np.frombuffer(
                file_bytes,
                dtype=np.int16
            )

        st.subheader("Audio Waveform")

        st.line_chart(signal[:2000])

    except Exception as e:

        st.warning(f"Waveform unavailable: {e}")

    # -----------------------------
    # SEND TO BACKEND
    # -----------------------------
    try:

        with open(temp_path, "rb") as f:

            response = requests.post(
                API_URL,
                files={"audio": f}
            )

        if response.status_code != 200:

            st.error(f"API Error: {response.text}")

            return

        result = response.json()

        # -----------------------------
        # DISPLAY RESULTS
        # -----------------------------
        st.subheader("Transcript")

        st.write(result["transcript"])

        col1, col2 = st.columns(2)

        col1.metric(
            "Score",
            round(result["score"], 2)
        )

        col2.metric(
            "Confidence",
            "—"
        )

        st.subheader("Feedback")

        st.write(result["feedback"])

        st.subheader("Phoneme Feedback")

        for p in result["phonemes"]:

            st.write(f"- {p}")

    except Exception as e:

        st.error(f"Processing failed: {e}")

    finally:

        try:
            os.remove(temp_path)
        except:
            pass

# -----------------------------
# PRACTICE SENTENCES
# -----------------------------
if "practice" in st.session_state:

    st.divider()

    st.subheader("Practice Sentences")

    for i, item in enumerate(
        st.session_state["practice"]
    ):

        st.markdown(
            f"### {i+1}. {item['text']}"
        )

        st.caption(
            f"Pronunciation: {item['phonetic']}"
        )

        audio = mic_recorder(
            start_prompt=f"Record Sentence {i+1}",
            stop_prompt="Stop Recording",
            key=f"practice_{i}"
        )

        if audio is not None:

            process_audio(audio["bytes"])

# -----------------------------
# FREE PRACTICE
# -----------------------------
st.divider()

st.subheader("Try Your Own Sentence")

st.caption(
    "Speak freely to test pronunciation"
)

audio = mic_recorder(
    start_prompt="Start Recording",
    stop_prompt="Stop Recording",
    key="free_practice"
)

if audio is not None:

    process_audio(audio["bytes"])

# -----------------------------
# FILE UPLOAD
# -----------------------------
st.divider()

st.subheader("Upload Audio Files")

uploaded_files = st.file_uploader(
    "Upload .wav files",
    type=["wav"],
    accept_multiple_files=True
)

if uploaded_files:

    for file in uploaded_files:

        st.write(f"Processing: {file.name}")

        process_audio(file.read())

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

        st.line_chart(
            df.set_index("step")[
                "pronunciation_score"
            ]
        )

    else:

        st.write("No data yet.")

else:

    st.write("No data yet.")