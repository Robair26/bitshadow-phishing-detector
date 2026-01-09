import os
from datetime import datetime

# Define the log directory
log_dir = "email_logs"
os.makedirs(log_dir, exist_ok=True)

def log_email_details(subject, sender, body, result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_filename = os.path.join(log_dir, f"{timestamp}.txt")

    with open(log_filename, "w", encoding="utf-8") as log_file:
        log_file.write(f"Timestamp: {timestamp}\n")
        log_file.write(f"Subject: {subject}\n")
        log_file.write(f"Sender: {sender}\n")
        log_file.write(f"Body: {body}\n")
        log_file.write(f"Phishing Detection Result: {result}\n")
        log_file.write("-" * 50 + "\n")
