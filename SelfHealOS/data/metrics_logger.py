import csv
import os
from config.config import DATA_DIR, DATA_FILE

HEADER = [
    "timestamp", "system_cpu", "system_ram", "disk_usage",
    "process_name", "pid", "process_cpu", "process_ram"
]

def initialize_dataset():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADER)

def log_snapshot(snapshot):
    initialize_dataset()
    s = snapshot["system"]
    try:
        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for p in snapshot["processes"]:
                writer.writerow([
                    snapshot["timestamp"],
                    s["cpu"], s["ram"], s["disk"],
                    p["name"], p["pid"], p["cpu"], p["memory"]
                ])
    except Exception as e:
        # Prevent crash if file is temporarily locked
        pass
