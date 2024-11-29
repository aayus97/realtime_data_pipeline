[//]: # (# Project Overview)

[//]: # ()
[//]: # ()
[//]: # (This project involves a modular and asynchronous system for monitoring, processing, and validating CSV files using Kafka, Celery, Redis, and PostgreSQL. Below is a detailed breakdown of each component and its role in the system.)

[//]: # ()
[//]: # ()
[//]: # (## 1. Kafka Producer)

[//]: # ()
[//]: # ()
[//]: # (The Kafka producer is responsible for monitoring a directory for new CSV files and sending information about them to a Kafka topic.)

[//]: # ()
[//]: # ()
[//]: # (### Flow)

[//]: # ()
[//]: # (- **Script**: `kafka_producer.py`)

[//]: # ()
[//]: # (- **Functionality**:)

[//]: # ()
[//]: # (  - Watches a directory for new files using a loop.)

[//]: # ()
[//]: # (  - When a new CSV file is detected, sends a JSON message to the Kafka topic `file_events`.)

[//]: # ()
[//]: # ()
[//]: # (### Example JSON Message)

[//]: # ()
[//]: # (```json)

[//]: # ()
[//]: # ({)

[//]: # ()
[//]: # (  "file_path": "data/split_1.csv",)

[//]: # ()
[//]: # (  "file_name": "split_1.csv")

[//]: # ()
[//]: # (})

[//]: # ()
[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (### Tools Used)

[//]: # ()
[//]: # (- `os` module to monitor the directory.)

[//]: # ()
[//]: # (- `KafkaProducer` from the `kafka-python` library to send messages.)

[//]: # ()
[//]: # ()
[//]: # (## 2. Kafka Consumer)

[//]: # ()
[//]: # ()
[//]: # (The Kafka consumer listens to the Kafka topic `file_events` and processes messages as they arrive.)

[//]: # ()
[//]: # ()
[//]: # (### Key Components)

[//]: # ()
[//]: # (- **Script**: `worker/kafka_consumer.py`)

[//]: # ()
[//]: # (- **Functionality**:)

[//]: # ()
[//]: # (  - Consumes messages from the Kafka topic.)

[//]: # ()
[//]: # (  - Parses each message from JSON string to Python dictionary.)

[//]: # ()
[//]: # (  - Validates the content for a valid file path.)

[//]: # ()
[//]: # (  - Sends tasks to Celery if the file path is valid using:)

[//]: # ()
[//]: # (    ```python)

[//]: # ()
[//]: # (    process_file_task.delay&#40;file_path&#41;)

[//]: # ()
[//]: # (    ```)

[//]: # ()
[//]: # (  - Logs an error if the message is invalid.)

[//]: # ()
[//]: # (### Task Workflow)

[//]: # ()
[//]: # ()
[//]: # (- **Validation**:)

[//]: # ()
[//]: # (  - Calls `validate_and_transform_data&#40;file_path&#41;` from `scripts/validate.py`.)

[//]: # ()
[//]: # (  - Ensures required columns are present, timestamps are valid, and numeric fields are within range.)

[//]: # ()
[//]: # (  - Quarantines file and logs an error if validation fails.)

[//]: # ()
[//]: # (  - Returns cleaned DataFrame if validation passes.)

[//]: # ()
[//]: # ()
[//]: # (- **Database Insertion**:)

[//]: # ()
[//]: # (  - Inserts validated data into the `raw_sensor_data` table in PostgreSQL using `psycopg2`.)

[//]: # ()
[//]: # ()
[//]: # (- **Aggregation**:)

[//]: # ()
[//]: # (  - Calculates metrics &#40;e.g., min, max, mean&#41; for sensor data.)

[//]: # ()
[//]: # (  - Inserts metrics into `aggregated_metrics` table.)

[//]: # ()
[//]: # ()
[//]: # (### Error Handling)

[//]: # ()
[//]: # (- Logs errors, retries tasks if needed, or quarantines files on validation failure.)

[//]: # ()
[//]: # ()
[//]: # (## 4. Quarantine Mechanism)

[//]: # ()
[//]: # ()
[//]: # (Files that fail validation are moved to a quarantine directory.)

[//]: # ()
[//]: # ()
[//]: # (### Script)

[//]: # ()
[//]: # (- `scripts/utils.py`)

[//]: # ()
[//]: # ()
[//]: # (### Functions)

[//]: # ()
[//]: # (- **`quarantine_file&#40;&#41;`**: Moves file to quarantine folder and logs details.)

[//]: # ()
[//]: # (- **`log_error&#40;&#41;`**: Writes error messages to a log file.)

[//]: # ()
[//]: # ()
[//]: # (## 5. Database Interaction)

[//]: # ()
[//]: # ()
[//]: # (Data is inserted into PostgreSQL using SQL queries with `psycopg2`.)

[//]: # ()
[//]: # ()
[//]: # (### Key Functions)

[//]: # ()
[//]: # (- **`connect_to_db&#40;&#41;`**: Establishes database connection using credentials from `db/config.py`.)

[//]: # ()
[//]: # (- **`execute_query&#40;query, data&#41;`**: Executes parameterized queries with retry logic using the `tenacity` library.)

[//]: # ()
[//]: # ()
[//]: # (### Tables)

[//]: # ()
[//]: # (- **`raw_sensor_data`**: Stores raw sensor data.)

[//]: # ()
[//]: # (- **`aggregated_metrics`**: Stores calculated metrics for each device and sensor type.)

[//]: # ()
[//]: # ()
[//]: # (## 6. Celery Worker)

[//]: # ()
[//]: # ()
[//]: # (The Celery worker executes tasks sent by the Kafka consumer.)

[//]: # ()
[//]: # ()
[//]: # (### Command to Start Worker)

[//]: # ()
[//]: # (```bash)

[//]: # ()
[//]: # (celery -A worker.tasks worker --loglevel=info)

[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (### How It Works)

[//]: # ()
[//]: # (- Listens for tasks from Redis broker.)

[//]: # ()
[//]: # (- Executes tasks asynchronously.)

[//]: # ()
[//]: # ()
[//]: # (### Worker Log Example)

[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # ([INFO/MainProcess] Task worker.tasks.process_file_task[task_id] received)

[//]: # ()
[//]: # ([WARNING/ForkPoolWorker-2] Data from data/split_1.csv validated and transformed successfully.)

[//]: # ()
[//]: # ([INFO/MainProcess] Task worker.tasks.process_file_task[task_id] succeeded in 1.2s)

[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # ()
[//]: # (## 7. Redis as a Message Broker)

[//]: # ()
[//]: # ()
[//]: # (Redis acts as an intermediary between the Kafka consumer and Celery worker.)

[//]: # ()
[//]: # ()
[//]: # (- Kafka consumer sends tasks to Redis.)

[//]: # ()
[//]: # (- Celery worker retrieves tasks from Redis and executes them.)

[//]: # ()
[//]: # ()
[//]: # (## Code Flow in Action)

[//]: # ()
[//]: # ()
[//]: # (1. Producer sends messages to Kafka:)

[//]: # ()
[//]: # (   ```json)

[//]: # ()
[//]: # (   {"file_path": "data/split_1.csv", "file_name": "split_1.csv"})

[//]: # ()
[//]: # (   ```)

[//]: # ()
[//]: # (Consumer reads the message, validates it, and sends a task to Celery:)

[//]: # ()
[//]: # (```python)

[//]: # ()
[//]: # (process_file_task.delay&#40;"data/split_1.csv"&#41;)

[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (Worker processes the task:)

[//]: # ()
[//]: # (- Validates the file.)

[//]: # ()
[//]: # (- Inserts valid data into the database.)

[//]: # ()
[//]: # (- Calculates and stores aggregated metrics.)

[//]: # ()
[//]: # (- Quarantines invalid files.)

[//]: # ()
[//]: # ()
[//]: # (# Build the images)

[//]: # (docker-compose build)

[//]: # ()
[//]: # (# Start the containers)

[//]: # (docker-compose up)


# **File Events Processing Workflow with Kafka, Celery, Redis, and PostgreSQL**

This project implements a modular, asynchronous system for monitoring, processing, validating, and storing data from CSV files. It leverages **Kafka**, **Celery**, **Redis**, and **PostgreSQL** for event-driven processing and database storage, making it a scalable and robust architecture for handling large volumes of data.

---

## **Table of Contents**
1. [Features](#features)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [How to Run the Workflow](#how-to-run-the-workflow)
   - [Start Zookeeper and Kafka](#1-start-zookeeper-and-kafka)
   - [Verify Zookeeper and Kafka](#2-verify-zookeeper-and-kafka)
   - [Create Kafka Topic](#3-create-kafka-topic)
   - [Run the Kafka Producer](#4-run-the-kafka-producer)
   - [Run the Kafka Consumer](#5-run-the-kafka-consumer)
   - [Start Redis Server](#6-start-redis-server)
   - [Start Celery Worker](#7-start-celery-worker)
5. [Testing the Workflow](#testing-the-workflow)
6. [Project Architecture](#project-architecture)
---

## **Features**

- Watches a directory (`data/`) for new CSV files.
- Publishes file events to Kafka topics.
- Consumes Kafka events and validates the CSV files.
- Processes tasks asynchronously using Celery workers.
- Inserts validated data into a **PostgreSQL** database.
- Calculates and stores aggregated metrics in a dedicated database table.
- Quarantines invalid files for further inspection.

---

## **System Requirements**

Ensure the following tools and packages are installed on your system:

1. **Kafka**: Distributed streaming platform for event processing.
2. **Zookeeper**: Required by Kafka for cluster management.
3. **Redis**: Acts as the Celery message broker.
4. **PostgreSQL**: For storing and querying validated data and metrics.
5. **Python 3.8+**: Programming language for the Kafka producer, consumer, and Celery tasks.
6. **Kafka-Python**: Python client for Kafka communication.
7. **Celery**: Distributed task queue for asynchronous processing.

---

## **Installation**

1. **Clone the Repository**:
    
    ```bash
    
    git clone https://github.com/your-repo/file-events-processing.git
    cd file-events-processing
    
    ```
    
2. **Install Python Dependencies**:
    - Create and activate a virtual environment:
        
        ```bash
        
        python3 -m venv venv
        source venv/bin/activate
        
        ```
        
    - Install dependencies:
        
        ```bash
        
        pip install -r requirements.txt
        
        ```
        
3. **Install Kafka**:
    - Using Homebrew on macOS:
        
        ```bash
        
        brew install kafka
        
        ```
        
4. **Install Redis**:
    - Using Homebrew on macOS:
        
        ```bash
        
        brew install redis
        
        ```
        
5. **Install PostgreSQL**:
    - Using Homebrew:
        
        ```bash
        
        brew install postgresql
        
        ```
        

---

## **Project Overview**

This project involves multiple components working together to create a reliable and scalable pipeline for file-based event processing. Below is a breakdown of each component:

### **1. Kafka Producer**

The Kafka producer monitors a directory (`data/`) for new CSV files and sends file information to a Kafka topic.

- **Script**: `kafka_producer.py`
- **Functionality**:
    - Watches the directory for new files.
    - Sends JSON messages to the Kafka topic `file_events` when a new file is detected.

### Example JSON Message:

```json

{
  "file_path": "data/split_1.csv",
  "file_name": "split_1.csv"
}

```

---

### **2. Kafka Consumer**

The Kafka consumer listens to the `file_events` topic, validates the file paths, and sends processing tasks to Celery.

- **Script**: `worker/kafka_consumer.py`
- **Functionality**:
    - Consumes messages from the Kafka topic.
    - Validates file paths and sends tasks to Celery for processing.
    - Logs errors or quarantines invalid files.

### Task Workflow:

1. **Validation**:
    - Ensures required columns are present, timestamps are valid, and numeric fields are within range.
    - Invalid files are quarantined.
2. **Database Insertion**:
    - Inserts validated data into the `raw_sensor_data` table in PostgreSQL.
3. **Aggregation**:
    - Calculates metrics (e.g., min, max, mean) and stores them in the `aggregated_metrics` table.

---

### **3. Celery Worker**

The Celery worker executes tasks sent by the Kafka consumer. It performs the following:

- **Validation**: Cleans and validates the CSV data.
- **Database Insertion**: Inserts validated data into PostgreSQL.
- **Aggregation**: Calculates metrics for the data and stores them.

### Command to Start the Worker:

```bash

celery -A worker.tasks worker --loglevel=info

```

### Example Worker Logs:

```css

[INFO/MainProcess] Task worker.tasks.process_file_task[task_id] received
[WARNING/ForkPoolWorker-2] Data from data/split_1.csv validated and transformed successfully.
[INFO/MainProcess] Task worker.tasks.process_file_task[task_id] succeeded in 1.2s

```

---

### **4. Database Interaction**

The PostgreSQL database is used to store validated data and aggregated metrics.

- **Tables**:
    - `raw_sensor_data`: Stores raw sensor data.
    - `aggregated_metrics`: Stores calculated metrics for each device and sensor type.
- **Key Functions**:
    - `connect_to_db()`: Establishes the database connection.
    - `execute_query(query, data)`: Executes SQL queries with retry logic using `tenacity`.

---

### **5. Quarantine Mechanism**

Files that fail validation are moved to a quarantine directory for inspection.

- **Script**: `scripts/utils.py`
- **Functions**:
    - `quarantine_file()`: Moves invalid files to the quarantine folder.
    - `log_error()`: Logs error messages for invalid files.

---

### **6. Redis as a Message Broker**

Redis acts as an intermediary between the Kafka consumer and the Celery worker.

- Kafka consumer sends tasks to Redis.
- Celery worker retrieves tasks from Redis and processes them asynchronously.

---

## **How to Run the Workflow**

### **1. Start Zookeeper and Kafka**

- Start Zookeeper:
    
    ```bash
    
    /opt/homebrew/opt/kafka/bin/zookeeper-server-start /opt/homebrew/etc/kafka/zookeeper.properties
    
    ```
    
- Start Kafka:
    
    ```bash
    
    /opt/homebrew/opt/kafka/bin/kafka-server-start /opt/homebrew/etc/kafka/server.properties
    
    ```
    

### **2. Verify Zookeeper and Kafka**

```bash

nc -z localhost 2181 && echo "Zookeeper is running"
nc -z localhost 9092 && echo "Kafka is running"

```

### **3. Create Kafka Topic**

```bash

kafka-topics --create --topic file_events --bootstrap-server localhost:9092 --replication-factor 1 --partitions 3

```

### **4. Run the Kafka Producer**

```bash

python producer/kafka_producer.py

```

### **5. Run the Kafka Consumer**

```bash

python -m worker.kafka_consumer

```

### **6. Start Redis Server**

```bash

redis-server

```

### **7. Start Celery Worker**

```bash

celery -A worker.tasks worker --loglevel=info

```

---

## **Testing the Workflow**

1. Add a new CSV file to the `data/` directory.
2. Verify Kafka messages using:
    
    ```bash
    
    kafka-console-consumer --topic file_events --from-beginning --bootstrap-server localhost:9092
    
    ```
    
3. Check Celery logs for file validation and database insertion.

---

## **Folder Structure**

```bash
file-events-processing/
├── config/                         # Configuration files for the pipeline
│   ├── celeryconfig.py             # Celery configuration
│   ├── db_config.py                # Database connection settings
│   ├── kafka_config.py             # Kafka producer/consumer configuration
│   └── pipeline_config.json        # General pipeline configuration in JSON format
├── data/                           # Directory to monitor for new CSV files
├── db/                             # Database-related scripts or files (e.g., migrations, schema)
├── producer/                       # Kafka producer module
│   ├── __init__.py                 # Module initialization
│   └── kafka_producer.py           # Kafka producer script for sending events
├── quarantine/                     # Directory for storing quarantined files
├── scripts/                        # Utility and task-specific scripts
│   ├── __init__.py                 # Module initialization
│   ├── aggregate.py                # Data aggregation logic (e.g., min, max, mean)
│   ├── database.py                 # Database interaction utilities
│   ├── monitor.py                  # Directory monitoring logic
│   ├── utils.py                    # General utility functions (e.g., file handling, logging)
│   └── validate.py                 # Data validation and cleaning logic
├── split_sensor_files/             # Directory for split files ready for processing
├── split_sensor_with_errors/       # Directory for split files with errors
├── worker/                         # Celery worker module for processing tasks
│   ├── __init__.py                 # Module initialization
│   ├── kafka_consumer.py           # Kafka consumer script for reading events
│   └── tasks.py                    # Celery tasks for file validation, database insertion, etc.
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation

```

## **Conclusion**

This project demonstrates a scalable, event-driven architecture for file-based workflows. It leverages Kafka for event streaming, Celery for distributed task processing, and Redis as a broker. With this setup, you can easily handle large volumes of file-based events in a distributed and asynchronous manner.