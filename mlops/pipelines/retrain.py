from mlops.monitoring.drift import detect_drift
import subprocess


def retrain_if_needed():
    if detect_drift():
        print("Drift detected. Retraining...")
        subprocess.run(["python", "mlops/train/train_model.py"])
    else:
        print("No drift detected here, pal!")