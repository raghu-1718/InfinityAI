# REST API connector example
import requests

def fetch_rest_api(url, params=None, headers=None):
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# WebSocket connector example
import websocket

def fetch_websocket(url, on_message):
    ws = websocket.WebSocketApp(url, on_message=on_message)
    ws.run_forever()

# Cloud storage connector example (AWS S3)
import boto3

def fetch_s3(bucket, key, aws_access_key, aws_secret_key):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj['Body'].read()

# Streaming connector example (Kafka)
from kafka import KafkaConsumer

def fetch_kafka(topic, bootstrap_servers):
    consumer = KafkaConsumer(topic, bootstrap_servers=bootstrap_servers)
    for message in consumer:
        print(message.value)

# Scraping connector example
from bs4 import BeautifulSoup

def fetch_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup
