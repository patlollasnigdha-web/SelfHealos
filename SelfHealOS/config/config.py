import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
MODEL_DIR = os.path.join(BASE_DIR, "model")
TESTS_DIR = os.path.join(BASE_DIR, "tests")

# File paths
DATA_FILE = os.path.join(DATA_DIR, "system_metrics.csv")
MODEL_FILE = os.path.join(MODEL_DIR, "anomaly_model.pkl")
EVAL_FILE = os.path.join(MODEL_DIR, "model_evaluation.json")
RECOVERY_LOG_FILE = os.path.join(LOGS_DIR, "recovery_log.json")
SYSTEM_LOG_FILE = os.path.join(LOGS_DIR, "system.log")
TEST_SCRIPT = os.path.join(TESTS_DIR, "test_process.py")

# Monitoring Configuration
MONITOR_INTERVAL = 5  # seconds
CONFIRMATION_READINGS = 3  # consecutive readings to confirm fault
TOP_PROCESSES_LIMIT = 15
CPU_SAMPLE_INTERVAL = 0.5  # seconds

# System Thresholds (Warning, Critical)
CPU_WARNING_THRESHOLD = 70.0
CPU_CRITICAL_THRESHOLD = 90.0

RAM_WARNING_THRESHOLD = 75.0
RAM_CRITICAL_THRESHOLD = 90.0

DISK_WARNING_THRESHOLD = 80.0
DISK_CRITICAL_THRESHOLD = 90.0

# Process Thresholds
PROCESS_CPU_THRESHOLD = 80.0
PROCESS_RAM_THRESHOLD = 20.0

# Recovery Configuration
RECOVERY_WAIT_TIME = 3.0  # seconds to wait before post-recovery verification
MAX_RECOVERY_RETRIES = 2

# Critical OS and System Protected Processes (Never terminate automatically)
PROTECTED_PROCESSES = {
    "system", "system idle process", "registry", "smss.exe",
    "csrss.exe", "wininit.exe", "services.exe", "lsass.exe",
    "winlogon.exe", "explorer.exe", "dwm.exe", "svchost.exe",
    "msmpeng.exe", "onedrive.exe", "spoolsv.exe", "fontdrvhost.exe",
    "sihost.exe", "taskhostw.exe", "ctfmon.exe", "shellexperiencehost.exe"
}

# Fault Types
FAULT_CPU_OVERLOAD = "CPU_OVERLOAD"
FAULT_MEMORY_OVERLOAD = "MEMORY_OVERLOAD"
FAULT_DISK_PRESSURE = "DISK_PRESSURE"
FAULT_PROCESS_ABNORMALITY = "PROCESS_ABNORMALITY"
FAULT_SYSTEM_NORMAL = "SYSTEM_NORMAL"

# Severity Levels
SEVERITY_NORMAL = "NORMAL"
SEVERITY_WARNING = "WARNING"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"
