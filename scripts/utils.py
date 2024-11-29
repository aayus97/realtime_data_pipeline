import os
from shutil import move
from datetime import datetime

QUARANTINE_DIR = "quarantine"
ERROR_LOG = f"{QUARANTINE_DIR}/errors.log"

# Ensure quarantine directory exists
os.makedirs(QUARANTINE_DIR, exist_ok=True)

def quarantine_file(file_path, reason):
    """
    Moves the file to the quarantine folder and logs the reason for failure.
    """
    try:
        quarantine_path = os.path.join(QUARANTINE_DIR, os.path.basename(file_path))
        move(file_path, quarantine_path)
        print(f"File {file_path} moved to quarantine. Reason: {reason}")
    except FileNotFoundError:
        print(f"File {file_path} not found for quarantining.")

def log_error(file_path, error_message):
    """
    Logs errors during processing, including detailed messages.
    """
    with open(ERROR_LOG, "a") as log_file:
        log_file.write(f"{datetime.now()}: {file_path} error - {error_message}\n")
    print(f"Error logged for {file_path}: {error_message}")