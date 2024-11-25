import pandas as pd
import random
import os


def introduce_single_error(df):
    """
    Introduces a single random error into the DataFrame:
    - Drops a random value (simulating missing data).
    - Alters a data type (e.g., replaces a numeric value with a string).
    - Introduces an out-of-range value.

    :param df: Input DataFrame.
    :return: DataFrame with one error introduced and a log of the error.
    """
    corrupted_df = df.copy()
    error_log = None

    # Randomly select a row to corrupt
    row_to_corrupt = random.choice(range(len(corrupted_df)))

    # Randomly choose a type of corruption
    corruption_type = random.choice(["drop", "datatype", "out_of_range"])

    if corruption_type == "drop":
        # Drop a random value in the row
        col_to_null = random.choice([col for col in corrupted_df.columns if col != "ts"])  # Exclude 'ts'
        corrupted_df.at[row_to_corrupt, col_to_null] = None
        error_log = f"Row {row_to_corrupt}: Dropped value in column '{col_to_null}'"

    elif corruption_type == "datatype":
        # Replace a numeric value with a string
        numeric_cols = corrupted_df.select_dtypes(include=["float64", "int64"]).columns
        numeric_cols = [col for col in numeric_cols if col != "ts"]  # Exclude 'ts'
        if len(numeric_cols) > 0:
            col_to_corrupt = random.choice(numeric_cols)
            corrupted_df[col_to_corrupt] = corrupted_df[col_to_corrupt].astype(object)
            corrupted_df.at[row_to_corrupt, col_to_corrupt] = "INVALID"
            error_log = f"Row {row_to_corrupt}: Replaced value in column '{col_to_corrupt}' with 'INVALID'"

    elif corruption_type == "out_of_range":
        # Introduce out-of-range values for temperature
        if "temp" in corrupted_df.columns:
            corrupted_df.at[row_to_corrupt, "temp"] = random.choice([-100, 100])  # Out of valid range
            error_log = f"Row {row_to_corrupt}: Introduced out-of-range value in column 'temp'"

    return corrupted_df, error_log


def split_file_with_errors(file_path, rows_per_file, output_folder="split_files", error_rate=0.1, correct_file_ratio=0.3):
    """
    Splits a CSV file into multiple smaller files and introduces a single error in some files,
    while preserving the 'ts' column without any modification.

    :param file_path: Path to the input CSV file.
    :param rows_per_file: Number of rows per split file.
    :param output_folder: Folder to store the split files.
    :param error_rate: Proportion of rows to corrupt in each split file.
    :param correct_file_ratio: Proportion of files to keep error-free.
    """
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Read the input CSV file with 'ts' as string
    df = pd.read_csv(file_path, dtype={"ts": str})

    # Preserve the 'ts' column exactly as it is
    if "ts" not in df.columns:
        raise ValueError("'ts' column is missing in the input file")

    # Validate that 'ts' is in the original format
    if not pd.api.types.is_string_dtype(df["ts"]):
        raise ValueError("'ts' column must remain in its original format as a string")

    # Calculate the number of splits needed
    total_rows = len(df)
    num_files = (total_rows // rows_per_file) + (1 if total_rows % rows_per_file != 0 else 0)

    # Randomly decide which files will be error-free
    correct_file_count = int(num_files * correct_file_ratio)
    correct_file_indices = set(random.sample(range(num_files), correct_file_count))

    # Split and save each chunk
    for i in range(num_files):
        start_row = i * rows_per_file
        end_row = start_row + rows_per_file
        split_df = df[start_row:end_row]

        # Introduce a single error only if this file is not marked as error-free
        error_log = None
        if i not in correct_file_indices:
            split_df, error_log = introduce_single_error(split_df)

        # Save the split file
        output_file = os.path.join(output_folder, f"split_{i + 1}.csv")
        split_df.to_csv(output_file, index=False, quoting=1)  # Use quoting to preserve exact string format
        status = "error-free" if i in correct_file_indices else "with errors"
        print(f"Created file: {output_file} ({status})")

        # Print error log for the file
        if error_log:
            print(f"Error introduced in {output_file}: {error_log}")


# Example usage
split_file_with_errors(
    "split_sensor_files/sensor.csv",
    rows_per_file=10000,
    output_folder="split_sensor_with_errors",
    error_rate=0.1,
    correct_file_ratio=0.3,  # 30% of the files will be error-free
)
