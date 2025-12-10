#!/usr/bin/env python3
"""
Универсальный запуск Home Food Abu Dhabi
Webhook для production (Railway) и polling для local
"""

import os
import asyncio
from contextlib import asynccontextmanager

print("=" * 50)
print("Home Food Abu Dhabi - Starting...")
print("=" * 50)

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8000))
RAILWAY_URL = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("RAILWAY_STATIC_URL")
IS_RAILWAY = RAILWAY_URL is not None

print(f"BOT_TOKEN: {BOT_TOKEN[:10] if BOT_TOKEN else 'Not set'}...")
print(f"PORT: {PORT}")
print(f"ENVIRONMENT: {'Railway (Production)' if IS_RAILWAY else 'Local (Development)'}")
print(f"MODE: {'Webhook' if IS_RAILWAY else 'Polling'}")
print("=" * 50)

bot_application = None

@asynccontextmanager
async def lifespan(app):
    """Lifespan для FastAPI - настройка и остановка бота"""
    global bot_application
    
    print("FastAPI starting up...")
    
    if not BOT_TOKEN:
        print("⚠️ BOT_TOKEN not set, skipping bot initialization")
        yield
        return
    
    try:
        # Импортируем бота
        import bot
        from telegram import Update
        
        print(f"Database: {'PostgreSQL' if bot.db.use_postgres else 'SQLite'}")
        
        # Создаем приложение
        application = bot.create_application()
        
        if application:
            await application.initialize()
            await application.start()
            
            if IS_RAILWAY:
                # Production: Webhook
                webhook_url = f"https://{RAILWAY_URL}/webhook"
                print(f"🌐 Setting webhook: {webhook_url}")
                
                await application.bot.delete_webhook(drop_pending_updates=True)
                await application.bot.set_webhook(url=webhook_url)
                
                print("✅ Webhook set successfully")
            else:
                # Local: Polling
                print("🔄 Starting polling...")
                await application.bot.delete_webhook(drop_pending_updates=True)
                await application.updater.start_polling(drop_pending_updates=True)
                print("✅ Polling started")
            
            bot_application = application
        
    except Exception as e:
        print(f"❌ Bot initialization error: {e}")
        import traceback
        traceback.print_exc()
    
    yield  # Приложение работает
    
    # Остановка
    print("Shutting down bot...")
    if bot_application:
        try:
            if not IS_RAILWAY and bot_application.updater.running:
                await bot_application.updater.stop()
            await bot_application.stop()
            await bot_application.shutdown()
        except Exception as e:
            print(f"Error during shutdown: {e}")


# Импортируем FastAPI app
from main import app as fastapi_app
from fastapi import Request, Response

# Применяем lifespan
fastapi_app.router.lifespan_context = lifespan


# Webhook endpoint
@fastapi_app.post("/webhook")
async def webhook(request: Request):
    """Обработчик Telegram webhook (только для Railway)"""
    if not IS_RAILWAY:
        return Response(status_code=403, content="Webhook only available in production")
    
    if not bot_application:
        print("⚠️ Webhook received but bot not ready")
        return Response(status_code=503, content="Bot not ready")
    
    try:
        from telegram import Update
        
        # Получаем данные
        data = await request.json()
        print(f"📨 Webhook received: {data.get('update_id', 'unknown')}")
        
        # Создаём Update объект
        update = Update.de_json(data, bot_application.bot)
        
        # Обрабатываем update СИНХРОННО
        await bot_application.process_update(update)
        
        print(f"✅ Update processed: {update.update_id}")
        return Response(status_code=200, content="OK")
    
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return Response(status_code=200, content="OK")  # Всё равно возвращаем 200


if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting server on 0.0.0.0:{PORT}")
    print("=" * 50)
    
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
