FROM python:3.10-slim

WORKDIR /app

# Copy app
COPY services/model_service/app ./app

# This better work!
COPY mlops ./mlops

COPY services/model_service/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]