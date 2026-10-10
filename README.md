# SelfHealOS 🖥️

### An Intelligent Self-Healing Operating System Framework

SelfHealOS is a Python-based system monitoring and automated recovery framework designed to detect potential system failures, identify abnormal resource usage, and initiate recovery actions. The project integrates system monitoring, fault logging, and machine learning to improve system reliability and reduce manual intervention.

---

## 📌 Project Overview

Modern computer systems may experience performance degradation due to excessive CPU utilization, memory exhaustion, disk pressure, and abnormal process behavior. Identifying these problems early and recovering from them manually can be time-consuming.

**SelfHealOS** aims to address this problem through continuous system monitoring, intelligent fault detection, and automated recovery mechanisms.

### 🎯 Objectives

* Monitor CPU, RAM, and disk utilization.
* Detect abnormal system behavior and resource overload.
* Classify system faults based on severity.
* Use machine learning to support fault prediction and detection.
* Log detected faults and recovery activities.
* Implement automated recovery actions where appropriate.
* Provide a foundation for a more reliable and self-managing computing environment.

---

## ✨ Key Features

* **Real-Time Monitoring:** Tracks system resource utilization.
* **Fault Detection:** Identifies potential CPU, memory, and disk-related issues.
* **Severity Classification:** Categorizes detected faults according to their severity.
* **Machine Learning Integration:** Supports intelligent fault classification using historical system data.
* **Automated Recovery:** Executes configured recovery actions for supported faults.
* **Fault Logging:** Maintains records of detected faults and recovery attempts.
* **Historical Analysis:** Uses collected system data to support model training and evaluation.

---

## 🛠️ Technologies Used

| Technology   | Purpose                                   |
| ------------ | ----------------------------------------- |
| Python       | Core application development              |
| psutil       | System and process monitoring             |
| pandas       | Dataset processing and manipulation       |
| scikit-learn | Machine learning and model development    |
| CSV          | Historical system data storage            |
| JSON         | Structured fault and recovery logs        |
| Git & GitHub | Version control and project collaboration |

*Note: Confirm these dependencies against your final project files before treating this list as definitive.*

---

## 🏗️ System Architecture

SelfHealOS follows a modular workflow:

1. **System Monitoring** — Collects CPU, memory, disk, and process information.
2. **Fault Detection** — Analyzes resource usage and identifies potential anomalies.
3. **Fault Classification** — Determines the fault type and severity.
4. **Machine Learning** — Uses historical data to support fault prediction or classification.
5. **Recovery Engine** — Performs configured recovery actions for supported faults.
6. **Logging and Analysis** — Stores fault details, timestamps, and recovery outcomes.

### Workflow

```text
       System Resources
              |
              v
      System Monitoring
              |
              v
        Fault Detection
              |
              v
      Fault Classification
              |
              v
      Machine Learning
              |
              v
       Recovery Engine
              |
              v
       Fault/Recovery Logs
```

*The diagram represents the intended high-level workflow. The exact execution sequence depends on the implemented modules.*

---

## 📂 Project Structure

The following is a suggested structure. Adjust it to match the actual files in your repository.

```text
OSSP-project/
│
├── SelfHealOS/
│   ├── ml/
│   │   └── train_model.py
│   │
│   ├── logs/
│   │   └── recovery_log.json
│   │
│   ├── monitoring/
│   ├── recovery/
│   ├── datasets/
│   │
│   └── main.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Installation and Setup

### Prerequisites

* Python 3.10 or later
* Git
* pip

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd OSSP-project
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your actual repository URL.

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### 3. Install Dependencies

If your project contains `requirements.txt`:

```bash
pip install -r requirements.txt
```

Otherwise, install the required packages:

```bash
pip install psutil pandas scikit-learn
```

---

## ▶️ Running the Project

Run the following commands from the appropriate project directory, depending on your actual file structure.

### Train the Machine Learning Model

```bash
python .\SelfHealOS\ml\train_model.py
```

### Start the Application

If `main.py` is the actual application entry point:

```bash
python .\SelfHealOS\main.py
```

**Important:** Replace the application command if your project uses a different entry point. Run the application from the directory expected by its configuration.

---

## 📊 Dataset

SelfHealOS uses historical system resource information to support fault detection and machine learning.

Potential dataset attributes include:

| Attribute    | Description                    |
| ------------ | ------------------------------ |
| timestamp    | Time of observation            |
| system_cpu   | Overall CPU utilization        |
| system_ram   | Overall memory utilization     |
| disk_usage   | Disk utilization               |
| process_name | Name of the monitored process  |
| pid          | Process identifier             |
| process_cpu  | CPU utilization of the process |
| process_ram  | Memory usage of the process    |

Historical data can be used to analyze system behavior and develop fault detection models.

**Note:** These columns describe the dataset format used during development and should be updated if the final dataset differs.

---

## 🔄 Recovery Mechanism

The recovery component is intended to respond to detected faults through configured corrective actions.

Examples of possible recovery strategies include:

* Recording the fault and generating a diagnostic report.
* Rechecking system resource utilization.
* Restarting a designated service when supported and authorized.
* Applying configured recovery actions for specific fault types.

Recovery actions should be validated carefully. Terminating processes or restarting services can cause data loss or interrupt important applications.

---

## 🔐 Safety Considerations

* Run the project with the minimum permissions necessary.
* Avoid terminating critical operating system processes.
* Validate recovery actions before enabling automatic execution.
* Keep recovery logs for troubleshooting and evaluation.
* Test potentially disruptive actions in a controlled environment.

---

## 🚧 Current Scope and Future Enhancements

Potential future enhancements include:

* Improved anomaly detection and failure prediction.
* More extensive fault classification.
* A real-time monitoring dashboard.
* Notifications for critical faults.
* More robust recovery policies.
* Recovery success-rate evaluation.
* Improved testing across different workloads and system configurations.

These enhancements represent possible future work, not necessarily completed features.

---

## 🎓 Project Information

**Project Name:** SelfHealOS
**Project Type:** Operating Systems / Machine Learning
**Development Language:** Python

SelfHealOS explores how system monitoring, machine learning, and automated recovery can be combined to improve system reliability.

---

