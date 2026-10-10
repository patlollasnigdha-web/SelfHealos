import os
import logging
from datetime import datetime
from config.config import LOGS_DIR, SYSTEM_LOG_FILE

def get_system_logger():
    os.makedirs(LOGS_DIR, exist_ok=True)
    logger = logging.getLogger("SelfHealOS")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # File handler
        fh = logging.FileHandler(SYSTEM_LOG_FILE, encoding="utf-8")
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

def log_event(event_type, details=None):
    """
    Log structured events:
    SYSTEM_STARTED, FAULT_DETECTED, FAULT_CLASSIFIED, RECOVERY_STARTED,
    RECOVERY_COMPLETED, RECOVERY_FAILED, RECOVERY_VERIFIED, SYSTEM_STOPPED
    """
    logger = get_system_logger()
    msg = f"EVENT: {event_type}"
    if details:
        if isinstance(details, dict):
            detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
            msg += f" | {detail_str}"
        else:
            msg += f" | {details}"
    logger.info(msg)
