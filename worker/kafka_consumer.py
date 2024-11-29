
import json
from kafka import KafkaConsumer
from worker.tasks import process_file_task
from config.kafka_config import KAFKA_BROKER_URL, KAFKA_TOPIC

def run_consumer():
    """
    Runs the Kafka consumer to read messages from the topic and send tasks to Celery.
    """
    print("Kafka consumer is now running...")

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER_URL],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="file-processing-group",
        value_deserializer=lambda x: x.decode("utf-8")  # Decode as plain text first
    )

    for message in consumer:
        try:
            raw_message = message.value
            print(f"Raw Message: {raw_message}")

            # Attempt to parse JSON
            file_event = json.loads(raw_message)

            # Validate message content
            file_path = file_event.get("file_path")
            if not file_path:
                print(f"Invalid message received (missing 'file_path'): {raw_message}")
                continue

            # Send task to Celery
            print(f"Sending task to Celery for file: {file_path}")
            process_file_task.delay(file_path)

        except json.JSONDecodeError as e:
            print(f"Invalid message received: {message.value}. Error: {e}")

if __name__ == "__main__":
    run_consumer()
