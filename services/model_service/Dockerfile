FROM python:3.10-slim

WORKDIR /app

# system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 👇 THIS IS THE FIX
COPY . .

# ensure logs dir exists
RUN mkdir -p /app/logs

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]