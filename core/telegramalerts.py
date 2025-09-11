import os
import requests

BOT_TOKEN = os.getenv("TELEGRAMBOTTOKEN")

def send_telegram(chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, json=data, timeout=5)
    except Exception as e:
        print(f"Telegram send failed: {e}")
