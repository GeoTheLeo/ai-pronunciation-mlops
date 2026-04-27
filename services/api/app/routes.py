from fastapi import APIRouter, UploadFile, File
import requests

router = APIRouter()

# This is the internal Docker network name
MODEL_URL = "http://model_service:8000/predict"

@router.post("/analyze")
async def analyze(audio: UploadFile = File(...)):
    response = requests.post(
        MODEL_URL,
        files={"audio": await audio.read()}
    )
    return response.json()