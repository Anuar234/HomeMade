"""
Модуль для отправки уведомлений
"""
import asyncio
from telegram import Bot
from src.config import BOT_TOKEN, ADMIN_IDS
from src.bot.utils.helpers import format_order


async def send_order_notification_to_admins(order: dict):
    """Отправка уведомления о новом заказе администраторам"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не установлен")
        return

    bot = Bot(token=BOT_TOKEN)

    for admin_id in ADMIN_IDS:
        try:
            message = f"""
🔔 <b>НОВЫЙ ЗАКАЗ!</b>

{format_order(order)}

Пожалуйста, обработайте заказ через /start
"""
            await bot.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode='HTML'
            )
            print(f"✅ Уведомление отправлено админу {admin_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки уведомления админу {admin_id}: {e}")


async def send_order_status_to_user(user_telegram_id: int, order: dict):
    """Отправка статуса заказа пользователю"""
    if not BOT_TOKEN or not user_telegram_id:
        return

    bot = Bot(token=BOT_TOKEN)

    try:
        message = f"""
✅ <b>Ваш заказ создан!</b>

{format_order(order)}

Мы свяжемся с вами в ближайшее время!
"""
        await bot.send_message(
            chat_id=user_telegram_id,
            text=message,
            parse_mode='HTML'
        )
        print(f"✅ Статус заказа отправлен пользователю {user_telegram_id}")
    except Exception as e:
        print(f"❌ Ошибка отправки статуса пользователю {user_telegram_id}: {e}")
