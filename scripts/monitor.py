import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from scripts.validate import validate_and_transform_data
from scripts.aggregate import calculate_and_store_aggregates
from scripts.utils import log_error
from db.config import DB_CONFIG
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import psycopg2


class FileHandler(FileSystemEventHandler):
    """
    Event handler for detecting new files in the monitored folder.
    """
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".csv"):
            print(f"New CSV file detected: {event.src_path}")
            try:
                process_file(event.src_path)
            except Exception as e:
                print(f"Failed to process file {event.src_path}: {e}")
                log_error(event.src_path, str(e))


@retry(
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_fixed(5)  # Wait 5 seconds between retries
)
def process_file(file_path):
    """
    Processes a single file:
    - Validates and transforms the data.
    - Stores valid data in the database.
    - Calculates and stores aggregated metrics.
    """
    print(f"Processing file: {file_path}")

    # Step 1: Validate and transform the data
    transformed_df = validate_and_transform_data(file_path)
    if transformed_df is None:
        # File has been quarantined due to validation failure
        return

    try:
        # Step 2: Insert valid data into the database
        query = """
            INSERT INTO raw_sensor_data (ts, device, co, humidity, light, lpg, motion, smoke, temp, file_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = [
            (
                row["ts"], row["device"], row["co"], row["humidity"], row["light"],
                row["lpg"], row["motion"], row["smoke"], row["temp"], os.path.basename(file_path)
            )
            for _, row in transformed_df.iterrows()
        ]
        execute_query_with_retry(query, data)
        print(f"Raw data from {file_path} inserted into the database.")

        # Step 3: Calculate and store aggregated metrics
        calculate_and_store_aggregates(transformed_df, file_path)
        print(f"Aggregated metrics for {file_path} calculated and stored.")

        print(f"Processing of {file_path} completed successfully.")

    except Exception as e:
        log_error(file_path, str(e))
        raise  # Allow retry logic to handle it


@retry(
    stop=stop_after_attempt(5),  # Retry up to 5 times
    wait=wait_fixed(5),  # Wait 5 seconds between retries
    retry=retry_if_exception_type(psycopg2.OperationalError)  # Retry only on OperationalError
)
def execute_query_with_retry(query, data):
    """
    Executes a SQL query with retries on transient failures.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # Use DB_CONFIG from db.config
        cursor = conn.cursor()
        cursor.executemany(query, data)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error executing query: {e}")
        raise  # Reraise exception for retry


def monitor_directory(folder_path="data", interval=5):
    """
    Monitors the specified folder for new CSV files and triggers processing.
    :param folder_path: Path to the folder to monitor.
    :param interval: Time in seconds between scans for new files.
    """
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

    print(f"Monitoring folder: {folder_path} for new CSV files...")

    # Initialize the watchdog observer
    observer = Observer()
    event_handler = FileHandler()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(interval)  # Keep the script running
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    monitor_directory(interval=5)
