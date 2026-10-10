import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.anomaly_detector import AnomalyDetector
from monitor.system_monitor import get_snapshot

def predict_current_state():
    detector = AnomalyDetector()
    snapshot = get_snapshot()
    result = detector.predict(snapshot)
    print("=" * 60)
    print("SelfHealOS — Real-Time ML Anomaly Prediction")
    print("=" * 60)
    print(f"Timestamp    : {snapshot['timestamp']}")
    print(f"System CPU   : {snapshot['system']['cpu']}%")
    print(f"System RAM   : {snapshot['system']['ram']}%")
    print(f"System Disk  : {snapshot['system']['disk']}%")
    print(f"Model Status : {result['status']}")
    print(f"Score        : {result['score']}")
    print(f"Confidence   : {result['confidence_str']}")
    print("=" * 60)
    return result

if __name__ == "__main__":
    predict_current_state()
