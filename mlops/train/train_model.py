import pandas as pd
import os
import joblib
from sklearn.linear_model import LinearRegression

DATA_PATH = "feature_store.csv"
MODEL_PATH = "model.pkl"


def train_model():
    if not os.path.exists(DATA_PATH):
        print("No data found")
        return

    df = pd.read_csv(DATA_PATH)

    if df.empty or len(df) < 10:
        print("Not enough data to train")
        return

    X = df[["num_words", "speech_rate", "avg_word_length"]]
    y = df["pronunciation_score"]

    model = LinearRegression()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print("Model trained and saved to model.pkl")


if __name__ == "__main__":
    train_model()