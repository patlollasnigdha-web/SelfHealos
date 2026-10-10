import os
import time
import psutil
from datetime import datetime
from config.config import TOP_PROCESSES_LIMIT, CPU_SAMPLE_INTERVAL

def _disk_percent():
    path = "C:\\" if os.name == "nt" else "/"
    try:
        return psutil.disk_usage(path).percent
    except (OSError, PermissionError):
        try:
            return psutil.disk_usage(os.path.abspath(os.sep)).percent
        except Exception:
            return 0.0

def get_system_metrics():
    try:
        cpu = psutil.cpu_percent(interval=0.2)
    except Exception:
        cpu = 0.0

    try:
        ram = psutil.virtual_memory().percent
    except Exception:
        ram = 0.0

    disk = _disk_percent()

    return {
        "cpu": round(cpu, 1),
        "ram": round(ram, 1),
        "disk": round(disk, 1),
    }

def get_process_metrics(limit=TOP_PROCESSES_LIMIT):
    result = []
    # Bulk iteration over process info
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            p_cpu = info.get("cpu_percent") or 0.0
            p_mem = info.get("memory_percent") or 0.0
            p_name = info.get("name") or "Unknown"
            result.append({
                "pid": info["pid"],
                "name": p_name,
                "cpu": round(p_cpu, 2),
                "memory": round(p_mem, 2),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        except Exception:
            pass

    # Sort and merge top CPU consumers and top RAM consumers
    by_cpu = sorted(result, key=lambda x: x["cpu"], reverse=True)[:limit]
    by_mem = sorted(result, key=lambda x: x["memory"], reverse=True)[:limit]

    seen = set()
    combined = []
    for p in by_cpu + by_mem:
        if p["pid"] not in seen:
            seen.add(p["pid"])
            combined.append(p)

    return combined[:limit]

def get_snapshot():
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system": get_system_metrics(),
        "processes": get_process_metrics(),
    }
