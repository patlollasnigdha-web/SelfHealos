import os
import joblib
import numpy as np
from config.config import MODEL_FILE

def get_anomaly_confidence(decision_score, threshold=0.0):
    """
    Computes genuine model confidence percentage based on distance from the decision boundary.
    Uses logistic sigmoid scaling over the Isolation Forest decision function.
    """
    diff = threshold - decision_score
    # Standard sigmoid confidence scaling
    confidence_val = 1.0 / (1.0 + np.exp(-12.0 * diff))
    # Percentage between 50% and 99%
    confidence_pct = round(float(confidence_val * 100), 1)
    return min(99.0, max(50.0, confidence_pct))

class AnomalyDetector:
    def __init__(self, model_file=MODEL_FILE):
        self.model_file = model_file
        self.model = None
        self.scaler = None
        self.threshold = 0.0
        self.features_list = []
        self._load()

    def _load(self):
        if not os.path.exists(self.model_file):
            return
        try:
            bundle = joblib.load(self.model_file)
            self.model = bundle["model"]
            self.scaler = bundle.get("scaler")
            self.threshold = float(bundle.get("threshold", 0.0))
            self.features_list = bundle.get("features", [])
        except Exception:
            self.model = None

    @staticmethod
    def extract_features(snapshot):
        s = snapshot["system"]
        processes = snapshot.get("processes", [])
        top_cpu = max((p["cpu"] for p in processes), default=0.0)
        top_ram = max((p["memory"] for p in processes), default=0.0)
        return np.array([[s["cpu"], s["ram"], s["disk"], top_cpu, top_ram]])

    def predict(self, snapshot):
        if self.model is None:
            return {
                "available": False,
                "score": 0.0,
                "status": "MODEL_NOT_FOUND",
                "confidence": 0.0,
                "confidence_str": "N/A"
            }

        try:
            x = self.extract_features(snapshot)
            if self.scaler:
                x = self.scaler.transform(x)

            # IsolationForest decision function: < 0 implies anomaly
            decision = float(self.model.decision_function(x)[0])
            is_anomaly = decision < self.threshold
            status = "ANOMALY" if is_anomaly else "NORMAL"
            confidence = get_anomaly_confidence(decision, self.threshold) if is_anomaly else round((1.0 - (1.0 / (1.0 + np.exp(-12.0 * (decision - self.threshold))))) * 100, 1)

            return {
                "available": True,
                "score": round(decision, 4),
                "status": status,
                "confidence": confidence,
                "confidence_str": f"{confidence:.1f}%"
            }
        except Exception as e:
            return {
                "available": False,
                "score": 0.0,
                "status": "ERROR",
                "confidence": 0.0,
                "confidence_str": "0.0%",
                "error": str(e)
            }
