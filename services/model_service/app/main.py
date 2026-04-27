# =========================================================
# 🔧 finally! a PATH FIX (I think this ensures Docker can resolve /app as module root)
# =========================================================
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# =========================================================
# 🚀 CORE IMPORTS
# =========================================================
from fastapi import FastAPI, UploadFile, File
import tempfile

# =========================================================
# 🧠 ML COMPONENTS
# =========================================================
from .model import PronunciationModel
from .inference import score_pronunciation

# =========================================================
# 📊 MLOps COMPONENTS
# =========================================================
from mlops.monitoring.logger import log_inference
from mlops.monitoring.metrics import compute_metrics
from mlops.drift.drift_detector import detect_drift
from mlops.alerting.email_alert import send_alert

# =========================================================
# ⚙️ APP INITIALIZATION
# =========================================================
app = FastAPI()

# Load model once at startup (important for performance)
model = PronunciationModel()

# =========================================================
# ❤️ HEALTH CHECK
# =========================================================
@app.get("/")
def health():
    """
    Basic service health check
    """
    return {"status": "ok"}

# =========================================================
# 🎯 INFERENCE ENDPOINT
# =========================================================
@app.post("/predict")
async def predict(audio: UploadFile = File(...)):
    """
    Main inference endpoint:
    - receives audio file
    - runs transcription + scoring
    - logs result for monitoring
    """

    # Save uploaded audio temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 🧠 Run model inference
        transcript = model.transcribe(tmp_path)
        result = score_pronunciation(transcript)

        # 📊 Log inference (core MLOps hook)
        log_inference(
            input_meta={"duration": len(content)},
            output=result
        )

        return result

    finally:
        # 🧹 Cleanup temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# =========================================================
# 📈 METRICS ENDPOINT
# =========================================================
@app.get("/metrics")
def metrics():
    """
    Returns aggregated performance metrics
    (e.g., average pronunciation score)
    """
    return compute_metrics()

# =========================================================
# ⚠️ DRIFT DETECTION ENDPOINT
# =========================================================
@app.get("/drift")
def drift():
    """
    Detects model performance drift compared to baseline
    and triggers alert if threshold exceeded
    """
    result = detect_drift()

    # 🚨 Trigger alert if drift detected
    if result["drift_detected"]:
        send_alert()

    return result