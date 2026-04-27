import json
from datetime import datetime

LOG_FILE = "inference_logs.jsonl"

def log_inference(input_meta, output):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "input_length": input_meta.get("duration"),
        "transcript_length": len(output["transcript"]),
        "score": output["pronunciation_score"],
        "cefr": output["cefr_level"]
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")