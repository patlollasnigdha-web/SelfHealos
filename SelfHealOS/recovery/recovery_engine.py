import json
import os
import time
from datetime import datetime

from config.config import (
    LOGS_DIR, RECOVERY_LOG_FILE,
    FAULT_CPU_OVERLOAD, FAULT_MEMORY_OVERLOAD, FAULT_DISK_PRESSURE
)
from recovery.recovery_actions import (
    restart_controlled_process, safe_disk_cleanup, is_protected_process
)
from recovery.recovery_verifier import RecoveryVerifier
from data.structured_logger import log_event

def _append_recovery_log(entry):
    os.makedirs(LOGS_DIR, exist_ok=True)
    records = []
    if os.path.exists(RECOVERY_LOG_FILE):
        try:
            with open(RECOVERY_LOG_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
                if not isinstance(records, list):
                    records = []
        except (json.JSONDecodeError, OSError):
            records = []
    records.append(entry)
    try:
        with open(RECOVERY_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4)
    except Exception as e:
        print(f"Warning: Failed to write to {RECOVERY_LOG_FILE}: {e}")

def execute_recovery(diagnosis):
    """
    Orchestrates safety checks, execution of recovery action, post-recovery verification,
    and structured logging.
    """
    fault_type = diagnosis.get("fault_type")
    p_name = diagnosis.get("process", "Unknown")
    pid = diagnosis.get("pid", 0)

    log_event("RECOVERY_STARTED", {
        "fault": fault_type, "process": p_name, "pid": pid
    })

    start_time = time.time()

    # Determine recovery action
    if fault_type in {FAULT_CPU_OVERLOAD, FAULT_MEMORY_OVERLOAD}:
        action = "RESTART"
        action_res = restart_controlled_process(pid, p_name)
    elif fault_type == FAULT_DISK_PRESSURE:
        action = "CLEANUP"
        action_res = safe_disk_cleanup()
    else:
        action = "INVESTIGATE"
        action_res = {
            "success": False,
            "status": "SAFE_STOP",
            "message": "Automated recovery withheld; condition logged for diagnostic analysis."
        }

    recovery_time = round(time.time() - start_time, 2)

    # Post-Recovery Verification
    verifier = RecoveryVerifier()
    verification = verifier.verify(diagnosis, action_res)

    final_status = "SUCCESS" if (action_res.get("success") and verification["verified"]) else action_res.get("status", "FAILED")
    if action_res.get("status") == "SAFE_STOP":
        final_status = "SAFE_STOP"

    # Construct complete structured log entry
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fault_type": fault_type,
        "severity": diagnosis.get("severity"),
        "process_name": p_name,
        "pid": pid,
        "action": action,
        "status": final_status,
        "before_metric": verification["before_metric"],
        "after_metric": verification["after_metric"],
        "recovery_time": recovery_time,
        "verification_status": verification["verification_status"],
        "verification_notes": verification["notes"],
        "message": action_res.get("message", "")
    }
    if "new_pid" in action_res and action_res["new_pid"]:
        log_entry["new_pid"] = action_res["new_pid"]

    _append_recovery_log(log_entry)

    # Structured event logging
    if final_status == "SUCCESS":
        log_event("RECOVERY_COMPLETED", {"pid": pid, "status": "SUCCESS", "new_pid": action_res.get("new_pid")})
        log_event("RECOVERY_VERIFIED", {"pid": pid, "status": verification["verification_status"]})
    elif final_status == "SAFE_STOP":
        log_event("RECOVERY_STOPPED_FOR_SAFETY", {"pid": pid, "reason": action_res.get("message")})
    else:
        log_event("RECOVERY_FAILED", {"pid": pid, "error": action_res.get("message")})

    # Console output display
    print("\n" + "=" * 78)
    print("                      RECOVERY & VERIFICATION ENGINE")
    print("=" * 78)
    print(f"Action             : {action}")
    print(f"Action Status      : {action_res.get('status')}")
    print(f"Message            : {action_res.get('message')}")
    print(f"BEFORE RECOVERY    : {verification['before_metric']}")
    print(f"AFTER RECOVERY     : {verification['after_metric']}")
    print(f"Verification Result: {verification['verification_status']}")
    print(f"Verification Notes : {verification['notes']}")
    print(f"Recovery Duration  : {recovery_time}s")
    print("=" * 78)

    return {
        **action_res,
        "verification": verification,
        "final_status": final_status
    }
