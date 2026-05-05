# -----------------------------
# BASE IMAGE
# -----------------------------
FROM python:3.11-slim

# -----------------------------
# SYSTEM DEPENDENCIES
# -----------------------------
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# -----------------------------
# WORKDIR
# -----------------------------
WORKDIR /app

# -----------------------------
# COPY FILES
# -----------------------------
COPY . .

# -----------------------------
# INSTALL DEPENDENCIES
# -----------------------------
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# RENDER PORT HANDLING
# -----------------------------
ENV PORT=8000

# -----------------------------
# START SERVER (RENDER SAFE)
# -----------------------------
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]