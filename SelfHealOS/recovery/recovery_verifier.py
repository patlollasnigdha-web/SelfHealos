import time
import psutil
from monitor.system_monitor import get_system_metrics
from config.config import (
    RECOVERY_WAIT_TIME, PROCESS_CPU_THRESHOLD, PROCESS_RAM_THRESHOLD
)

class RecoveryVerifier:
    def __init__(self, wait_time=RECOVERY_WAIT_TIME):
        self.wait_time = wait_time

    def verify(self, diagnosis, action_result):
        """
        Performs rigorous post-recovery measurement and validation.
        Compares system and process state before vs after recovery.
        """
        # 1. Wait for the recovery changes to stabilize
        time.sleep(self.wait_time)

        old_pid = diagnosis.get("pid")
        new_pid = action_result.get("new_pid")
        fault_type = diagnosis.get("fault_type")
        before_cpu = diagnosis.get("process_cpu", diagnosis.get("system_cpu", 0.0))
        before_ram = diagnosis.get("process_ram", diagnosis.get("system_ram", 0.0))

        # 2. Sample new post-recovery metrics
        after_system = get_system_metrics()
        after_proc_cpu = 0.0
        after_proc_ram = 0.0
        proc_alive = False

        if new_pid and psutil.pid_exists(new_pid):
            try:
                p = psutil.Process(new_pid)
                p.cpu_percent(None)
                time.sleep(0.3)
                after_proc_cpu = round(p.cpu_percent(None), 2)
                after_proc_ram = round(p.memory_percent(), 2)
                proc_alive = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                proc_alive = False

        old_proc_exists = psutil.pid_exists(old_pid) if old_pid else False

        # 3. Assess recovery success criteria
        is_verified = False
        verification_notes = []

        if action_result.get("status") == "SAFE_STOP":
            is_verified = False
            verification_notes.append("Recovery action was halted for safety (unmanaged/protected target).")
            after_metric = f"System CPU: {after_system['cpu']}%, RAM: {after_system['ram']}%"
        elif fault_type in {"CPU_OVERLOAD", "MEMORY_OVERLOAD"}:
            if not old_proc_exists and proc_alive and after_proc_cpu < PROCESS_CPU_THRESHOLD:
                is_verified = True
                verification_notes.append(
                    f"Faulty PID {old_pid} terminated; recovered PID {new_pid} stable at CPU {after_proc_cpu}%, RAM {after_proc_ram}%."
                )
            elif not old_proc_exists and not new_pid:
                is_verified = True
                verification_notes.append(f"Offending PID {old_pid} terminated successfully.")
            else:
                is_verified = False
                verification_notes.append("Post-recovery metrics did not meet normal thresholds.")
            after_metric = f"Proc CPU: {after_proc_cpu}%, RAM: {after_proc_ram}% (System CPU: {after_system['cpu']}%)"
        elif fault_type == "DISK_PRESSURE":
            after_metric = f"System Disk: {after_system['disk']}%"
            is_verified = action_result.get("success", False)
            verification_notes.append(f"Post-cleanup disk usage is {after_system['disk']}%.")
        else:
            after_metric = f"System CPU: {after_system['cpu']}%, RAM: {after_system['ram']}%"
            is_verified = action_result.get("success", False)
            verification_notes.append("System resources re-evaluated.")

        before_metric = (
            f"Proc CPU: {before_cpu}%, RAM: {before_ram}% (System CPU: {diagnosis.get('system_cpu', 0)}%)"
            if fault_type in {"CPU_OVERLOAD", "MEMORY_OVERLOAD"}
            else f"Disk: {diagnosis.get('disk_usage', 0)}%"
        )

        return {
            "verified": is_verified,
            "verification_status": "SUCCESS" if is_verified else "FAILED",
            "before_metric": before_metric,
            "after_metric": after_metric,
            "after_system": after_system,
            "after_process": {
                "pid": new_pid,
                "cpu": after_proc_cpu,
                "ram": after_proc_ram,
                "alive": proc_alive
            },
            "notes": " ".join(verification_notes)
        }
