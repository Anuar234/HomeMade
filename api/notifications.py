"""
Telegram Notifications for Orders
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


async def send_telegram_notifications(order: dict):
    """Отправка уведомлений в Telegram о новом заказе"""
    try:
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
        ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]

        if not BOT_TOKEN:
            print("⚠️ BOT_TOKEN не установлен, уведомления не отправлены")
            return

        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)

        # Форматируем заказ для отображения
        status_emoji = {
            'pending': '🕐',
            'confirmed': '✅',
            'cooking': '👨‍🍳',
            'ready': '🎉',
            'delivered': '📦',
            'cancelled': '❌'
        }

        emoji = status_emoji.get(order.get('status', 'pending'), '🕐')

        items_text = ""
        if order.get('items_data'):
            for item_str in order['items_data'].split(','):
                parts = item_str.split(':')
                if len(parts) >= 4:
                    product_name = parts[1]
                    quantity = parts[2]
                    price = parts[3]

                    items_text += f"  • {product_name} x{quantity} = {price} AED\n"

        # Handle both datetime objects and ISO strings
        created_at = order['created_at']
        if isinstance(created_at, str):
            created = datetime.fromisoformat(created_at).strftime('%d.%m.%Y %H:%M')
        else:
            created = created_at.strftime('%d.%m.%Y %H:%M')

        customer_telegram = order.get('customer_telegram', 'Не указан')
        telegram_display = f"@{customer_telegram}" if customer_telegram and customer_telegram != 'Не указан' else customer_telegram

        # Сообщение для админов
        admin_message = f"""
🔔 <b>НОВЫЙ ЗАКАЗ!</b>

📋 <b>Заказ #{order['id']}</b>
{emoji} <b>Статус:</b> Ожидает обработки

👤 <b>Имя:</b> {order.get('customer_name', 'Не указано')}
📱 <b>Telegram:</b> {telegram_display}
📍 <b>Адрес:</b> {order.get('customer_address', 'Не указан')}
📞 <b>Телефон:</b> {order.get('customer_phone', 'Не указан')}

🛒 <b>Состав заказа:</b>
{items_text}
💰 <b>Итого:</b> {order['total_amount']} AED

🕐 <b>Создан:</b> {created}

<b>Пожалуйста, обработайте заказ через /start</b>
"""

        # Сообщение для пользователя
        user_message = f"""
✅ <b>Ваш заказ создан!</b>

📋 <b>Заказ #{order['id']}</b>
{emoji} <b>Статус:</b> Ожидает подтверждения

🛒 <b>Состав заказа:</b>
{items_text}
💰 <b>Итого:</b> {order['total_amount']} AED

📍 <b>Адрес доставки:</b> {order.get('customer_address', 'Не указан')}

<b>Мы свяжемся с вами в ближайшее время!</b>
Вы можете отслеживать статус заказа через /start → "Мои заказы"
"""

        # Отправляем админам
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    parse_mode='HTML'
                )
                print(f"✅ Уведомление отправлено админу {admin_id}")
            except Exception as e:
                print(f"❌ Ошибка отправки админу {admin_id}: {e}")

        # Отправляем пользователю
        user_telegram_id = order.get('user_telegram_id')
        if user_telegram_id:
            try:
                await bot.send_message(
                    chat_id=user_telegram_id,
                    text=user_message,
                    parse_mode='HTML'
                )
                print(f"✅ Уведомление отправлено пользователю {user_telegram_id}")
            except Exception as e:
                print(f"❌ Ошибка отправки пользователю {user_telegram_id}: {e}")
                print(f"   Возможно, пользователь не написал боту /start")
        else:
            print("⚠️ user_telegram_id не указан, уведомление пользователю не отправлено")

    except Exception as e:
        print(f"❌ Ошибка отправки уведомлений: {e}")
        import traceback
        traceback.print_exc()


async def send_status_update_notification(order: dict):
    """Отправка уведомления пользователю об изменении статуса заказа"""
    try:
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        user_telegram_id = order.get('user_telegram_id')

        if not BOT_TOKEN:
            print("⚠️ BOT_TOKEN не установлен, уведомление не отправлено")
            return

        if not user_telegram_id:
            print("⚠️ user_telegram_id не указан, уведомление не отправлено")
            return

        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)

        # Статусы на русском
        status_names = {
            'pending': '🕐 Ожидает обработки',
            'confirmed': '✅ Подтвержден',
            'cooking': '👨‍🍳 Готовится',
            'ready': '🎉 Готов к получению',
            'delivered': '📦 Доставлен',
            'cancelled': '❌ Отменен'
        }

        status = order.get('status', 'pending')
        status_text = status_names.get(status, status)

        items_text = ""
        if order.get('items_data'):
            for item_str in order['items_data'].split(','):
                parts = item_str.split(':')
                if len(parts) >= 4:
                    product_name = parts[1]
                    quantity = parts[2]
                    items_text += f"  • {product_name} x{quantity}\n"

        message = f"""
📢 <b>Обновление статуса заказа</b>

📋 <b>Заказ #{order['id']}</b>
{status_text}

🛒 <b>Состав:</b>
{items_text}
💰 <b>Итого:</b> {order['total_amount']} AED

📍 <b>Адрес:</b> {order.get('customer_address', 'Не указан')}
"""

        # Дополнительная информация в зависимости от статуса
        if status == 'confirmed':
            message += "\n<b>Ваш заказ принят в работу!</b> Ожидайте начала приготовления."
        elif status == 'cooking':
            message += "\n<b>Ваш заказ готовится!</b> Скоро всё будет готово 👨‍🍳"
        elif status == 'ready':
            message += "\n<b>Ваш заказ готов!</b> Ожидайте доставку 🎉"
        elif status == 'delivered':
            message += "\n<b>Приятного аппетита!</b> Спасибо за заказ! 😊"
        elif status == 'cancelled':
            message += "\n<b>Заказ отменен.</b> Если у вас есть вопросы, свяжитесь с поддержкой."

        await bot.send_message(
            chat_id=user_telegram_id,
            text=message,
            parse_mode='HTML'
        )
        print(f"✅ Уведомление о статусе '{status}' отправлено пользователю {user_telegram_id}")

    except Exception as e:
        print(f"❌ Ошибка отправки уведомления о статусе: {e}")
        print(f"   Возможно, пользователь не написал боту /start")
