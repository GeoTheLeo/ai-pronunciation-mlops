from fastapi import FastAPI, UploadFile, File
import requests

app = FastAPI()

MODEL_SERVICE_URL = "http://model_service:8000/analyze"


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(audio: UploadFile = File(...)):
    """
    API layer:
    - receives request
    - forwards to model_service
    - returns response
    """

    files = {
        "audio": (audio.filename, await audio.read(), audio.content_type)
    }

    response = requests.post(MODEL_SERVICE_URL, files=files)

    return response.json()