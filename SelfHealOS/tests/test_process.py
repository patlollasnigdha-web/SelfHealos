import argparse
import os
import sys
import time
import threading

def _cpu_worker(stop_flag):
    while not stop_flag["stop"]:
        total = 0
        for n in range(1_000_000):
            total += n * n

def run_cpu_fault():
    print("=" * 60)
    print("SelfHealOS Controlled Fault Simulator — CPU FAULT")
    print(f"PID     : {os.getpid()}")
    print("STATUS  : INDUCING HIGH CPU LOAD (MULTI-THREADED)")
    print("=" * 60)
    stop_flag = {"stop": False}
    threads = []
    for _ in range(4):
        t = threading.Thread(target=_cpu_worker, args=(stop_flag,))
        t.daemon = True
        t.start()
        threads.append(t)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_flag["stop"] = True
        print("\nFault simulator stopped.")

def run_memory_fault():
    print("=" * 60)
    print("SelfHealOS Controlled Fault Simulator — MEMORY FAULT")
    print(f"PID     : {os.getpid()}")
    print("STATUS  : ALLOCATING MEMORY BLOCKS")
    print("=" * 60)
    chunks = []
    try:
        for _ in range(8):
            chunks.append(bytearray(50 * 1024 * 1024))  # ~400MB total
            time.sleep(0.05)
        print("Memory allocated. Holding active state...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMemory fault simulator stopped.")

def run_abnormal_fault():
    print("=" * 60)
    print("SelfHealOS Controlled Fault Simulator — ABNORMAL BEHAVIOR")
    print(f"PID     : {os.getpid()}")
    print("STATUS  : BURSTING RESOURCE USAGE")
    print("=" * 60)
    stop_flag = {"stop": False}
    t = threading.Thread(target=_cpu_worker, args=(stop_flag,))
    t.daemon = True
    t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_flag["stop"] = True
        print("\nAbnormal simulator stopped.")

def run_recovered_mode():
    print("=" * 60)
    print("SelfHealOS Controlled Process — RECOVERED MODE")
    print(f"PID     : {os.getpid()}")
    print("STATUS  : OPERATING NORMALLY (LOW RESOURCE USAGE)")
    print("=" * 60)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nRecovered process stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SelfHealOS Controlled Test Process")
    parser.add_argument("--mode", choices=["cpu", "memory", "abnormal", "recovered"], default="cpu")
    args = parser.parse_args()

    if os.environ.get("SELFHEAL_RECOVERED") == "1" or args.mode == "recovered":
        run_recovered_mode()
    elif args.mode == "memory":
        run_memory_fault()
    elif args.mode == "abnormal":
        run_abnormal_fault()
    else:
        run_cpu_fault()
