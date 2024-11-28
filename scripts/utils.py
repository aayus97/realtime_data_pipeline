

# import os
# from shutil import move
# from datetime import datetime
#
# QUARANTINE_DIR = "quarantine"
# ERROR_LOG = os.path.join(QUARANTINE_DIR, "errors.log")
#
# # Ensure quarantine directory exists
# os.makedirs(QUARANTINE_DIR, exist_ok=True)
#
# def quarantine_file(file_path, reason):
#     """
#     Moves the file to the quarantine folder and logs the reason for failure.
#     """
#     try:
#         quarantine_path = os.path.join(QUARANTINE_DIR, os.path.basename(file_path))
#         if os.path.exists(file_path):  # Check if the file exists before moving
#             move(file_path, quarantine_path)  # Use shutil.move to handle moving files
#             with open(ERROR_LOG, "a") as log_file:
#                 log_file.write(f"{datetime.now()}: {file_path} quarantined - {reason}\n")
#             print(f"File {file_path} moved to quarantine. Reason: {reason}")
#         else:
#             print(f"File {file_path} does not exist, cannot quarantine.")
#     except Exception as e:
#         print(f"Failed to quarantine file {file_path}. Error: {e}")
#         with open(ERROR_LOG, "a") as log_file:
#             log_file.write(f"{datetime.now()}: Failed to quarantine {file_path} - {reason}. Error: {e}\n")
#

# import os
# from shutil import move
# from datetime import datetime
#
# QUARANTINE_DIR = "quarantine"
# ERROR_LOG = os.path.join(QUARANTINE_DIR, "errors.log")
#
# # Ensure quarantine directory exists
# os.makedirs(QUARANTINE_DIR, exist_ok=True)
#
# def quarantine_file(file_path, reason):
#     """
#     Moves the file to the quarantine folder and logs the reason for failure.
#     """
#     try:
#         quarantine_path = os.path.join(QUARANTINE_DIR, os.path.basename(file_path))
#         if os.path.exists(file_path):  # Check if the file exists before moving
#             move(file_path, quarantine_path)
#             with open(ERROR_LOG, "a") as log_file:
#                 log_file.write(f"{datetime.now()}: {file_path} quarantined - {reason}\n")
#             print(f"File {file_path} moved to quarantine. Reason: {reason}")
#         else:
#             print(f"File {file_path} does not exist, cannot quarantine.")
#     except Exception as e:
#         with open(ERROR_LOG, "a") as log_file:
#             log_file.write(f"{datetime.now()}: Failed to quarantine {file_path} - {reason}. Error: {e}\n")
#         print(f"Failed to quarantine file {file_path}. Error: {e}")
#
#
#
# def log_error(file_path, error_message, retry_count=None):
#     """
#     Logs errors during processing, including retry attempts.
#     """
#     with open(ERROR_LOG, "a") as log_file:
#         if retry_count:
#             log_file.write(
#                 f"{datetime.now()}: {file_path} error (retry {retry_count}) - {error_message}\n"
#             )
#         else:
#             log_file.write(f"{datetime.now()}: {file_path} error - {error_message}\n")
#     print(f"Error logged for {file_path}: {error_message}")

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