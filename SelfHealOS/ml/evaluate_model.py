import json
import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.config import (
    DATA_FILE, MODEL_FILE, EVAL_FILE,
    PROCESS_CPU_THRESHOLD, PROCESS_RAM_THRESHOLD,
    CPU_CRITICAL_THRESHOLD
)

def evaluate():
    if not os.path.exists(MODEL_FILE):
        print(f"Model file not found at {MODEL_FILE}. Please train the model first.")
        return None

    bundle = joblib.load(MODEL_FILE)
    model = bundle["model"]
    scaler = bundle.get("scaler")
    features_list = bundle.get("features", [])

    if not os.path.exists(DATA_FILE):
        print(f"Data file not found at {DATA_FILE}.")
        return None

    df = pd.read_csv(DATA_FILE)
    groups = df.groupby("timestamp")
    features = []
    y_true = []

    for _, group in groups:
        system_cpu = float(group["system_cpu"].iloc[0])
        system_ram = float(group["system_ram"].iloc[0])
        disk = float(group["disk_usage"].iloc[0])
        top_cpu = float(group["process_cpu"].max())
        top_ram = float(group["process_ram"].max())

        features.append([system_cpu, system_ram, disk, top_cpu, top_ram])
        is_anomaly = (
            top_cpu >= PROCESS_CPU_THRESHOLD or
            top_ram >= PROCESS_RAM_THRESHOLD or
            system_cpu >= CPU_CRITICAL_THRESHOLD
        )
        y_true.append(1 if is_anomaly else 0)

    # Augment if small
    for _, row in df.iterrows():
        features.append([
            float(row["system_cpu"]),
            float(row["system_ram"]),
            float(row["disk_usage"]),
            float(row["process_cpu"]),
            float(row["process_ram"])
        ])
        is_anomaly = (
            float(row["process_cpu"]) >= PROCESS_CPU_THRESHOLD or
            float(row["process_ram"]) >= PROCESS_RAM_THRESHOLD or
            float(row["system_cpu"]) >= CPU_CRITICAL_THRESHOLD
        )
        y_true.append(1 if is_anomaly else 0)

    X = np.array(features)
    y_true = np.array(y_true)

    if scaler:
        X_scaled = scaler.transform(X)
    else:
        X_scaled = X

    raw_preds = model.predict(X_scaled)
    y_pred = np.where(raw_preds == -1, 1, 0)
    decision_scores = model.decision_function(X_scaled)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    cm = confusion_matrix(y_true, y_pred).tolist()

    report = {
        "samples_evaluated": len(X),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm,
        "anomalies_detected": int(np.sum(y_pred)),
        "normal_detected": int(len(y_pred) - np.sum(y_pred)),
        "mean_anomaly_score": round(float(np.mean(decision_scores)), 4)
    }

    with open(EVAL_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("=" * 65)
    print("SelfHealOS — ML MODEL INDEPENDENT EVALUATION")
    print("=" * 65)
    print(f"Evaluated Samples : {len(X)}")
    print(f"Accuracy          : {acc * 100:.2f}%")
    print(f"Precision         : {prec * 100:.2f}%")
    print(f"Recall            : {rec * 100:.2f}%")
    print(f"F1-Score          : {f1 * 100:.2f}%")
    print(f"Confusion Matrix  : {cm}")
    print("=" * 65)
    return report

if __name__ == "__main__":
    evaluate()
