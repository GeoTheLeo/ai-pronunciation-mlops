from mlops.monitoring.metrics import compute_metrics

# Baseline (can later come from training data)
REFERENCE = {"avg_score": 0.75}

# Threshold for drift detection
THRESHOLD = 0.15

def detect_drift():
    current = compute_metrics()

    drift = abs(current["avg_score"] - REFERENCE["avg_score"])

    return {
        "drift": drift,
        "drift_detected": drift > THRESHOLD,
        "current": current,
        "reference": REFERENCE
    }