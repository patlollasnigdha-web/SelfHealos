import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from detector.fault_detector import FaultDetector
from diagnosis.diagnosis_engine import diagnose

class TestFaultDetection(unittest.TestCase):
    def setUp(self):
        self.detector = FaultDetector(confirmations=3)

    def test_confirmation_mechanism(self):
        faulty_proc = {"pid": 99999, "name": "faulty_sim", "cpu": 95.0, "memory": 5.0}
        snapshot = {
            "timestamp": "2026-09-27 12:00:00",
            "system": {"cpu": 90.0, "ram": 50.0, "disk": 40.0},
            "processes": [faulty_proc]
        }

        # Reading 1
        conf1 = self.detector.update(snapshot)
        self.assertEqual(len(conf1), 0)
        self.assertEqual(self.detector.persistence[99999], 1)

        # Reading 2
        conf2 = self.detector.update(snapshot)
        self.assertEqual(len(conf2), 0)
        self.assertEqual(self.detector.persistence[99999], 2)

        # Reading 3 -> Confirmed!
        conf3 = self.detector.update(snapshot)
        self.assertEqual(len(conf3), 1)
        self.assertEqual(conf3[0]["pid"], 99999)

    def test_diagnosis_cpu_overload(self):
        proc = {"pid": 99999, "name": "stress_cpu", "cpu": 98.0, "memory": 2.0}
        sys_metrics = {"cpu": 92.0, "ram": 50.0, "disk": 40.0}
        diag = diagnose(proc, sys_metrics)
        self.assertEqual(diag["fault_type"], "CPU_OVERLOAD")
        self.assertEqual(diag["severity"], "CRITICAL")
        self.assertEqual(diag["action_recommended"], "RESTART")

    def test_diagnosis_memory_overload(self):
        proc = {"pid": 88888, "name": "mem_hog", "cpu": 5.0, "memory": 85.0}
        sys_metrics = {"cpu": 15.0, "ram": 92.0, "disk": 40.0}
        diag = diagnose(proc, sys_metrics)
        self.assertEqual(diag["fault_type"], "MEMORY_OVERLOAD")
        self.assertEqual(diag["severity"], "CRITICAL")

if __name__ == "__main__":
    unittest.main()
