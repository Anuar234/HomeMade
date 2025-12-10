#!/usr/bin/env python3
"""
Универсальный запуск Home Food Abu Dhabi
Запускает FastAPI и Telegram Bot одновременно в одном процессе

ВАЖНО: Обновите Procfile:
web: python start.py

Это запустит и API, и бота в одном процессе!
"""

import os
import asyncio
import threading
from contextlib import asynccontextmanager

print("=" * 50)
print("Home Food Abu Dhabi - Starting...")
print("=" * 50)

# Проверка переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8000))

if not BOT_TOKEN:
    print("WARNING: BOT_TOKEN not set! Bot will not work.")
    print("Set it in Railway environment variables")
else:
    print(f"BOT_TOKEN: {BOT_TOKEN[:10]}...")

print(f"PORT: {PORT}")
print(f"ADMIN_IDS: {os.getenv('ADMIN_IDS', 'Not set')}")
print("=" * 50)


def run_bot_in_thread():
    """Запуск бота с созданием нового event loop для потока"""
    if not BOT_TOKEN:
        print("Skipping bot - no BOT_TOKEN")
        return

    try:
        print("Starting Telegram Bot thread...")
        
        # КРИТИЧЕСКИ ВАЖНО: создаем новый event loop для этого потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Импортируем бота
        import bot
        from telegram import Update


        print("Database: homefood.db")
        print(f"Admins: {bot.ADMIN_IDS}")

        # Создаем приложение через нашу функцию
        application = bot.create_application()

        if not application:
            print("Failed to create bot application")
            return

        print("Bot started and listening for updates...")

        # Запускаем бота асинхронно в текущем event loop
        async def run_bot_async():
            async with application:
                await application.start()
                await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
                # Держим бота живым
                await asyncio.Event().wait()

        # Запускаем
        loop.run_until_complete(run_bot_async())


    except Exception as e:
        print(f"Bot error: {e}")
        import traceback
        traceback.print_exc()


def start_bot_thread():
    """Запускаем бота в отдельном потоке с daemon=True"""
    bot_thread = threading.Thread(
        target=run_bot_in_thread,
        daemon=True,
        name="TelegramBotThread"
    )
    bot_thread.start()
    print("Bot thread started")
    return bot_thread


@asynccontextmanager
async def lifespan(app):
    """Lifespan events для FastAPI - запускаем бота при старте"""
    print("FastAPI starting up...")

    # Запускаем бота в отдельном потоке
    start_bot_thread()

    yield  # Приложение работает

    print("FastAPI shutting down...")


# Импортируем FastAPI app и добавляем lifespan
from main import app as fastapi_app

# Заменяем lifespan в существующем app
fastapi_app.router.lifespan_context = lifespan


if __name__ == "__main__":
    import uvicorn

    print(f"Starting FastAPI on 0.0.0.0:{PORT}")
    print("=" * 50)
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')[:30]}...")
    print(f"Using: {'PostgreSQL' if os.getenv('DATABASE_URL') else 'SQLite'}")

    
    # Запускаем FastAPI (бот запустится автоматически через lifespan)
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        access_log=True
    )