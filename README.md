# Project Overview

This project involves a modular and asynchronous system for monitoring, processing, and validating CSV files using Kafka, Celery, Redis, and PostgreSQL. Below is a detailed breakdown of each component and its role in the system.

## 1. Kafka Producer

The Kafka producer is responsible for monitoring a directory for new CSV files and sending information about them to a Kafka topic.

### Flow
- **Script**: `kafka_producer.py`
- **Functionality**:
  - Watches a directory for new files using a loop.
  - When a new CSV file is detected, sends a JSON message to the Kafka topic `file_events`.

### Example JSON Message
```json
{
  "file_path": "data/split_1.csv",
  "file_name": "split_1.csv"
}

```
### Tools Used
- `os` module to monitor the directory.
- `KafkaProducer` from the `kafka-python` library to send messages.

## 2. Kafka Consumer

The Kafka consumer listens to the Kafka topic `file_events` and processes messages as they arrive.

### Key Components
- **Script**: `worker/kafka_consumer.py`
- **Functionality**:
  - Consumes messages from the Kafka topic.
  - Parses each message from JSON string to Python dictionary.
  - Validates the content for a valid file path.
  - Sends tasks to Celery if the file path is valid using:
    ```python
    process_file_task.delay(file_path)
    ```
  - Logs an error if the message is invalid.
### Task Workflow

- **Validation**:
  - Calls `validate_and_transform_data(file_path)` from `scripts/validate.py`.
  - Ensures required columns are present, timestamps are valid, and numeric fields are within range.
  - Quarantines file and logs an error if validation fails.
  - Returns cleaned DataFrame if validation passes.

- **Database Insertion**:
  - Inserts validated data into the `raw_sensor_data` table in PostgreSQL using `psycopg2`.

- **Aggregation**:
  - Calculates metrics (e.g., min, max, mean) for sensor data.
  - Inserts metrics into `aggregated_metrics` table.

### Error Handling
- Logs errors, retries tasks if needed, or quarantines files on validation failure.

## 4. Quarantine Mechanism

Files that fail validation are moved to a quarantine directory.

### Script
- `scripts/utils.py`

### Functions
- **`quarantine_file()`**: Moves file to quarantine folder and logs details.
- **`log_error()`**: Writes error messages to a log file.

## 5. Database Interaction

Data is inserted into PostgreSQL using SQL queries with `psycopg2`.

### Key Functions
- **`connect_to_db()`**: Establishes database connection using credentials from `db/config.py`.
- **`execute_query(query, data)`**: Executes parameterized queries with retry logic using the `tenacity` library.

### Tables
- **`raw_sensor_data`**: Stores raw sensor data.
- **`aggregated_metrics`**: Stores calculated metrics for each device and sensor type.

## 6. Celery Worker

The Celery worker executes tasks sent by the Kafka consumer.

### Command to Start Worker
```bash
celery -A worker.tasks worker --loglevel=info
```
### How It Works
- Listens for tasks from Redis broker.
- Executes tasks asynchronously.

### Worker Log Example
```
[INFO/MainProcess] Task worker.tasks.process_file_task[task_id] received
[WARNING/ForkPoolWorker-2] Data from data/split_1.csv validated and transformed successfully.
[INFO/MainProcess] Task worker.tasks.process_file_task[task_id] succeeded in 1.2s
```

## 7. Redis as a Message Broker

Redis acts as an intermediary between the Kafka consumer and Celery worker.

- Kafka consumer sends tasks to Redis.
- Celery worker retrieves tasks from Redis and executes them.

## Code Flow in Action

1. Producer sends messages to Kafka:
   ```json
   {"file_path": "data/split_1.csv", "file_name": "split_1.csv"}
   ```
Consumer reads the message, validates it, and sends a task to Celery:
```python
process_file_task.delay("data/split_1.csv")
```
Worker processes the task:
- Validates the file.
- Inserts valid data into the database.
- Calculates and stores aggregated metrics.
- Quarantines invalid files.


# Build the images
docker-compose build

# Start the containers
docker-compose up
