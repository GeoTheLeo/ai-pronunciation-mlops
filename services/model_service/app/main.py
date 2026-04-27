from fastapi import FastAPI, UploadFile, File
import tempfile
import os

from app.model import PronunciationModel
from app.inference import score_pronunciation, generate_feedback

# Optional MLOps logging (keep if I've already wired it)
try:
    from mlops.monitoring.logger import log_inference
    LOGGING_ENABLED = True
except Exception:
    LOGGING_ENABLED = False


app = FastAPI()

# Load model once
model = PronunciationModel()


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(audio: UploadFile = File(...)):
    """
    Main inference endpoint:
    - accepts audio
    - transcribes
    - scores pronunciation
    - generates feedback
    """

    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Step 1 — transcription
        transcript = model.transcribe(tmp_path)

        # Step 2 — scoring
        result = score_pronunciation(transcript)

        # Step 3 — feedback
        feedback = generate_feedback(
            transcript,
            result["pronunciation_score"]
        )

        result["feedback"] = feedback

        # Step 4 — MLOps logging
        if LOGGING_ENABLED:
            log_inference(
                input_meta={"bytes": len(content)},
                output=result
            )

        return result

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)