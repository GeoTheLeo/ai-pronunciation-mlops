from fastapi import FastAPI, UploadFile, File
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .model import PronunciationModel
from .inference import score_pronunciation
from mlops.monitoring.logger import log_inference

app = FastAPI()

# Lazy-loaded model (do NOT initialize at startup)
model = None

# Thread pool to prevent blocking FastAPI event loop
executor = ThreadPoolExecutor(max_workers=1)


def run_inference(tmp_path: str, content: bytes):
    """
    This runs in a background thread to avoid blocking the API.
    """

    global model

    # Lazy load model on first request
    if model is None:
        print("🔄 Loading Whisper model (first request only)...")
        model = PronunciationModel()

    # Run transcription
    transcript = model.transcribe(tmp_path)

    # Score pronunciation
    result = score_pronunciation(transcript)

    # Log inference (MLOps monitoring)
    log_inference(
        input_meta={"audio_bytes": len(content)},
        output=result
    )

    return result


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(audio: UploadFile = File(...)):
    """
    Receives audio file and returns pronunciation analysis.
    """

    # Save uploaded audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Run blocking inference in thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        run_inference,
        tmp_path,
        content
    )

    return result