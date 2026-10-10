import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from recovery.recovery_actions import is_protected_process, restart_controlled_process, safe_disk_cleanup
from recovery.recovery_verifier import RecoveryVerifier

class TestRecoveryEngine(unittest.TestCase):
    def test_protected_process_rejection(self):
        # Protected OS processes must be blocked
        self.assertTrue(is_protected_process("explorer.exe", 100))
        self.assertTrue(is_protected_process("csrss.exe", 200))
        self.assertTrue(is_protected_process("System", 4))

        res = restart_controlled_process(4, "System")
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "SAFE_STOP")

    def test_unmanaged_process_rejection(self):
        # Unmanaged non-controlled processes must be safely stopped from arbitrary restarts
        res = restart_controlled_process(999999, "unknown_external.exe")
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "SAFE_STOP")

    def test_safe_disk_cleanup(self):
        res = safe_disk_cleanup()
        self.assertTrue(res["success"])
        self.assertIn("mb_freed", res)

if __name__ == "__main__":
    unittest.main()
