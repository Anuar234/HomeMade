"""
Keyboard builders for Telegram Bot
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .constants import CATEGORIES


def get_admin_main_keyboard():
    """Get main admin keyboard"""
    keyboard = [
        [InlineKeyboardButton("📦 Все заказы", callback_data="all_orders")],
        [InlineKeyboardButton("🕐 Ожидающие заказы", callback_data="pending_orders")],
        [InlineKeyboardButton("🍽️ Управление продуктами", callback_data="manage_products")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_user_main_keyboard():
    """Get main user keyboard"""
    keyboard = [
        [InlineKeyboardButton("📋 Мои заказы", callback_data="my_orders")],
        [InlineKeyboardButton("📞 Контакты", url="https://t.me/homefoodabudhabi")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_product_management_keyboard():
    """Get product management keyboard"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить продукт", callback_data="add_product")],
        [InlineKeyboardButton("✏️ Редактировать продукт", callback_data="edit_product")],
        [InlineKeyboardButton("📋 Список продуктов", callback_data="list_products")],
        [InlineKeyboardButton("🗑️ Удалить продукт", callback_data="delete_product")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_category_keyboard():
    """Get category selection keyboard"""
    keyboard = []
    for cat_id, cat_name in CATEGORIES:
        keyboard.append([InlineKeyboardButton(cat_name, callback_data=f"category_{cat_id}")])
    return InlineKeyboardMarkup(keyboard)


def get_product_confirm_keyboard():
    """Get product confirmation keyboard"""
    keyboard = [
        [InlineKeyboardButton("✅ Сохранить", callback_data="save_product")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_product")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_order_status_keyboard(order_id: str):
    """Get order status change keyboard"""
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"status_{order_id}_confirmed")],
        [InlineKeyboardButton("👨‍🍳 Готовится", callback_data=f"status_{order_id}_cooking")],
        [InlineKeyboardButton("🎉 Готов", callback_data=f"status_{order_id}_ready")],
        [InlineKeyboardButton("📦 Доставлен", callback_data=f"status_{order_id}_delivered")],
        [InlineKeyboardButton("❌ Отменить", callback_data=f"status_{order_id}_cancelled")],
        [InlineKeyboardButton("◀️ Назад", callback_data="all_orders")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_button(callback_data="back_to_main"):
    """Get single back button"""
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)


def get_products_list_keyboard(products: list):
    """Get keyboard with list of products for deletion"""
    keyboard = []
    for product in products:
        product_id = product.get('id')
        product_name = product.get('name')
        keyboard.append([
            InlineKeyboardButton(
                f"🗑️ {product_name}",
                callback_data=f"delete_product_{product_id}"
            )
        ])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="manage_products")])
    return InlineKeyboardMarkup(keyboard)
