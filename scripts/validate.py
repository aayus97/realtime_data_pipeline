import pandas as pd
from scripts.utils import quarantine_file
from datetime import datetime

# Quarantine directory and error log path
QUARANTINE_DIR = "quarantine"
ERROR_LOG = f"{QUARANTINE_DIR}/errors.log"

def log_and_quarantine(file_path, error_message):
    """
    Handles logging and quarantining of a file.
    Logs only once and moves the file to the quarantine folder.
    """
    full_message = f"{file_path} quarantined - {error_message}"
    # Log the message
    with open(ERROR_LOG, "a") as log_file:
        log_file.write(f"{datetime.now()}: {full_message}\n")
    print(full_message)  # For debugging

    # Quarantine the file
    try:
        quarantine_file(file_path, error_message)
    except Exception as e:
        fail_message = f"Failed to quarantine file {file_path} - {e}. Reason: {error_message}"
        with open(ERROR_LOG, "a") as log_file:
            log_file.write(f"{datetime.now()}: {fail_message}\n")
        print(fail_message)

def validate_and_transform_data(file_path, normalize=True):
    """
    Validates and transforms the data from the CSV file.
    Logs all validation failures before quarantining the file if necessary.
    """
    validation_errors = []  # Collect all validation errors

    try:
        print(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)

        # Check required columns
        required_columns = {"ts", "device", "co", "humidity", "light", "lpg", "motion", "smoke", "temp"}
        if not required_columns.issubset(df.columns):
            missing_cols = required_columns - set(df.columns)
            validation_errors.append(f"Missing required columns: {missing_cols}")

        # Validate timestamps
        df["ts"] = pd.to_numeric(df["ts"], errors="coerce")
        df["ts"] = pd.to_datetime(df["ts"], unit="s", errors="coerce")
        invalid_ts_rows = df[df["ts"].isnull()]
        if not invalid_ts_rows.empty:
            invalid_indices = invalid_ts_rows.index.tolist()
            invalid_values = invalid_ts_rows["ts"].tolist()
            validation_errors.append(
                f"Invalid timestamps in rows: {invalid_indices} (values: {invalid_values})"
            )

        # Validate numeric fields
        numeric_fields = ["co", "humidity", "lpg", "smoke", "temp"]
        for field in numeric_fields:
            df[field] = pd.to_numeric(df[field], errors="coerce")
            invalid_rows = df[df[field].isnull()]
            if not invalid_rows.empty:
                invalid_indices = invalid_rows.index.tolist()
                validation_errors.append(
                    f"Invalid data in numeric field '{field}' in rows: {invalid_indices}"
                )

        # Validate ranges for numeric fields
        field_ranges = {
            "temp": (-50, 50),
            "humidity": (0, 100),
            "co": (0, 1),
            "lpg": (0, 1),
            "smoke": (0, 1),
        }
        for field, (min_val, max_val) in field_ranges.items():
            out_of_range = df[(df[field] < min_val) | (df[field] > max_val)]
            if not out_of_range.empty:
                invalid_indices = out_of_range.index.tolist()
                validation_errors.append(
                    f"{field} out of range in rows: {invalid_indices}"
                )

        # If there are validation errors, log them and quarantine the file
        if validation_errors:
            error_message = "; ".join(validation_errors)
            log_and_quarantine(file_path, error_message)
            return None

        # Normalize sensor values (if enabled)
        if normalize:
            for field in numeric_fields:
                df[f"{field}_normalized"] = (df[field] - df[field].min()) / (df[field].max() - df[field].min())

        # Standardize boolean fields
        df["light"] = df["light"].astype(bool)
        df["motion"] = df["motion"].astype(bool)

        print(f"Data from {file_path} validated and transformed successfully.")
        return df

    except Exception as e:
        # Log critical errors and quarantine the file
        log_and_quarantine(file_path, f"Critical validation error: {str(e)}")
        return None

