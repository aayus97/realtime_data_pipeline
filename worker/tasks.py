#
# import os
# import time
# from celery import Celery
# from scripts.validate import validate_and_transform_data
# from scripts.database import execute_query
# from scripts.aggregate import calculate_and_store_aggregates
# from scripts.utils import log_error
#
# # Initialize Celery app
# app = Celery("tasks")
# app.config_from_object("config.celeryconfig")  # Load configuration from celeryconfig.py
#
#
# @app.task(bind=True, max_retries=5, default_retry_delay=10)
# def process_file_task(self, file_path):
#     """
#     Celery task to process a file:
#     - Validates and transforms the data.
#     - Inserts valid data into the database.
#     - Calculates and stores aggregated metrics.
#     """
#     try:
#         print(f"Starting task to process file: {file_path}")
#
#         # Step 1: Validate and transform the data
#         transformed_df = validate_and_transform_data(file_path)
#         if transformed_df is None:
#             print(f"Validation failed for file: {file_path}. File quarantined.")
#             return
#
#         # Step 2: Insert valid data into the database
#         query = """
#             INSERT INTO raw_sensor_data (ts, device, co, humidity, light, lpg, motion, smoke, temp, file_name)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         data = [
#             (
#                 row["ts"], row["device"], row["co"], row["humidity"], row["light"],
#                 row["lpg"], row["motion"], row["smoke"], row["temp"], os.path.basename(file_path)
#             )
#             for _, row in transformed_df.iterrows()
#         ]
#         execute_query(query, data)
#         print(f"Data from file {file_path} inserted into the database.")
#
#         # Step 3: Calculate and store aggregated metrics
#         calculate_and_store_aggregates(transformed_df, file_path)
#         print(f"Aggregated metrics for file {file_path} calculated and stored.")
#
#         print(f"Processing of file {file_path} completed successfully.")
#
#     except Exception as e:
#         # Retry the task if an exception occurs
#         print(f"Error processing file {file_path}: {e}")
#         log_error(file_path, str(e))
#         self.retry(exc=e)  # Retry the task
#


import os
import json
from kafka import KafkaConsumer
from celery import Celery
from scripts.validate import validate_and_transform_data
from scripts.database import execute_query
from scripts.aggregate import calculate_and_store_aggregates
from scripts.utils import log_error
from scripts.utils import quarantine_file
from config.kafka_config import KAFKA_BROKER_URL, KAFKA_TOPIC

# Initialize Celery app
app = Celery("tasks")
app.config_from_object("config.celeryconfig")  # Load configuration from celeryconfig.py

# @app.task(bind=True, max_retries=5, default_retry_delay=10)
# def process_file_task(self, file_path):
#     """
#     Celery task to process a file:
#     - Validates and transforms the data.
#     - Inserts valid data into the database.
#     - Calculates and stores aggregated metrics.
#     """
#     try:
#         print(f"Starting task to process file: {file_path}")
#
#         # Step 1: Validate and transform the data
#         transformed_df = validate_and_transform_data(file_path)
#         if transformed_df is None:
#             print(f"Validation failed for file: {file_path}. File quarantined.")
#             return
#
#         # Step 2: Insert valid data into the database
#         query = """
#             INSERT INTO raw_sensor_data (ts, device, co, humidity, light, lpg, motion, smoke, temp, file_name)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         data = [
#             (
#                 row["ts"], row["device"], row["co"], row["humidity"], row["light"],
#                 row["lpg"], row["motion"], row["smoke"], row["temp"], os.path.basename(file_path)
#             )
#             for _, row in transformed_df.iterrows()
#         ]
#         execute_query(query, data)
#         print(f"Data from file {file_path} inserted into the database.")
#
#         # Step 3: Calculate and store aggregated metrics
#         calculate_and_store_aggregates(transformed_df, file_path)
#         print(f"Aggregated metrics for file {file_path} calculated and stored.")
#
#         print(f"Processing of file {file_path} completed successfully.")
#
#     except Exception as e:
#         # Retry the task if an exception occurs
#         print(f"Error processing file {file_path}: {e}")
#         log_error(file_path, str(e))
#         self.retry(exc=e)  # Retry the task
#

# @app.task(bind=True, max_retries=5, default_retry_delay=10)
# def process_file_task(self, file_path):
#     """
#     Celery task to process a file:
#     - Validates and transforms the data.
#     - Inserts valid data into the database.
#     - Calculates and stores aggregated metrics.
#     - Moves invalid files to quarantine if validation fails.
#     """
#     try:
#         print(f"Starting task to process file: {file_path}")
#
#         # Step 1: Validate and transform the data
#         transformed_df = validate_and_transform_data(file_path)
#         if transformed_df is None:
#             reason = f"Validation failed for file: {file_path}"
#             print(reason)
#             quarantine_file(file_path, reason)
#             return  # Stop further processing
#
#         # Step 2: Insert valid data into the database
#         query = """
#             INSERT INTO raw_sensor_data (ts, device, co, humidity, light, lpg, motion, smoke, temp, file_name)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         data = [
#             (
#                 row["ts"], row["device"], row["co"], row["humidity"], row["light"],
#                 row["lpg"], row["motion"], row["smoke"], row["temp"], os.path.basename(file_path)
#             )
#             for _, row in transformed_df.iterrows()
#         ]
#         execute_query(query, data)
#         print(f"Data from file {file_path} inserted into the database.")
#
#         # Step 3: Calculate and store aggregated metrics
#         calculate_and_store_aggregates(transformed_df, file_path)
#         print(f"Aggregated metrics for file {file_path} calculated and stored.")
#
#         print(f"Processing of file {file_path} completed successfully.")
#
#     except Exception as e:
#         # Log the error and move the file to quarantine on failure
#         error_message = f"Error processing file {file_path}: {e}"
#         print(error_message)
#         log_error(file_path, str(e))
#         quarantine_file(file_path, error_message)
#         self.retry(exc=e)  # Retry the task

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

# @app.task
# def kafka_consumer_task():
#     """
#     Celery task that consumes messages from Kafka and triggers file processing.
#     """
#     print("Starting Kafka Consumer...")
#     consumer = KafkaConsumer(
#         KAFKA_TOPIC,
#         bootstrap_servers=[KAFKA_BROKER_URL],
#         auto_offset_reset="earliest",
#         enable_auto_commit=True,
#         group_id="file-processing-group",
#         value_deserializer=lambda v: json.loads(v.decode("utf-8"))
#     )
#     for message in consumer:
#         file_event = message.value
#         file_path = file_event.get("file_path")
#         print(f"Kafka Event Received: {file_event}")  # Log raw Kafka event
#         if file_path:
#             print(f"Sending task to Celery for file: {file_path}")
#             process_file_task.delay(file_path)  # Send the task to Celery
#         else:
#             print(f"Invalid Kafka Event: {file_event}")
#

