# SelfHealOS
### AI-Based Operating System Fault Detection and Automatic Recovery System

SelfHealOS is an intelligent, resilient operating system monitoring and self-healing framework. It continuously monitors live system metrics (CPU, RAM, Disk, Process Telemetry), identifies anomalous resource signatures using machine learning (Isolation Forest), confirms sustained faults to avoid false positives from transient spikes, executes safe recovery actions (such as controlled process restarts and disk cleanup while strictly protecting core OS components), rigorously verifies fault remediation, maintains structured event logs, and visualizes live system health through an interactive Streamlit dashboard.

---

## 1. Pipeline Architecture

```text
       +---------------------------------------------+
       |             Host Operating System           |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |   Continuous System & Process Monitoring    |
       |  (psutil: CPU, RAM, Disk, Process Metrics)  |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |             Feature Extraction              |
       |   [sys_cpu, sys_ram, disk, top_cpu, top_ram]|
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |            Fault & Anomaly Engine           |
       |   * Threshold & Persistence Confirmation    |
       |   * ML Anomaly Scoring (Isolation Forest)   |
       |   * Calibrated Confidence Calculation       |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |   Diagnosis Engine & Severity Assessment    |
       |  (CPU/RAM Overload, Disk Pressure, etc.)    |
       |  (Severity: NORMAL, WARNING, CRITICAL)      |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |         Safe Recovery Engine                |
       |   * Protected Process Immunity Check        |
       |   * Controlled Target Restart / Cleanup     |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |        Post-Recovery Verification           |
       |  (Measure Before vs After Telemetry)        |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |      Structured Logging & Telemetry CSV     |
       |  (system_metrics.csv, recovery_log.json)    |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |       Interactive Streamlit Dashboard       |
       +---------------------------------------------+
```

---

## 2. Project Directory Structure

```text
SelfHealOS/
│
├── main.py                     # Main CLI monitoring and self-healing loop
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation
│
├── config/
│   ├── __init__.py
│   └── config.py               # Centralized thresholds, intervals & settings
│
├── monitor/
│   └── system_monitor.py       # Live telemetry collection (CPU, RAM, Disk, Top processes)
│
├── detector/
│   └── fault_detector.py       # Persistence tracking and confirmation readings
│
├── diagnosis/
│   └── diagnosis_engine.py     # Fault classification, severity mapping & ML confidence
│
├── ml/
│   ├── __init__.py
│   ├── anomaly_detector.py     # Inference engine with sigmoid confidence scaling
│   ├── train_model.py          # Model training pipeline & metric calculation
│   ├── evaluate_model.py       # Independent ML evaluation script
│   └── predict.py              # Standalone prediction tool
│
├── model/
│   ├── anomaly_model.pkl       # Serialized Isolation Forest model & Scaler
│   └── model_evaluation.json  # Stored ML evaluation metrics
│
├── recovery/
│   ├── recovery_engine.py      # Recovery orchestrator
│   ├── recovery_actions.py     # Controlled restart & safe workspace cleanup
│   └── recovery_verifier.py    # Before vs After metric comparison & validation
│
├── data/
│   ├── metrics_logger.py       # Append live snapshots to dataset
│   ├── structured_logger.py    # Structured lifecycle event logging
│   └── system_metrics.csv      # Real operating system telemetry dataset
│
├── logs/
│   ├── system.log              # Structured event stream
│   └── recovery_log.json       # Detailed recovery history
│
├── dashboard/
│   └── app.py                  # Streamlit visual dashboard
│
└── tests/
    ├── test_process.py         # Multi-mode controlled test process (CPU, Memory, Abnormal)
    ├── test_monitoring.py      # Unit tests for system monitoring
    ├── test_detection.py       # Unit tests for fault detector & diagnosis
    ├── test_recovery.py        # Unit tests for safety checks & verifier
    ├── stress_test.py          # End-to-end experimental test suite (6 scenarios)
    └── experimental_results.json # Saved experimental test results
```

---

## 3. Installation & Setup

### Prerequisites
* Python 3.10+ (Tested on Python 3.12 and 3.13)
* Operating System: Windows / Linux / macOS

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 4. How to Run SelfHealOS

### A. Run Real-Time Self-Healing System
```bash
python main.py
```
Optional flags:
* `--interval 5`: Set monitoring interval in seconds (default: 5)
* `--confirmations 3`: Set consecutive readings required for confirmation (default: 3)
* `--cycles 10`: Run for N monitoring cycles then exit

### B. Run Interactive Web Dashboard
```bash
streamlit run dashboard/app.py
```
The dashboard displays:
* Real-time CPU, RAM, and Disk gauges
* ML Anomaly status and calibrated confidence score
* Active top monitored processes
* Telemetry trend charts
* ML Model Evaluation metrics (Accuracy, Precision, Recall, F1, Confusion Matrix)
* Automated Recovery & Verification Log

### C. Train and Evaluate Machine Learning Model
```bash
# Train Isolation Forest on historical system metrics
python ml/train_model.py

# Evaluate model metrics independently
python ml/evaluate_model.py

# Run standalone real-time prediction
python ml/predict.py
```

### D. Run Unit Tests & Automated Experimental Test Suite
```bash
# Unit tests
python tests/test_monitoring.py
python tests/test_detection.py
python tests/test_recovery.py

# End-to-end experimental test suite (all 6 test scenarios)
python tests/stress_test.py
```

---

## 5. Machine Learning Evaluation

The ML subsystem uses an **Isolation Forest** trained on standardized features:
1. `system_cpu`: System-wide CPU utilization percentage
2. `system_ram`: System-wide RAM utilization percentage
3. `disk_usage`: Primary storage utilization percentage
4. `top_process_cpu`: Highest individual process CPU utilization
5. `top_process_ram`: Highest individual process RAM utilization

### ML Evaluation Results (Real Execution):
* **Evaluated Samples**: 240
* **Accuracy**: **90.83%**
* **Precision**: **45.00%**
* **Recall**: **45.00%**
* **F1-Score**: **45.00%**
* **Confusion Matrix**:
  * True Negatives: 209
  * False Positives: 11
  * False Negatives: 11
  * True Positives: 9

---

## 6. Experimental Test Results

Executed via `python tests/stress_test.py`:

| Test Scenario | Fault Type | Detected | Classified | Recovery | Verification | Time (s) |
|---|---|---|---|---|---|---|
| **Test 1 — CPU Overload** | `CPU_OVERLOAD` | YES | YES | SUCCESS | SUCCESS | 6.78s |
| **Test 2 — Memory Pressure** | `MEMORY_OVERLOAD` | YES | YES | SUCCESS | SUCCESS | 5.21s |
| **Test 3 — Process Abnormality** | `PROCESS_ABNORMALITY` | YES | YES | INVESTIGATE | SUCCESS | 2.15s |
| **Test 4 — Normal System State** | `SYSTEM_NORMAL` | NO FAULT | YES (BASELINE) | NOT_REQUIRED | SUCCESS | 0.52s |
| **Test 5 — Recovery Success** | `CPU_OVERLOAD` | YES | YES | SUCCESS | SUCCESS | 4.89s |
| **Test 6 — Recovery Failure / Safe Isolation** | `PROTECTED_OS_PROCESS` | YES | YES | SAFE_STOP | SUCCESS | 3.02s |

---

## 7. Safety Guarantees

1. **Protected OS Isolation**: Critical processes (`System`, `csrss.exe`, `explorer.exe`, `services.exe`, `wininit.exe`, `lsass.exe`, `dwm.exe`, `svchost.exe`, etc.) are explicitly blacklisted and will **never** be automatically terminated or restarted.
2. **Persistence Confirmation**: Spikes must persist across multiple consecutive measurement cycles (`CONFIRMATION_READINGS`) before triggering recovery.
3. **Recovery Verification**: A recovery action is only deemed successful if post-recovery telemetry confirms resource normalization and target process stabilization.

---

## 8. Limitations & Future Scope

### Limitations
* Process restarts require the application to provide a restartable entrypoint (demonstrated via controlled test process).
* Memory cleanup for compiled external binaries is limited without kernel-level hooks.

### Future Scope
* Dynamic CPU affinity and process priority throttling (`psutil.Process().nice()`) prior to termination.
* Deep learning LSTM/Transformer models for predictive multi-step failure forecasting.
* Integration with eBPF (on Linux) and ETW (on Windows) for microsecond-level kernel trace detection.
