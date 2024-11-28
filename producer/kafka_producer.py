import os
import time
import json
from kafka import KafkaProducer
from config.kafka_config import KAFKA_BROKER_URL, KAFKA_TOPIC

def monitor_and_publish(folder_path="data"):
    """
    Monitors the folder for new files and publishes events to Kafka.
    """
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    print(f"Monitoring folder: {folder_path}")
    seen_files = set()

    while True:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if file_name not in seen_files and file_path.endswith(".csv"):
                print(f"New file detected: {file_path}")
                producer.send(KAFKA_TOPIC, {"file_path": file_path, "file_name": file_name})
                seen_files.add(file_name)
        time.sleep(5)

if __name__ == "__main__":
    monitor_and_publish()
