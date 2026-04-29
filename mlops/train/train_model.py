import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import os

DATA_PATH = "mlops/data/feature_store.csv"
MODEL_PATH = "mlops/models/model.pkl"

# -----------------------------
# LOAD DATA
# -----------------------------
if not os.path.exists(DATA_PATH):
    raise Exception("No feature store data found. Run the app first.")

df = pd.read_csv(DATA_PATH)

# -----------------------------
# FEATURES / TARGET
# -----------------------------
X = df[["num_words", "speech_rate", "avg_word_length"]]
y = df["pronunciation_score"]

# -----------------------------
# TRAIN TEST SPLIT
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# -----------------------------
# MLFLOW TRACKING
# -----------------------------
mlflow.set_experiment("pronunciation_model")

with mlflow.start_run():

    model = GradientBoostingRegressor()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)

    mlflow.log_metric("mse", mse)
    mlflow.sklearn.log_model(model, "model")

    os.makedirs("mlops/models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Model trained. MSE: {mse}")