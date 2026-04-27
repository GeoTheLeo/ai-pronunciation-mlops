import json
import os
from datetime import datetime

LOG_FILE = "/app/logs/inference_logs.jsonl"

def log_inference(input_meta, output):
    os.makedirs("/app/logs", exist_ok=True)

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "score": output.get("pronunciation_score"),
        "cefr": output.get("cefr_level")
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")