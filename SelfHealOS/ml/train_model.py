import csv
import json
import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.config import (
    DATA_FILE, MODEL_DIR, MODEL_FILE, EVAL_FILE,
    PROCESS_CPU_THRESHOLD, PROCESS_RAM_THRESHOLD,
    CPU_CRITICAL_THRESHOLD
)

FEATURE_NAMES = ["system_cpu", "system_ram", "disk_usage", "top_process_cpu", "top_process_ram"]

def load_and_validate_data():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Dataset not found at: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)
    required_cols = [
        "timestamp", "system_cpu", "system_ram", "disk_usage",
        "process_name", "pid", "process_cpu", "process_ram"
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in dataset.")

    df = df.dropna(subset=required_cols)
    if len(df) < 5:
        raise ValueError(f"Dataset has too few records ({len(df)}). Need at least 5 records.")

    return df

def extract_snapshot_features(df):
    """
    Extract snapshot-level features:
    [system_cpu, system_ram, disk_usage, top_process_cpu, top_process_ram]
    Ground-truth anomalies defined by significant CPU/RAM process anomalies or critical CPU overload.
    """
    groups = df.groupby("timestamp")
    features = []
    ground_truth_labels = []

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
        ground_truth_labels.append(1 if is_anomaly else 0)

    # Augment with individual process records
    for _, row in df.iterrows():
        s_cpu = float(row["system_cpu"])
        s_ram = float(row["system_ram"])
        s_disk = float(row["disk_usage"])
        p_cpu = float(row["process_cpu"])
        p_ram = float(row["process_ram"])
        features.append([s_cpu, s_ram, s_disk, p_cpu, p_ram])
        is_anomaly = (
            p_cpu >= PROCESS_CPU_THRESHOLD or
            p_ram >= PROCESS_RAM_THRESHOLD or
            s_cpu >= CPU_CRITICAL_THRESHOLD
        )
        ground_truth_labels.append(1 if is_anomaly else 0)

    return np.array(features), np.array(ground_truth_labels)

def train_and_evaluate():
    print("=" * 70)
    print("SelfHealOS — ML MODEL TRAINING & EVALUATION")
    print("=" * 70)

    df = load_and_validate_data()
    print(f"Loaded {len(df)} telemetry rows from {DATA_FILE}")

    X, y_true = extract_snapshot_features(df)
    anomaly_ratio = float(np.mean(y_true))
    print(f"Extracted {len(X)} feature vectors with {X.shape[1]} features:")
    for f in FEATURE_NAMES:
        print(f"  - {f}")
    print(f"Dataset Anomaly Distribution: {int(np.sum(y_true))} anomalies / {len(y_true)} total ({anomaly_ratio*100:.1f}%)")

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train Isolation Forest with contamination matching dataset anomaly proportion
    contamination_rate = max(0.05, min(0.35, anomaly_ratio if anomaly_ratio > 0 else 0.15))
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination_rate,
        random_state=42
    )
    model.fit(X_scaled)

    # Predict: -1 for anomaly, 1 for normal
    raw_preds = model.predict(X_scaled)
    y_pred = np.where(raw_preds == -1, 1, 0)
    decision_scores = model.decision_function(X_scaled)

    # Calculate actual ML evaluation metrics
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    cm = confusion_matrix(y_true, y_pred).tolist()

    eval_results = {
        "samples": len(X),
        "features": FEATURE_NAMES,
        "contamination": round(contamination_rate, 4),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm,
        "true_positives": cm[1][1] if len(cm) > 1 else 0,
        "false_positives": cm[0][1] if len(cm) > 1 else 0,
        "true_negatives": cm[0][0] if len(cm) > 0 else 0,
        "false_negatives": cm[1][0] if len(cm) > 1 else 0,
        "anomaly_count": int(np.sum(y_pred)),
        "normal_count": int(len(y_pred) - np.sum(y_pred)),
        "mean_score": round(float(np.mean(decision_scores)), 4),
        "min_score": round(float(np.min(decision_scores)), 4),
        "max_score": round(float(np.max(decision_scores)), 4),
    }

    # Save model and artifacts
    os.makedirs(MODEL_DIR, exist_ok=True)
    bundle = {
        "model": model,
        "scaler": scaler,
        "threshold": 0.0,
        "features": FEATURE_NAMES,
        "metrics": eval_results,
    }
    joblib.dump(bundle, MODEL_FILE)
    print(f"\nTrained model successfully saved to: {MODEL_FILE}")

    with open(EVAL_FILE, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=4)
    print(f"Evaluation metrics saved to: {EVAL_FILE}")

    print("\nMODEL EVALUATION RESULTS:")
    print("-" * 50)
    print(f"Accuracy  : {acc * 100:.2f}%")
    print(f"Precision : {prec * 100:.2f}%")
    print(f"Recall    : {rec * 100:.2f}%")
    print(f"F1-Score  : {f1 * 100:.2f}%")
    print(f"Confusion Matrix (TN, FP, FN, TP): {cm}")
    print("=" * 70)

    return eval_results

if __name__ == "__main__":
    train_and_evaluate()
