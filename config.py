"""
Конфигурация приложения
"""
import os

class Settings:
    # Основные настройки
    APP_NAME = "Home Food Abu Dhabi"
    VERSION = "1.0.0"
    
    # Настройки сервера
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS настройки
    CORS_ORIGINS = ["*"]
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]
    
    # Пути к статическим файлам
    STATIC_DIR = "static"
    
    # Настройки базы данных (пока используем in-memory)
    DATABASE_URL = "sqlite:///./home_food.db"
    
    # Настройки Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Создаем экземпляр настроек
settings = Settings()