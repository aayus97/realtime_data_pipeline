from celery import Celery
from scripts.validate import validate_and_transform_data
from scripts.database import execute_query
from scripts.aggregate import calculate_and_store_aggregates
from scripts.utils import quarantine_file


app = Celery("tasks")
app.config_from_object("config.celeryconfig")

@app.task(bind=True, max_retries=5, default_retry_delay=10)
def process_file_task(self, file_path):
    """
    Celery task to process a file:
    - Validates and transforms the data.
    - Inserts valid data into the database.
    - Calculates and stores aggregated metrics.
    """
    try:
        print(f"Starting task to process file: {file_path}")

        # Step 1: Validate and transform the data
        transformed_df = validate_and_transform_data(file_path)
        if transformed_df is None:
            print(f"Validation failed for file: {file_path}")
            return

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
        execute_query(query, data)
        print(f"Data from file {file_path} inserted into the database.")

        # Step 3: Calculate and store aggregated metrics
        calculate_and_store_aggregates(transformed_df, file_path)
        print(f"Aggregated metrics for file {file_path} calculated and stored.")

        print(f"Processing of file {file_path} completed successfully.")

    except Exception as e:
        # Log error and retry the task
        quarantine_file(file_path, f"Task processing failed: {str(e)}")
        self.retry(exc=e)
