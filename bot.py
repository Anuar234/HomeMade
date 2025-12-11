"""
Telegram Bot для Home Food Abu Dhabi
Модульная версия - использует bot/ модули
"""

# Import from bot modules
from bot.config import BOT_TOKEN, ADMIN_IDS, USE_POSTGRES
from bot.handlers import (
    start,
    help_command,
    orders_command,
    pending_command,
    stats_command,
    products_command,
    get_product_conversation_handler,
    button_callback
)

# Telegram imports
from telegram.ext import Application, CommandHandler, CallbackQueryHandler


def create_application():
    """
    Create and configure bot application
    This is imported by start.py for Railway deployment
    """
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set!")
        return None

    print("=" * 50)
    print("🤖 Creating Telegram Bot Application")
    print("=" * 50)

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    print("📝 Registering command handlers...")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("orders", orders_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("products", products_command))

    # Add conversation handler for product management
    print("📝 Registering product conversation handler...")
    application.add_handler(get_product_conversation_handler())

    # Add callback query handler
    print("📝 Registering callback handler...")
    application.add_handler(CallbackQueryHandler(button_callback))

    print("=" * 50)
    print(f"✅ Bot application created successfully")
    print(f"   Database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
    print(f"   Admins: {len(ADMIN_IDS)} configured")
    print("=" * 50)

    return application


def main():
    """Main function for local development"""
    print("🚀 Starting bot in polling mode (local development)...")
    application = create_application()

    if application:
        application.run_polling()
    else:
        print("❌ Failed to create application")


if __name__ == "__main__":
    main()
