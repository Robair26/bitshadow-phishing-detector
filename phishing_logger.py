import os
import logging
from datetime import datetime

# Directory for storing logs
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure file-based logging
log_file_path = os.path.join(LOG_DIR, f"phishing_logs_{datetime.now().strftime('%Y%m%d')}.log")
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
file_handler.setLevel(logging.INFO)

# Get global logger and add the file handler
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# Function to log results

def log_detection_result(email_text, result):
    log_entry = f"RESULT: {result} | TEXT: {email_text[:150]}{'...' if len(email_text) > 150 else ''}"
    logger.info(log_entry)
