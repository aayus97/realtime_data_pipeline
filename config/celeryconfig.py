# celeryconfig.py

from kombu import Exchange, Queue

# Broker and backend configuration w/o docker
broker_url = "redis://localhost:6379/0"  # Redis as the broker
result_backend = "redis://localhost:6379/0"  # Redis for result storage

# # docker_specific config
# broker_url = "redis://redis:6379/0"
# result_backend = "redis://redis:6379/0"


# Task serialization settings
task_serializer = "json"  # Serialize tasks as JSON
result_serializer = "json"  # Serialize results as JSON
accept_content = ["json"]  # Only accept JSON content

# Timezone settings
timezone = "UTC"  # Set the timezone
enable_utc = True  # Use UTC for timestamps

# Task queues configuration
task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),  # Default queue
)


task_routes = {
    "worker.tasks.process_file_task": {"queue": "default"},
    "worker.tasks.kafka_consumer_task": {"queue": "default"},
}

task_annotations = {
    "worker.tasks.process_file_task": {
        "max_retries": 5,  # Maximum number of retries for this task
        "retry_delay": 10,  # Delay (in seconds) between retries
    },
}

# Worker concurrency
worker_concurrency = 4  # Number of worker processes (adjust based on system resources)

# Worker prefetch settings (optional)
# Limits the number of tasks a worker fetches before processing
worker_prefetch_multiplier = 1  # Useful for tasks with varying execution times

# Result expiration settings (optional)
result_expires = 3600  # Task results expire after 1 hour

# Task rate limiting (optional)
# Limits the number of tasks processed by a worker per second
worker_task_limit = None  # Example: "10/s" for 10 tasks per second
