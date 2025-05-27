import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))  # Fallback to 0 if not set

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"