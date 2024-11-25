import pandas as pd
from scripts.utils import quarantine_file, log_error


def validate_and_transform_data(file_path, normalize=True):
    """
    Validates and transforms the data from the CSV file.
    - Quarantines invalid rows and logs errors.
    - Returns a cleaned DataFrame if validation passes.
    """
    try:
        # Load the data
        df = pd.read_csv(file_path)

        # Required columns
        required_columns = {"ts", "device", "co", "humidity", "light", "lpg", "motion", "smoke", "temp"}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")

        # Parse timestamps and drop invalid rows
        df["ts"] = pd.to_numeric(df["ts"], errors="coerce")
        df["ts"] = pd.to_datetime(df["ts"], unit="s", errors="coerce")
        invalid_ts_rows = df[df["ts"].isnull()]
        if not invalid_ts_rows.empty:
            log_error(file_path, f"Invalid timestamps in rows: {invalid_ts_rows.index.tolist()}")
            df = df.dropna(subset=["ts"])

        # Validate numeric fields
        numeric_fields = ["co", "humidity", "lpg", "smoke", "temp"]
        for field in numeric_fields:
            df[field] = pd.to_numeric(df[field], errors="coerce")
            invalid_rows = df[df[field].isnull()]
            if not invalid_rows.empty:
                log_error(file_path, f"Invalid data in numeric field '{field}' in rows: {invalid_rows.index.tolist()}")
                df = df.dropna(subset=[field])

        # Validate ranges for numeric fields
        field_ranges = {
            "temp": (-50, 50),
            "humidity": (0, 100),
        }
        for field, (min_val, max_val) in field_ranges.items():
            out_of_range = df[(df[field] < min_val) | (df[field] > max_val)]
            if not out_of_range.empty:
                log_error(file_path, f"{field} out of range in rows: {out_of_range.index.tolist()}")
                df = df.drop(out_of_range.index)

        # Normalize sensor values (if enabled)
        if normalize:
            df["temp_normalized"] = (df["temp"] - df["temp"].min()) / (df["temp"].max() - df["temp"].min())

        # Standardize boolean fields
        df["light"] = df["light"].astype(bool)
        df["motion"] = df["motion"].astype(bool)

        print(f"Data from {file_path} validated and transformed successfully.")
        return df

    except Exception as e:
        # Quarantine the file if a critical validation step fails
        quarantine_file(file_path, str(e))
        log_error(file_path, str(e))
        return None
