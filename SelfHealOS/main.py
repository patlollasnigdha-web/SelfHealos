import argparse
import os
import sys
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.config import (
    MONITOR_INTERVAL, CONFIRMATION_READINGS, TOP_PROCESSES_LIMIT,
    FAULT_CPU_OVERLOAD, FAULT_MEMORY_OVERLOAD
)
from monitor.system_monitor import get_snapshot
from data.metrics_logger import log_snapshot
from data.structured_logger import log_event
from detector.fault_detector import FaultDetector
from diagnosis.diagnosis_engine import diagnose
from ml.anomaly_detector import AnomalyDetector
from recovery.recovery_engine import execute_recovery

def print_header(interval, confirmations):
    print("\n" + "=" * 78)
    print("                         SelfHealOS")
    print("              AI-Based OS Fault Detection")
    print("                 and Automatic Recovery")
    print("=" * 78)
    print(f"Monitoring interval : {interval} seconds")
    print(f"Fault confirmation  : {confirmations} consecutive readings")
    print("Recovery policy     : Safe controlled recovery / Protected OS isolation")
    print("Press Ctrl+C to stop.")
    print("=" * 78)

def print_status(snapshot, detector, model_result):
    s = snapshot["system"]
    cpu_status = detector.system_status(s['cpu'], 'cpu')
    ram_status = detector.system_status(s['ram'], 'ram')
    disk_status = detector.system_status(s['disk'], 'disk')

    print("\n" + "-" * 78)
    print(f"CURRENT SYSTEM STATUS [{snapshot['timestamp']}]")
    print("-" * 78)
    print(f"CPU  : {s['cpu']:5.1f}% [{cpu_status}]")
    print(f"RAM  : {s['ram']:5.1f}% [{ram_status}]")
    print(f"Disk : {s['disk']:5.1f}% [{disk_status}]")

    if model_result.get("available"):
        print(f"\nML Anomaly Score : {model_result['score']:.4f}")
        print(f"ML Model State   : {model_result['status']} (Confidence: {model_result['confidence_str']})")

    print("\nTop monitored processes:")
    print(f"{'PID':<8}{'Process Name':<32}{'CPU %':>8}{'RAM %':>9}{'Persist':>10}")
    print("-" * 78)
    for p in snapshot["processes"][:TOP_PROCESSES_LIMIT]:
        count = detector.persistence.get(p["pid"], 0)
        p_name = p["name"][:30]
        print(f"{p['pid']:<8}{p_name:<32}{p['cpu']:>8.1f}{p['memory']:>9.1f}{count:>7}/{detector.confirmations}")

def run_pipeline(interval=MONITOR_INTERVAL, confirmations=CONFIRMATION_READINGS, max_cycles=None):
    print_header(interval, confirmations)
    log_event("SYSTEM_STARTED", {"interval": interval, "confirmations": confirmations})

    detector = FaultDetector(confirmations=confirmations)
    model = AnomalyDetector()

    cycle = 0
    try:
        while True:
            cycle += 1
            snapshot = get_snapshot()
            log_snapshot(snapshot)

            model_result = model.predict(snapshot)
            confirmed = detector.update(snapshot)

            print_status(snapshot, detector, model_result)

            if not confirmed:
                print("\n[OK] System operational. No persistent fault confirmed.")
            else:
                for process in confirmed:
                    log_event("FAULT_DETECTED", {
                        "pid": process["pid"], "name": process["name"],
                        "cpu": process["cpu"], "memory": process["memory"]
                    })

                    diagnosis = diagnose(process, snapshot["system"], model_result)

                    log_event("FAULT_CLASSIFIED", {
                        "fault_type": diagnosis["fault_type"],
                        "severity": diagnosis["severity"],
                        "confidence": diagnosis["confidence_str"],
                        "pid": diagnosis["pid"]
                    })

                    print("\n" + "=" * 78)
                    print("                         FAULT CONFIRMED")
                    print("=" * 78)
                    print(f"Process    : {diagnosis['process']} (PID {diagnosis['pid']})")
                    print(f"Fault Type : {diagnosis['fault_type']}")
                    print(f"Severity   : {diagnosis['severity']}")
                    print(f"Confidence : {diagnosis['confidence_str']}")
                    print(f"Reason     : {diagnosis['reason']}")

                    result = execute_recovery(diagnosis)
                    detector.mark_handled(process["pid"])

                    if result.get("new_pid"):
                        detector.replace_pid(process["pid"], result["new_pid"])

            if max_cycles and cycle >= max_cycles:
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nSelfHealOS stopped safely by user.")
    finally:
        log_event("SYSTEM_STOPPED", {"cycles_executed": cycle})

def main():
    parser = argparse.ArgumentParser(description="SelfHealOS — AI-Based OS Fault Detection & Automatic Recovery")
    parser.add_argument("--interval", type=float, default=MONITOR_INTERVAL, help="Monitoring interval in seconds")
    parser.add_argument("--confirmations", type=int, default=CONFIRMATION_READINGS, help="Readings to confirm fault")
    parser.add_argument("--cycles", type=int, default=None, help="Number of cycles to run (optional)")
    args = parser.parse_args()

    run_pipeline(interval=args.interval, confirmations=args.confirmations, max_cycles=args.cycles)

if __name__ == "__main__":
    main()
