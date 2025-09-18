# Example Kafka consumer for market data
from kafka import KafkaConsumer
import json
import os

bootstrap = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
bootstrap_servers = [s.strip() for s in bootstrap.split(',') if s.strip()]

consumer = KafkaConsumer(
    'market-data',
    bootstrap_servers=bootstrap_servers,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    print(f"Received market data: {message.value}")
