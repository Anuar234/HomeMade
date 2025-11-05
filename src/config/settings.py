"""
Конфигурация приложения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]
TELEGRAM_TARGET = os.getenv("TELEGRAM_TARGET", "")

# Database
DATABASE = os.getenv("DATABASE", "homefood.db")

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# URLs
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://homemade-production.up.railway.app")
