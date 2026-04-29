import pandas as pd
import os

FEATURE_STORE_PATH = "mlops/data/feature_store.csv"


def save_features(features: dict):
    df = pd.DataFrame([features])

    if os.path.exists(FEATURE_STORE_PATH):
        df.to_csv(FEATURE_STORE_PATH, mode="a", header=False, index=False)
    else:
        df.to_csv(FEATURE_STORE_PATH, index=False)


def load_features():
    if os.path.exists(FEATURE_STORE_PATH):
        return pd.read_csv(FEATURE_STORE_PATH)
    return pd.DataFrame()