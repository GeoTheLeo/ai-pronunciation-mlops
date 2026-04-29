import pandas as pd

BASELINE_PATH = "mlops/data/baseline.csv"
CURRENT_PATH = "mlops/data/feature_store.csv"


def detect_drift(threshold=0.2):
    baseline = pd.read_csv(BASELINE_PATH)
    current = pd.read_csv(CURRENT_PATH)

    drift = {}

    for col in ["speech_rate", "avg_word_length"]:
        drift[col] = abs(baseline[col].mean() - current[col].mean())

    print("Drift:", drift)

    return any(v > threshold for v in drift.values())