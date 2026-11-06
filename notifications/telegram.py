import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def send_message(message):

    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing from .env")
        return False

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(
            TELEGRAM_URL,
            json=payload,
            timeout=15
        )

        response.raise_for_status()
        print("Telegram notification sent!")
        return True

    except requests.exceptions.RequestException as error:
        print(f"Telegram error: {error}")
        return False