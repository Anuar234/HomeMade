"""
Telegram Bot для Home Food Abu Dhabi
Новая модульная версия

IMPORTANT: Этот файл - демонстрация новой структуры.
Полная миграция будет выполнена позже.
Текущий bot.py все еще работает и используется в production.
"""

# === IMPORTS FROM MODULES ===
from bot.config import BOT_TOKEN, ADMIN_IDS, USE_POSTGRES
from bot.constants import (
    NAME, DESCRIPTION, PRICE, IMAGE, COOK_TELEGRAM, CATEGORY, INGREDIENTS, CONFIRM,
    STATUS_EMOJI, STATUS_NAMES, CATEGORIES, ERROR_MESSAGES
)
from bot.utils import (
    is_admin,
    format_order,
    format_stats,
    validate_product_name,
    validate_product_description,
    validate_price,
    validate_image_url,
    validate_telegram_username
)

# Database import
from database import (
    db, get_all_products, get_product_by_id, add_product, delete_product,
    get_all_orders, get_order_by_id, update_order_status, log_activity
)

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

import json
from datetime import datetime


# ===== COMMAND HANDLERS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command - Main entry point
    Shows different UI for admins vs regular users
    """
    user = update.effective_user
    user_id = user.id

    # Log activity
    log_activity(
        str(user_id),
        user.username or "",
        user.first_name or "",
        user.last_name or "",
        "start_command",
        "User started bot"
    )

    if is_admin(update):
        # Admin panel
        keyboard = [
            [InlineKeyboardButton("📦 Все заказы", callback_data="all_orders")],
            [InlineKeyboardButton("🕐 Ожидающие заказы", callback_data="pending_orders")],
            [InlineKeyboardButton("🍽️ Управление продуктами", callback_data="manage_products")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"👋 Привет, <b>{user.first_name}</b>!\n\n"
            "🔧 <b>Админ-панель Home Food Abu Dhabi</b>\n\n"
            "Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        # User panel
        keyboard = [
            [InlineKeyboardButton("📋 Мои заказы", callback_data="my_orders")],
            [InlineKeyboardButton("📞 Контакты", url="https://t.me/homefoodabudhabi")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"👋 Привет, <b>{user.first_name}</b>!\n\n"
            "🍽️ <b>Home Food Abu Dhabi</b>\n"
            "Домашняя еда с доставкой\n\n"
            "📱 Откройте наше мини-приложение для заказа:\n"
            "👉 /app\n\n"
            "Или выберите действие ниже:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help command"""
    help_text = """
🤖 <b>Команды бота:</b>

<b>Для всех:</b>
/start - Главное меню
/help - Справка
/app - Открыть каталог блюд

<b>Для администраторов:</b>
/orders - Последние заказы
/pending - Ожидающие заказы
/stats - Статистика
/products - Список продуктов
/addproduct - Добавить продукт
"""

    await update.message.reply_text(help_text, parse_mode='HTML')


# ===== APPLICATION FACTORY =====

def create_application():
    """
    Create and configure bot application
    This is imported by start.py for Railway deployment
    """
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set!")
        return None

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # TODO: Add remaining handlers from bot.py
    # - orders command
    # - pending command
    # - stats command
    # - products command
    # - ConversationHandler for adding products
    # - CallbackQueryHandler for buttons

    print(f"✅ Bot application created")
    print(f"   Database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
    print(f"   Admins: {len(ADMIN_IDS)}")

    return application


# ===== MAIN (for local development) =====

def main():
    """Main function for local development"""
    application = create_application()

    if application:
        print("🚀 Starting bot in polling mode...")
        application.run_polling()


if __name__ == "__main__":
    main()
