from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# ✅ CORS (THIS WAS MISSING)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_SERVICE_URL = "http://model_service:8000/analyze"


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(audio: UploadFile = File(...)):
    files = {
        "audio": (audio.filename, await audio.read(), audio.content_type)
    }

    response = requests.post(MODEL_SERVICE_URL, files=files)

    return response.json()