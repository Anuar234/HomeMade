#!/usr/bin/env python3
"""
Универсальный скрипт запуска Home Food Abu Dhabi
Запускает API и Telegram Bot одновременно
"""

import os
import sys
import threading
import time

def run_bot():
    """Запуск Telegram бота в отдельном потоке"""
    try:
        print("🤖 Запуск Telegram бота...")
        # Импортируем и запускаем бота
        import bot
        bot.main()
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")
        import traceback
        traceback.print_exc()

def run_api():
    """Запуск API сервера"""
    try:
        print("🚀 Запуск API сервера...")
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        
        # Запускаем uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Главная функция"""
    print("""
    ╔═══════════════════════════════════════╗
    ║   🍽️  Home Food Abu Dhabi           ║
    ║   Платформа домашней еды             ║
    ╚═══════════════════════════════════════╝
    """)
    
    print("📍 Окружение:")
    print(f"   PORT: {os.getenv('PORT', '8000')}")
    print(f"   BOT_TOKEN: {'✅ Установлен' if os.getenv('BOT_TOKEN') else '❌ Не установлен'}")
    print(f"   ADMIN_IDS: {os.getenv('ADMIN_IDS', 'По умолчанию')}")
    print()
    
    # Запускаем бота в отдельном потоке (daemon=True означает, что поток завершится при завершении основного процесса)
    bot_thread = threading.Thread(target=run_bot, daemon=True, name="TelegramBot")
    bot_thread.start()
    
    print("✅ Telegram бот запущен в фоновом режиме")
    print()
    
    # Небольшая задержка
    time.sleep(2)
    
    # Запускаем API в главном потоке (это важно для Railway)
    run_api()

if __name__ == "__main__":
    main()