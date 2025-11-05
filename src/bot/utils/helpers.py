"""
Вспомогательные функции для бота
"""
from datetime import datetime
from src.config import ADMIN_IDS


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in ADMIN_IDS


def format_order(order: dict) -> str:
    """Форматирование заказа для отображения"""
    status_emoji = {
        'pending': '🕐',
        'confirmed': '✅',
        'cooking': '👨‍🍳',
        'ready': '🎉',
        'delivered': '📦',
        'cancelled': '❌'
    }

    status_names = {
        'pending': 'Ожидает',
        'confirmed': 'Подтвержден',
        'cooking': 'Готовится',
        'ready': 'Готов',
        'delivered': 'Доставлен',
        'cancelled': 'Отменен'
    }

    emoji = status_emoji.get(order['status'], '❓')
    status_name = status_names.get(order['status'], order['status'])

    items_text = ""
    if order.get('items_data'):
        for item_str in order['items_data'].split(','):
            parts = item_str.split(':')
            if len(parts) >= 4:
                product_name = parts[1] if len(parts) > 1 else 'Продукт'
                quantity = parts[2] if len(parts) > 2 else '0'
                price = parts[3] if len(parts) > 3 else '0'
                cook_telegram = parts[4] if len(parts) > 4 else ''

                cook_info = f" (👨‍🍳 @{cook_telegram})" if cook_telegram else ""
                items_text += f"  • {product_name} x{quantity} = {price} AED{cook_info}\n"

    created = datetime.fromisoformat(order['created_at']).strftime('%d.%m.%Y %H:%M')

    customer_telegram = order.get('customer_telegram', 'Не указан')
    telegram_display = f"@{customer_telegram}" if customer_telegram and customer_telegram != 'Не указан' else customer_telegram

    return f"""
📋 <b>Заказ #{order['id'][:8]}</b>
{emoji} <b>Статус:</b> {status_name}

👤 <b>Имя:</b> {order.get('customer_name', 'Не указано')}
📱 <b>Telegram:</b> {telegram_display}
📍 <b>Адрес:</b> {order.get('customer_address', 'Не указан')}
📞 <b>Телефон:</b> {order.get('customer_phone', 'Не указан')}

🛒 <b>Состав заказа:</b>
{items_text}
💰 <b>Итого:</b> {order['total_amount']} AED

🕐 <b>Создан:</b> {created}
"""
