import os
from datetime import datetime

QUARANTINE_DIR = "quarantine"
ERROR_LOG = os.path.join(QUARANTINE_DIR, "errors.log")

# Ensure quarantine directory exists
os.makedirs(QUARANTINE_DIR, exist_ok=True)


def quarantine_file(file_path, reason):
    """
    Moves the file to the quarantine folder and logs the reason for failure.
    """
    quarantine_path = os.path.join(QUARANTINE_DIR, os.path.basename(file_path))
    os.rename(file_path, quarantine_path)
    with open(ERROR_LOG, "a") as log_file:
        log_file.write(f"{datetime.now()}: {file_path} quarantined - {reason}\n")
    print(f"File {file_path} quarantined. Reason: {reason}")


# def log_error(file_path, error_message):
#     """
#     Logs generic errors during processing.
#     """
#     with open(ERROR_LOG, "a") as log_file:
#         log_file.write(f"{datetime.now()}: {file_path} error - {error_message}\n")
#     print(f"Error logged for {file_path}: {error_message}")
def log_error(file_path, error_message, retry_count=None):
    """
    Logs errors during processing, including retry attempts.
    """
    with open(ERROR_LOG, "a") as log_file:
        if retry_count:
            log_file.write(
                f"{datetime.now()}: {file_path} error (retry {retry_count}) - {error_message}\n"
            )
        else:
            log_file.write(f"{datetime.now()}: {file_path} error - {error_message}\n")
    print(f"Error logged for {file_path}: {error_message}")
