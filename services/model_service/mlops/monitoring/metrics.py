import json
import os

LOG_FILE = "/app/logs/inference_logs.jsonl"

def compute_metrics():
    if not os.path.exists(LOG_FILE):
        return {"avg_score": 0, "num_samples": 0}

    scores = []

    with open(LOG_FILE, "r") as f:
        for line in f:
            record = json.loads(line)
            scores.append(record["score"])

    if not scores:
        return {"avg_score": 0, "num_samples": 0}

    return {
        "avg_score": sum(scores) / len(scores),
        "num_samples": len(scores)
    }