from mlops.monitoring.drift import detect_drift
import subprocess


def retrain_if_needed():
    if detect_drift():
        print("Whoa! Drift detected → Retraining model...")
        subprocess.run(["python", "mlops/train/train_model.py"])
    else:
        print("Pow! No drift detected here, baby!")


if __name__ == "__main__":
    retrain_if_needed()