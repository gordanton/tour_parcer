import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env файле")

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except ValueError as exc:
    raise ValueError("ADMIN_ID должен быть числом") from exc

DB_NAME = os.getenv("DB_NAME", "travel_promotions.db")
