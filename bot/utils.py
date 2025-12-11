"""
Bot Utility Functions
Permissions, formatters, validators
"""

from telegram import Update
from .config import ADMIN_IDS
from .constants import STATUS_EMOJI, STATUS_NAMES
from datetime import datetime


# ===== PERMISSIONS =====

def is_admin(update: Update) -> bool:
    """Check if user is admin"""
    user_id = update.effective_user.id
    return user_id in ADMIN_IDS


# ===== FORMATTERS =====

def format_order(order: dict) -> str:
    """
    Format order for display
    Returns formatted string with emoji, status, items, total
    """
    order_id = order.get('id', 'N/A')
    status = order.get('status', 'pending')
    emoji = STATUS_EMOJI.get(status, '❓')
    status_name = STATUS_NAMES.get(status, status)

    customer_name = order.get('customer_name', 'Не указано')
    customer_phone = order.get('customer_phone', 'Не указан')
    customer_address = order.get('customer_address', 'Не указан')
    total = order.get('total_amount', 0)

    # Parse created_at
    created_str = order.get('created_at', '')
    try:
        if created_str:
            created_dt = datetime.fromisoformat(created_str)
            created_formatted = created_dt.strftime('%d.%m.%Y %H:%M')
        else:
            created_formatted = 'Неизвестно'
    except:
        created_formatted = str(created_str)

    text = f"""
{emoji} <b>Заказ #{order_id}</b>
━━━━━━━━━━━━━━━
👤 Клиент: {customer_name}
📞 Телефон: {customer_phone}
📍 Адрес: {customer_address}

💵 Сумма: {total} AED
📊 Статус: {status_name}
🕐 Создан: {created_formatted}
"""

    return text.strip()


def format_stats(stats: dict) -> str:
    """
    Format statistics for display
    """
    total_orders = stats.get('total', 0)
    by_status = stats.get('by_status', {})
    total_revenue = stats.get('total_revenue', 0)

    text = f"""
📊 <b>Статистика заказов</b>
━━━━━━━━━━━━━━━

📦 Всего заказов: {total_orders}
💰 Общая выручка: {total_revenue} AED

<b>По статусам:</b>
"""

    for status, count in by_status.items():
        emoji = STATUS_EMOJI.get(status, '❓')
        name = STATUS_NAMES.get(status, status)
        text += f"{emoji} {name}: {count}\n"

    return text.strip()


# ===== VALIDATORS =====

def validate_product_name(name: str) -> tuple[bool, str]:
    """
    Validate product name
    Returns (is_valid, error_message)
    """
    if len(name.strip()) < 3:
        return False, '❌ Название слишком короткое. Минимум 3 символа.'
    return True, ''


def validate_product_description(description: str) -> tuple[bool, str]:
    """
    Validate product description
    Returns (is_valid, error_message)
    """
    if len(description.strip()) < 10:
        return False, '❌ Описание слишком короткое. Минимум 10 символов.'
    return True, ''


def validate_price(price_str: str) -> tuple[bool, float, str]:
    """
    Validate and parse price
    Returns (is_valid, price_float, error_message)
    """
    try:
        price = float(price_str.strip().replace(',', '.'))
        if price <= 0:
            return False, 0, '❌ Цена должна быть больше 0'
        return True, price, ''
    except ValueError:
        return False, 0, '❌ Неверная цена. Введите число (например: 25 или 25.50)'


def validate_image_url(url: str) -> tuple[bool, str]:
    """
    Validate image URL
    Returns (is_valid, error_message)
    """
    url = url.strip()
    if not url.startswith('http://') and not url.startswith('https://'):
        return False, '❌ Неверный URL изображения. Должен начинаться с http:// или https://'
    return True, ''


def validate_telegram_username(username: str) -> tuple[bool, str, str]:
    """
    Validate and normalize Telegram username
    Returns (is_valid, normalized_username, error_message)
    """
    username = username.strip()

    # Skip option
    if username.lower() in ['пропустить', 'skip', '-']:
        return True, '', ''

    # Remove @ if present
    if username.startswith('@'):
        username = username[1:]

    # Basic validation
    if username and (len(username) < 3 or not username.replace('_', '').isalnum()):
        return False, '', '❌ Неверный формат username. Используйте буквы, цифры и _'

    return True, username, ''
