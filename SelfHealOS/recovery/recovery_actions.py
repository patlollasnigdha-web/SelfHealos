import os
import sys
import glob
import time
import subprocess
import psutil
from config.config import (
    BASE_DIR, TEST_SCRIPT, PROTECTED_PROCESSES, LOGS_DIR
)

def is_protected_process(name, pid=None):
    """
    Checks if a process is a critical system process that must NEVER be killed or restarted.
    """
    if not name:
        return True
    name_clean = name.lower().strip()
    if name_clean in PROTECTED_PROCESSES:
        return True
    for p in PROTECTED_PROCESSES:
        if p in name_clean:
            return True
    if pid is not None and pid <= 4:
        return True
    return False

def is_controlled_test_process(pid):
    """
    Checks if the PID belongs to a SelfHealOS controlled test/stress process.
    """
    try:
        p = psutil.Process(pid)
        cmdline = " ".join(p.cmdline()).lower()
        test_py = "test_process.py"
        stress_py = "stress_test.py"
        return (test_py in cmdline or stress_py in cmdline or "selfhealos" in cmdline)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def restart_controlled_process(pid, name):
    """
    Safely terminates an abnormal controlled test process and relaunches it in recovered mode.
    """
    if is_protected_process(name, pid):
        return {
            "success": False,
            "status": "SAFE_STOP",
            "message": f"Refused to restart protected OS process: {name} (PID {pid})."
        }

    if not is_controlled_test_process(pid):
        return {
            "success": False,
            "status": "SAFE_STOP",
            "message": f"Automatic restart refused: '{name}' (PID {pid}) is an external/unmanaged process."
        }

    try:
        old_proc = psutil.Process(pid)
        env = os.environ.copy()
        env["SELFHEAL_RECOVERED"] = "1"

        # Spawn recovered process
        new_proc = subprocess.Popen(
            [sys.executable, TEST_SCRIPT],
            cwd=BASE_DIR,
            env=env,
            creationflags=0,
        )

        # Terminate fault-inducing process
        try:
            old_proc.kill()
            old_proc.wait(timeout=2)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            pass

        time.sleep(0.3)
        if psutil.pid_exists(new_proc.pid):
            return {
                "success": True,
                "status": "SUCCESS",
                "new_pid": new_proc.pid,
                "old_pid": pid,
                "message": f"Controlled process safely restarted: PID {pid} -> PID {new_proc.pid} in recovered state."
            }
        else:
            return {
                "success": False,
                "status": "FAILED",
                "new_pid": None,
                "message": "Process restart attempted but recovered process was not detected."
            }
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return {"success": False, "status": "FAILED", "message": f"Process error: {str(e)}"}
    except Exception as e:
        return {"success": False, "status": "FAILED", "message": f"Unexpected error during restart: {str(e)}"}

def safe_disk_cleanup():
    """
    Performs safe cleanup of temporary cache/test files generated in the workspace.
    NEVER deletes user files outside safe directories.
    """
    cleaned_bytes = 0
    cleaned_files = 0

    # 1. Clean temporary test artifacts if present
    temp_test_dir = os.path.join(BASE_DIR, "tests", "temp_stress_files")
    if os.path.exists(temp_test_dir):
        for fpath in glob.glob(os.path.join(temp_test_dir, "*.*")):
            try:
                sz = os.path.getsize(fpath)
                os.remove(fpath)
                cleaned_bytes += sz
                cleaned_files += 1
            except Exception:
                pass

    # 2. Clean old __pycache__ if any
    for root, dirs, files in os.walk(BASE_DIR):
        if "__pycache__" in root:
            for f in files:
                if f.endswith(".pyc"):
                    try:
                        sz = os.path.getsize(os.path.join(root, f))
                        os.remove(os.path.join(root, f))
                        cleaned_bytes += sz
                        cleaned_files += 1
                    except Exception:
                        pass

    mb_freed = round(cleaned_bytes / (1024 * 1024), 2)
    return {
        "success": True,
        "status": "SUCCESS" if cleaned_files > 0 else "NO_OP",
        "cleaned_files": cleaned_files,
        "mb_freed": mb_freed,
        "message": f"Safe cleanup completed: {cleaned_files} temporary files removed ({mb_freed} MB freed)."
    }
