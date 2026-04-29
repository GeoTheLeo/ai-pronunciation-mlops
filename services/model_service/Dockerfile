FROM python:3.10-slim

WORKDIR /app

# Finally!! FIXED PATHS (project root)
COPY services/model_service/app ./app
COPY services/model_service/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]