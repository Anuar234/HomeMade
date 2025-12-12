"""
Bot Constants
Conversation states, emojis, categories, and other static values
"""

# Conversation States for adding products
NAME, DESCRIPTION, PRICE, IMAGE, CATEGORY, INGREDIENTS, CONFIRM = range(7)

# Order status emojis
STATUS_EMOJI = {
    'pending': '🕐',
    'confirmed': '✅',
    'cooking': '👨‍🍳',
    'ready': '🎉',
    'delivered': '📦',
    'cancelled': '❌'
}

# Order status names (Russian)
STATUS_NAMES = {
    'pending': 'Ожидает',
    'confirmed': 'Подтвержден',
    'cooking': 'Готовится',
    'ready': 'Готов',
    'delivered': 'Доставлен',
    'cancelled': 'Отменен'
}

# Product categories
CATEGORIES = [
    ('pelmeni', '🥟 Пельмени'),
    ('plov', '🍚 Плов'),
    ('soup', '🍲 Супы'),
    ('khachapuri', '🥖 Хачапури'),
    ('burger', '🍔 Бургеры'),
    ('pizza', '🍕 Пицца'),
    ('dessert', '🍰 Десерты'),
    ('salad', '🥗 Закуски'),
    ('drinks', '🥤 Напитки')
]

# Error messages
ERROR_MESSAGES = {
    'name_too_short': '❌ Название слишком короткое. Минимум 3 символа.',
    'description_too_short': '❌ Описание слишком короткое. Минимум 10 символов.',
    'invalid_price': '❌ Неверная цена. Введите число (например: 25 или 25.50)',
    'invalid_url': '❌ Неверный URL изображения. Должен начинаться с http:// или https://',
    'not_admin': '❌ У вас нет доступа к этой команде.'
}
