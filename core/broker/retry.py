from tenacity import retry, stop_after_attempt, wait_fixed
import requests

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def call_broker_api(url, payload):
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()
