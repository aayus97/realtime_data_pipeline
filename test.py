from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send('file_events', {'event': 'file_upload', 'file_name': 'data.csv', 'timestamp': '2024-11-28T10:00:00'})
producer.flush()
print("Message sent to Kafka!")
