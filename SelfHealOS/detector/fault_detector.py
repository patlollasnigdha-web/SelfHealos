from config.config import (
    PROCESS_CPU_THRESHOLD, PROCESS_RAM_THRESHOLD,
    CPU_WARNING_THRESHOLD, CPU_CRITICAL_THRESHOLD,
    RAM_WARNING_THRESHOLD, RAM_CRITICAL_THRESHOLD,
    DISK_WARNING_THRESHOLD, DISK_CRITICAL_THRESHOLD,
    CONFIRMATION_READINGS,
    SEVERITY_NORMAL, SEVERITY_WARNING, SEVERITY_CRITICAL
)

class FaultDetector:
    def __init__(self, confirmations=CONFIRMATION_READINGS):
        self.confirmations = confirmations
        self.persistence = {}  # pid -> consecutive reading count
        self.handled = set()    # pids currently handled/recovering

    def system_status(self, value, metric):
        """Returns severity status string for a given system metric value."""
        if metric == "cpu":
            warning, critical = CPU_WARNING_THRESHOLD, CPU_CRITICAL_THRESHOLD
        elif metric == "ram":
            warning, critical = RAM_WARNING_THRESHOLD, RAM_CRITICAL_THRESHOLD
        elif metric == "disk":
            warning, critical = DISK_WARNING_THRESHOLD, DISK_CRITICAL_THRESHOLD
        else:
            warning, critical = 75.0, 90.0

        if value >= critical:
            return SEVERITY_CRITICAL
        if value >= warning:
            return SEVERITY_WARNING
        return SEVERITY_NORMAL

    def is_abnormal(self, process, system=None):
        """Checks if a process exceeds CPU/Memory thresholds or is abnormal."""
        cpu = float(process.get("cpu", 0.0))
        mem = float(process.get("memory", 0.0))

        if cpu >= PROCESS_CPU_THRESHOLD or mem >= PROCESS_RAM_THRESHOLD:
            return True

        if system:
            # If system is in critical state and this process is a top contributor (>40% cpu or >15% mem)
            if system.get("cpu", 0.0) >= CPU_CRITICAL_THRESHOLD and cpu >= 40.0:
                return True
            if system.get("ram", 0.0) >= RAM_CRITICAL_THRESHOLD and mem >= 15.0:
                return True

        return False

    def update(self, snapshot):
        """
        Updates persistence tracking for observed processes and returns a list
        of confirmed faulty processes that reached the required confirmation count.
        """
        system = snapshot.get("system", {})
        processes = snapshot.get("processes", [])
        current_abnormal_pids = set()
        confirmed = []

        for p in processes:
            pid = p["pid"]
            if not self.is_abnormal(p, system):
                continue

            current_abnormal_pids.add(pid)
            self.persistence[pid] = self.persistence.get(pid, 0) + 1

            if self.persistence[pid] >= self.confirmations and pid not in self.handled:
                confirmed.append(p)

        # Clean up processes that are no longer abnormal
        for pid in list(self.persistence.keys()):
            if pid not in current_abnormal_pids:
                del self.persistence[pid]
                self.handled.discard(pid)

        return confirmed

    def mark_handled(self, pid):
        self.handled.add(pid)

    def replace_pid(self, old_pid, new_pid):
        self.handled.discard(old_pid)
        self.persistence.pop(old_pid, None)
        self.persistence[new_pid] = 0
