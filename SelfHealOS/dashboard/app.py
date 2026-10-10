import json
import os
import sys
import time
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.config import (
    DATA_FILE, MODEL_FILE, EVAL_FILE, RECOVERY_LOG_FILE, SYSTEM_LOG_FILE,
    CPU_WARNING_THRESHOLD, CPU_CRITICAL_THRESHOLD,
    RAM_WARNING_THRESHOLD, RAM_CRITICAL_THRESHOLD,
    DISK_WARNING_THRESHOLD, DISK_CRITICAL_THRESHOLD
)
from monitor.system_monitor import get_snapshot
from ml.anomaly_detector import AnomalyDetector
from detector.fault_detector import FaultDetector

st.set_page_config(
    page_title="SelfHealOS — AI Operating System Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #616161;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #1E88E5;
    }
    .status-normal {
        color: #2e7d32;
        font-weight: bold;
    }
    .status-warning {
        color: #f57f17;
        font-weight: bold;
    }
    .status-critical {
        color: #c62828;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🛡️ SelfHealOS")
st.sidebar.markdown("**AI-Powered Fault Detection & Self-Healing**")
st.sidebar.markdown("---")
refresh_rate = st.sidebar.slider("Live Dashboard Refresh (sec)", min_value=2, max_value=30, value=5)
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)

st.sidebar.markdown("### System Thresholds")
st.sidebar.info(f"""
- **CPU Warning / Critical**: {CPU_WARNING_THRESHOLD}% / {CPU_CRITICAL_THRESHOLD}%
- **RAM Warning / Critical**: {RAM_WARNING_THRESHOLD}% / {RAM_CRITICAL_THRESHOLD}%
- **Disk Warning / Critical**: {DISK_WARNING_THRESHOLD}% / {DISK_CRITICAL_THRESHOLD}%
""")

# Header
st.markdown('<p class="main-title">SelfHealOS Control & Telemetry Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Continuous OS Telemetry, Machine Learning Anomaly Detection & Safe Automated Recovery</p>', unsafe_allow_html=True)

# 1. LIVE SYSTEM SNAPSHOT
snapshot = get_snapshot()
detector = FaultDetector()
model = AnomalyDetector()
ml_result = model.predict(snapshot)

sys_metrics = snapshot["system"]
cpu_val = sys_metrics["cpu"]
ram_val = sys_metrics["ram"]
disk_val = sys_metrics["disk"]

cpu_stat = detector.system_status(cpu_val, "cpu")
ram_stat = detector.system_status(ram_val, "ram")
disk_stat = detector.system_status(disk_val, "disk")

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="System CPU",
        value=f"{cpu_val:.1f}%",
        delta=f"Status: {cpu_stat}",
        delta_color="inverse" if cpu_stat != "NORMAL" else "normal"
    )
    st.progress(min(1.0, max(0.0, cpu_val / 100.0)))

with col2:
    st.metric(
        label="System RAM",
        value=f"{ram_val:.1f}%",
        delta=f"Status: {ram_stat}",
        delta_color="inverse" if ram_stat != "NORMAL" else "normal"
    )
    st.progress(min(1.0, max(0.0, ram_val / 100.0)))

with col3:
    st.metric(
        label="Disk Usage",
        value=f"{disk_val:.1f}%",
        delta=f"Status: {disk_stat}",
        delta_color="inverse" if disk_stat != "NORMAL" else "normal"
    )
    st.progress(min(1.0, max(0.0, disk_val / 100.0)))

with col4:
    ml_status = ml_result.get("status", "N/A")
    score = ml_result.get("score", 0.0)
    conf = ml_result.get("confidence_str", "N/A")
    st.metric(
        label="ML Anomaly Engine",
        value=ml_status,
        delta=f"Confidence: {conf} (Score: {score:.3f})"
    )

st.markdown("---")

# Tabs for Organized Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🖥️ Active Processes",
    "📈 Telemetry & Trends",
    "🤖 ML Model Evaluation",
    "🔄 Recovery History",
    "📋 System Event Logs"
])

# TAB 1: ACTIVE PROCESSES
with tab1:
    st.subheader("Top Active Monitored Processes")
    if snapshot["processes"]:
        proc_df = pd.DataFrame(snapshot["processes"])
        st.dataframe(
            proc_df.rename(columns={
                "pid": "PID",
                "name": "Process Name",
                "cpu": "CPU Usage (%)",
                "memory": "Memory Usage (%)"
            }),
            use_container_width=True
        )
    else:
        st.write("No active process metrics available.")

# TAB 2: TELEMETRY & TRENDS
with tab2:
    st.subheader("Historical System Resource Telemetry")
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try:
            df = pd.read_csv(DATA_FILE)
            if not df.empty and "timestamp" in df.columns:
                # Group by timestamp to get system-level curve
                summary_df = df.groupby("timestamp")[["system_cpu", "system_ram", "disk_usage"]].mean().reset_index()
                st.line_chart(summary_df.set_index("timestamp"))
                st.caption("Aggregated CPU, RAM, and Disk telemetry over time.")
            else:
                st.info("Telemetry data file is currently empty.")
        except Exception as e:
            st.error(f"Error reading telemetry data: {e}")
    else:
        st.info("No historical telemetry file found. Run SelfHealOS monitoring to collect data.")

# TAB 3: ML MODEL EVALUATION
with tab3:
    st.subheader("Machine Learning Performance & Metrics")
    if os.path.exists(EVAL_FILE):
        try:
            with open(EVAL_FILE, "r", encoding="utf-8") as f:
                eval_data = json.load(f)

            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Model Accuracy", f"{eval_data.get('accuracy', 0)*100:.2f}%")
            m_col2.metric("Precision", f"{eval_data.get('precision', 0)*100:.2f}%")
            m_col3.metric("Recall", f"{eval_data.get('recall', 0)*100:.2f}%")
            m_col4.metric("F1-Score", f"{eval_data.get('f1_score', 0)*100:.2f}%")

            st.markdown("#### Confusion Matrix Breakdown")
            cm = eval_data.get("confusion_matrix", [[0, 0], [0, 0]])
            if len(cm) == 2:
                cm_df = pd.DataFrame(
                    cm,
                    columns=["Predicted Normal", "Predicted Anomaly"],
                    index=["Actual Normal", "Actual Anomaly"]
                )
                st.table(cm_df)

            st.markdown("#### Model Specification")
            st.json({
                "Algorithm": "Isolation Forest (Unsupervised / Semi-supervised)",
                "Features Used": eval_data.get("features", ["system_cpu", "system_ram", "disk_usage", "top_process_cpu", "top_process_ram"]),
                "Samples Evaluated": eval_data.get("samples_evaluated", eval_data.get("samples", 0)),
                "Anomalies Flagged": eval_data.get("anomaly_count", eval_data.get("anomalies_detected", 0)),
                "Model File": MODEL_FILE
            })
        except Exception as e:
            st.error(f"Failed to load evaluation metrics: {e}")
    else:
        st.warning("Model evaluation metrics not generated yet. Run `python ml/train_model.py`.")

# TAB 4: RECOVERY HISTORY
with tab4:
    st.subheader("Automated Recovery & Verification Log")
    if os.path.exists(RECOVERY_LOG_FILE):
        try:
            with open(RECOVERY_LOG_FILE, "r", encoding="utf-8") as f:
                rec_logs = json.load(f)

            if rec_logs:
                rec_df = pd.DataFrame(rec_logs)
                cols_to_show = [c for c in [
                    "timestamp", "fault_type", "severity", "process_name", "pid",
                    "action", "status", "verification_status", "before_metric", "after_metric", "recovery_time"
                ] if c in rec_df.columns]
                st.dataframe(rec_df[cols_to_show].sort_index(ascending=False), use_container_width=True)
            else:
                st.info("No recovery records logged yet.")
        except Exception as e:
            st.error(f"Error loading recovery log: {e}")
    else:
        st.info("No recovery log found.")

# TAB 5: SYSTEM EVENT LOGS
with tab5:
    st.subheader("Structured System Event Stream")
    if os.path.exists(SYSTEM_LOG_FILE):
        try:
            with open(SYSTEM_LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                st.text_area("Recent System Logs", "".join(lines[-40:]), height=350)
            else:
                st.info("System log is empty.")
        except Exception as e:
            st.error(f"Error reading system log: {e}")
    else:
        st.info("System log file will be generated when SelfHealOS runs.")

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
