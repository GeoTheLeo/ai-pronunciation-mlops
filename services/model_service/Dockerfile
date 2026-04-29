FROM python:3.10-slim

WORKDIR /app

# Copy app code
COPY app/ ./app

# 🔥 COPY MLOPS CODE INTO CONTAINER
COPY ../../mlops ./mlops

# Copy requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]