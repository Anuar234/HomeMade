#!/usr/bin/env python3
"""
Home Food Abu Dhabi - Webhook для Railway с поддержкой ConversationHandler
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

print(f"BOT_TOKEN: {BOT_TOKEN[:10] if BOT_TOKEN else 'Not set'}...")
print(f"PORT: {PORT}")
print(f"RAILWAY_URL: {RAILWAY_URL}")
print("=" * 50)

bot_application = None

@asynccontextmanager
async def lifespan(app):
    """Lifespan для FastAPI"""
    global bot_application
    
    print("FastAPI starting up...")
    
    if not BOT_TOKEN:
        print("⚠️ BOT_TOKEN not set")
        yield
        return
    
    try:
        # Import create_application from bot.py (not bot module)
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Import bot.py as a module
        import importlib.util
        spec = importlib.util.spec_from_file_location("bot_app", "bot.py")
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)

        from database import db
        print(f"Database: {'PostgreSQL' if db.use_postgres else 'SQLite'}")

        # Run migration if on Railway
        if RAILWAY_URL:
            print("🔄 Running database migration...")
            try:
                import subprocess
                result = subprocess.run(['python', 'migrate_products.py'],
                                      capture_output=True, text=True, timeout=30)
                if result.stdout:
                    print(result.stdout)
                if result.returncode != 0 and result.stderr:
                    print(f"Migration warning: {result.stderr}")
            except Exception as e:
                print(f"Migration skipped: {e}")

        # Создаем приложение
        application = bot_module.create_application()
        
        if application:
            # КРИТИЧЕСКИ ВАЖНО: инициализируем приложение полностью
            await application.initialize()
            
            # ВАЖНО: запускаем приложение (это инициализирует persistence и handlers)
            await application.start()
            
            # Настройка webhook
            webhook_url = f"https://{RAILWAY_URL}/webhook/{BOT_TOKEN}"
            print(f"🌐 Setting webhook: {webhook_url}")
            
            await application.bot.delete_webhook(drop_pending_updates=True)
            await application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=["message", "callback_query"]
            )
            
            print("✅ Webhook configured")
            bot_application = application
            
            # ВАЖНО: Запускаем обработчик очереди в фоне
            asyncio.create_task(process_updates())
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    yield
    
    # Shutdown
    if bot_application:
        try:
            await bot_application.stop()
            await bot_application.shutdown()
        except Exception as e:
            print(f"Shutdown error: {e}")


async def process_updates():
    """Обработчик очереди updates - необходим для ConversationHandler"""
    global bot_application
    
    if not bot_application:
        return
    
    print("🔄 Starting update processor...")
    
    try:
        # Непрерывно обрабатываем updates из очереди
        while True:
            try:
                # Получаем update из очереди (ждём максимум 1 секунду)
                update = await asyncio.wait_for(
                    bot_application.update_queue.get(),
                    timeout=1.0
                )
                
                # Обрабатываем update через все handlers
                await bot_application.process_update(update)
                
            except asyncio.TimeoutError:
                # Таймаут - это нормально, продолжаем ждать
                continue
            except Exception as e:
                print(f"❌ Error processing update: {e}")
                import traceback
                traceback.print_exc()
    except asyncio.CancelledError:
        print("Update processor cancelled")


from main import app as fastapi_app
from fastapi import Request, Response

fastapi_app.router.lifespan_context = lifespan


@fastapi_app.post("/webhook/{token}")
async def webhook(token: str, request: Request):
    """Telegram webhook"""
    if token != BOT_TOKEN:
        return Response(status_code=403)
    
    if not bot_application:
        return Response(status_code=503)
    
    try:
        from telegram import Update
        
        data = await request.json()
        update_id = data.get('update_id', 'unknown')
        
        # Логируем детали
        if 'message' in data:
            msg = data['message']
            print(f"📨 Message [{update_id}]: {msg.get('text', 'no text')[:50]}")
        elif 'callback_query' in data:
            cb = data['callback_query']
            print(f"📨 Callback [{update_id}]: {cb.get('data', 'no data')}")
        
        # Создаём Update
        update = Update.de_json(data, bot_application.bot)
        
        # Кладём в очередь для обработки
        await bot_application.update_queue.put(update)
        
        return {"ok": True}
    
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return {"ok": False}


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
