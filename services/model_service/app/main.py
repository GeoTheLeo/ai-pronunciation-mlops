from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import tempfile
import os
import pandas as pd

from app.transcription import transcribe_audio
from app.llm_feedback import generate_feedback
from app.scoring import get_audio_duration, compute_similarity_score

load_dotenv()

# -----------------------------
# APP INIT
# -----------------------------
app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "../../../")
)

DATA_PATH = os.path.join(
    ROOT_DIR,
    "feature_store.csv"
)

# -----------------------------
# REQUEST MODEL
# -----------------------------
class PracticeRequest(BaseModel):
    target_language: str
    native_language: str

# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
def extract_features(transcript, duration):

    words = transcript.split()

    num_words = len(words)

    speech_rate = (
        num_words / duration
        if duration > 0 else 0
    )

    avg_word_length = (
        sum(len(w) for w in words) / num_words
        if num_words > 0 else 0
    )

    return {
        "num_words": num_words,
        "speech_rate": speech_rate,
        "avg_word_length": avg_word_length,
        "duration_seconds": duration,
    }

# -----------------------------
# SAVE FEATURES
# -----------------------------
def save_features(features):

    df = pd.DataFrame([features])

    if os.path.exists(DATA_PATH):

        df.to_csv(
            DATA_PATH,
            mode="a",
            header=False,
            index=False
        )

    else:

        df.to_csv(
            DATA_PATH,
            index=False
        )

# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def root():

    return {
        "message": "AI Pronunciation Coach API Running"
    }

# -----------------------------
# ANALYZE AUDIO
# -----------------------------
@app.post("/analyze")
async def analyze_audio(
    audio: UploadFile = File(...),
    target_text: str = Form(None),
):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_audio:

        temp_audio.write(await audio.read())

        temp_path = temp_audio.name

    try:

        # -----------------------------
        # TRANSCRIPTION
        # -----------------------------
        transcript = transcribe_audio(
            temp_path
        )

        # -----------------------------
        # REAL AUDIO DURATION
        # -----------------------------
        duration = get_audio_duration(temp_path)

        # -----------------------------
        # FEATURES (logged for analytics)
        # -----------------------------
        features = extract_features(
            transcript,
            duration
        )

        # -----------------------------
        # SCORING: text-similarity against the target phrase.
        # None when there's no target (free/open practice) - there's nothing to
        # score pronunciation accuracy against in that case.
        # -----------------------------
        score = compute_similarity_score(
            transcript,
            target_text
        )

        # -----------------------------
        # AI FEEDBACK (real LLM call, grounded in the transcript/target/score)
        # -----------------------------
        feedback, phonemes, practice = generate_feedback(
            transcript,
            target_text=target_text,
            score=score,
        )

        # -----------------------------
        # SAVE ANALYTICS (only when we have a real score to trend)
        # -----------------------------
        if score is not None:

            features["pronunciation_score"] = score

            save_features(features)

        # -----------------------------
        # RESPONSE
        # -----------------------------
        return {
            "transcript": transcript,
            "score": score,
            "feedback": feedback,
            "phonemes": phonemes,
            "practice": practice
        }

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)

# -----------------------------
# PRACTICE GENERATION
# -----------------------------
@app.post("/generate-practice")
def generate_practice(
    req: PracticeRequest
):

    practice_bank = {

        "German": [
            {
                "text": "Guten Morgen, wie geht es Ihnen?",
                "phonetic": "GOO-ten MOR-gen vee GAYT ess EE-nen"
            },
            {
                "text": "Ich lerne Deutsch jeden Tag.",
                "phonetic": "ikh LEHR-neh doytch YAY-den tahk"
            },
            {
                "text": "Können Sie das bitte wiederholen?",
                "phonetic": "KUH-nen zee dahs BIT-te VEE-der-ho-len"
            }
        ],

        "French": [
            {
                "text": "Bonjour, comment allez-vous ?",
                "phonetic": "bohn-ZHOOR koh-mahn tah-lay VOO"
            },
            {
                "text": "Je voudrais pratiquer le français.",
                "phonetic": "zhuh voo-DRAY pra-tee-KAY luh frahn-SAY"
            },
            {
                "text": "Pouvez-vous parler plus lentement ?",
                "phonetic": "poo-vay VOO par-LAY ploo lahn-te-MAHN"
            }
        ],

        "Spanish": [
            {
                "text": "Hola, ¿cómo estás?",
                "phonetic": "OH-lah KOH-moh es-TAHS"
            },
            {
                "text": "Estoy aprendiendo español.",
                "phonetic": "es-TOY ah-pren-dee-EN-doh es-pan-YOL"
            },
            {
                "text": "¿Puede repetir eso por favor?",
                "phonetic": "PWEH-deh reh-peh-TEER EH-soh por fah-VOR"
            }
        ],

        "Portuguese": [
            {
                "text": "Olá, tudo bem?",
                "phonetic": "oh-LAH TOO-doo BENG"
            },
            {
                "text": "Estou aprendendo português.",
                "phonetic": "es-TOH ah-pren-DEN-do por-too-GAYS"
            },
            {
                "text": "Você pode repetir isso?",
                "phonetic": "vo-SEH PO-jee reh-peh-CHEER EE-soo"
            }
        ],

        "Russian": [
            {
                "text": "Здравствуйте, как ваши дела?",
                "phonetic": "ZDRAV-stvooy-tye kak vah-shee dye-LAH"
            },
            {
                "text": "Я изучаю русский язык.",
                "phonetic": "ya ee-zoo-CHAH-yu ROOS-kee ya-ZYK"
            },
            {
                "text": "Можете повторить это?",
                "phonetic": "MO-zhe-tye pafta-REET EH-ta"
            }
        ],

        "Japanese": [
            {
                "text": "こんにちは、お元気ですか？",
                "phonetic": "kon-nee-chee-wah oh-gen-kee dess-kah"
            },
            {
                "text": "日本語を勉強しています。",
                "phonetic": "nee-hon-go oh ben-kyoh shee-teh ee-mahs"
            },
            {
                "text": "もう一度お願いします。",
                "phonetic": "moh ee-chee-doh oh-neh-guy-shee-mahs"
            }
        ],

        "Chinese": [
            {
                "text": "你好，你今天怎么样？",
                "phonetic": "nee how nee jin tian zen me yang"
            },
            {
                "text": "我正在学习中文。",
                "phonetic": "woh jeng dzai shweh-shee jong-wen"
            },
            {
                "text": "请再说一遍。",
                "phonetic": "ching dzai shwoh ee byan"
            }
        ]
    }

    sentences = practice_bank.get(
        req.target_language.strip(),
        practice_bank["German"]
    )

    return {
        "sentences": sentences
    }

# -----------------------------
# ANALYTICS ENDPOINT
# -----------------------------
@app.get("/analytics")
def analytics():

    if not os.path.exists(DATA_PATH):

        return {
            "scores": []
        }

    try:

        df = pd.read_csv(DATA_PATH)

        if "pronunciation_score" not in df.columns:

            return {
                "scores": []
            }

        scores = (
            df["pronunciation_score"]
            .dropna()
            .tolist()
        )

        return {
            "scores": scores
        }

    except Exception as e:

        return {
            "scores": [],
            "error": str(e)
        }
