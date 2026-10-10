import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from monitor.system_monitor import get_system_metrics, get_process_metrics, get_snapshot

class TestSystemMonitoring(unittest.TestCase):
    def test_system_metrics(self):
        metrics = get_system_metrics()
        self.assertIn("cpu", metrics)
        self.assertIn("ram", metrics)
        self.assertIn("disk", metrics)
        self.assertIsInstance(metrics["cpu"], (int, float))
        self.assertIsInstance(metrics["ram"], (int, float))
        self.assertIsInstance(metrics["disk"], (int, float))
        self.assertTrue(0.0 <= metrics["cpu"] <= 100.0)
        self.assertTrue(0.0 <= metrics["ram"] <= 100.0)
        self.assertTrue(0.0 <= metrics["disk"] <= 100.0)

    def test_process_metrics(self):
        processes = get_process_metrics(limit=5)
        self.assertIsInstance(processes, list)
        self.assertTrue(len(processes) > 0)
        first = processes[0]
        self.assertIn("pid", first)
        self.assertIn("name", first)
        self.assertIn("cpu", first)
        self.assertIn("memory", first)
        self.assertIsInstance(first["pid"], int)

    def test_snapshot_structure(self):
        snapshot = get_snapshot()
        self.assertIn("timestamp", snapshot)
        self.assertIn("system", snapshot)
        self.assertIn("processes", snapshot)

if __name__ == "__main__":
    unittest.main()
