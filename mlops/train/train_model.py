import pandas as pd
import joblib
import os
from sklearn.ensemble import GradientBoostingRegressor

DATA_PATH = "services/model_service/feature_store.csv"
MODEL_PATH = "services/model_service/model.pkl"
MODEL_PATH = "model.pkl"


def create_training_data(df):
    """
    Create synthetic but meaningful labels from features
    """

    # normalize features
    df["speech_rate_norm"] = df["speech_rate"] / df["speech_rate"].max()
    df["word_len_norm"] = df["avg_word_length"] / df["avg_word_length"].max()

    # heuristic scoring (this is the key improvement)
    df["target"] = (
        0.6 * df["speech_rate_norm"] +
        0.4 * df["word_len_norm"]
    )

    return df


def train():
    if not os.path.exists(DATA_PATH):
        raise Exception("No feature store found.")

    df = pd.read_csv(DATA_PATH)

    if len(df) < 5:
        raise Exception("Not enough data to train.")

    df = create_training_data(df)

    X = df[["num_words", "speech_rate", "avg_word_length"]]
    y = df["target"]

    model = GradientBoostingRegressor()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    print("✅ Model trained successfully")


if __name__ == "__main__":
    train()