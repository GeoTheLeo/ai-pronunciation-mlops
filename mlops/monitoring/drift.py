import pandas as pd

BASELINE_PATH = "mlops/data/baseline.csv"
CURRENT_PATH = "mlops/data/feature_store.csv"


def detect_drift(threshold=0.5):
    baseline = pd.read_csv(BASELINE_PATH)
    current = pd.read_csv(CURRENT_PATH)

    drift_scores = {}

    for col in ["speech_rate", "avg_word_length"]:
        baseline_mean = baseline[col].mean()
        current_mean = current[col].mean()

        drift = abs(current_mean - baseline_mean)
        drift_scores[col] = drift

    print("Drift scores:", drift_scores)

    return any(v > threshold for v in drift_scores.values())