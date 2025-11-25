import logging
import os
from datetime import datetime

LOG_FILE = "error.log"

# Configure root logger for module usage
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def log_exception(context, exc):
    msg = f"{context} - {type(exc).__name__}: {str(exc)}"
    logging.exception(msg)

def log_info(msg):
    logging.info(msg)

def get_log_path():
    return os.path.abspath(LOG_FILE)
