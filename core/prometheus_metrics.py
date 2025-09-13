# Prometheus metrics example for FastAPI
from prometheus_client import start_http_server, Summary
import random
import time

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

def process_request(t):
    time.sleep(t)

if __name__ == '__main__':
    start_http_server(8001)
    while True:
        process_request(random.random())
