"""
Telegram Bot для HomeMade Food
Переработанная версия с модульной структурой
"""
import asyncio
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

from src.config import BOT_TOKEN, ADMIN_IDS, WEB_APP_URL
from src.database import get_db, init_database, add_missing_columns
from src.bot.utils import is_admin, format_order

# Conversation states
(NAME, DESCRIPTION, PRICE, IMAGE, COOK_TELEGRAM,
 CATEGORY, INGREDIENTS, CONFIRM) = range(8)


# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id

    not_admin_keyboard = [
        [InlineKeyboardButton("🍱 Открыть меню", url=f"{WEB_APP_URL}/app")],
        [InlineKeyboardButton("📦 Мои заказы", callback_data="my_orders")],
        [InlineKeyboardButton("💬 Связаться с поддержкой", url="https://t.me/sekeww")],
    ]

    if not is_admin(user_id):
        await update.message.reply_text(
            "👋 Привет!\n\n"
            "Добро пожаловать в <b>HomeMade</b> — место, где вкус и уют встречаются прямо у тебя дома 🍲\n\n"
            "📱 Здесь ты можешь заказать домашнюю еду, приготовленную с любовью. Всё просто — выбирай, заказывай и наслаждайся 😋\n\n"
            "Готов начать?",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(not_admin_keyboard)
        )
        return

    keyboard = [
        [InlineKeyboardButton("📦 Все заказы", callback_data="orders_all")],
        [InlineKeyboardButton("�� Новые заказы", callback_data="orders_pending")],
        [InlineKeyboardButton("👨‍🍳 В работе", callback_data="orders_cooking")],
        [InlineKeyboardButton("🍽️ Управление меню", callback_data="menu_manage")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🍽️ <b>HomeMade Admin Panel</b>\n\n"
        "Добро пожаловать, шеф 👨‍🍳\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def my_orders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать заказы пользователя"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*,
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' ||
                       oi.quantity || ':' || oi.price || ':' ||
                       COALESCE(oi.cook_telegram, '')
                   ) as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_telegram_id = ?
            GROUP BY o.id
            ORDER BY o.created_at DESC
            LIMIT 5
        ''', (user_id,))
        orders = [dict(row) for row in cursor.fetchall()]

    if not orders:
        await query.edit_message_text("📭 У тебя пока нет заказов.")
        return

    await query.edit_message_text(f"📦 <b>Твои последние {len(orders)} заказов</b>", parse_mode='HTML')

    for order in orders:
        keyboard = [
            [InlineKeyboardButton("📝 Подробнее", callback_data=f"order_detail_{order['id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            format_order(order),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "my_orders":
        await my_orders_callback(update, context)
        return

    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ У вас нет доступа к этой функции")
        return

    # Admin handlers
    if data == "orders_all":
        await show_all_orders(query)
    elif data == "orders_pending":
        await show_pending_orders(query)
    elif data == "orders_cooking":
        await show_cooking_orders(query)
    elif data == "stats":
        await show_stats(query)
    elif data.startswith("order_detail_"):
        await show_order_detail(query, data)
    elif data.startswith("status_"):
        await update_order_status(query, data)


async def show_all_orders(query):
    """Показать все заказы"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*,
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' ||
                       oi.quantity || ':' || oi.price || ':' ||
                       COALESCE(oi.cook_telegram, '')
                   ) as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.created_at DESC
            LIMIT 5
        ''')
        orders = [dict(row) for row in cursor.fetchall()]

    if not orders:
        await query.edit_message_text("📭 Заказов пока нет")
        return

    await query.edit_message_text(f"📦 <b>Последние {len(orders)} заказов</b>", parse_mode='HTML')

    for order in orders:
        keyboard = [
            [InlineKeyboardButton("📝 Подробнее", callback_data=f"order_detail_{order['id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            format_order(order),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def show_pending_orders(query):
    """Показать новые заказы"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*,
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' ||
                       oi.quantity || ':' || oi.price || ':' ||
                       COALESCE(oi.cook_telegram, '')
                   ) as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status = 'pending'
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''')
        orders = [dict(row) for row in cursor.fetchall()]

    if not orders:
        await query.edit_message_text("✅ Новых заказов нет")
        return

    await query.edit_message_text(f"🕐 <b>Новых заказов: {len(orders)}</b>", parse_mode='HTML')

    for order in orders:
        keyboard = [
            [
                InlineKeyboardButton("✅ Принять", callback_data=f"status_{order['id']}_confirmed"),
                InlineKeyboardButton("❌ Отменить", callback_data=f"status_{order['id']}_cancelled")
            ],
            [InlineKeyboardButton("📝 Подробнее", callback_data=f"order_detail_{order['id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            format_order(order),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def show_cooking_orders(query):
    """Показать заказы в работе"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*,
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' ||
                       oi.quantity || ':' || oi.price || ':' ||
                       COALESCE(oi.cook_telegram, '')
                   ) as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status IN ('confirmed', 'cooking')
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''')
        orders = [dict(row) for row in cursor.fetchall()]

    if not orders:
        await query.edit_message_text("📭 Заказов в работе нет")
        return

    await query.edit_message_text(f"👨‍🍳 <b>Заказов в работе: {len(orders)}</b>", parse_mode='HTML')

    for order in orders:
        keyboard = [
            [InlineKeyboardButton("📝 Подробнее", callback_data=f"order_detail_{order['id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            format_order(order),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def show_order_detail(query, data):
    """Показать детали заказа"""
    order_id = data.replace("order_detail_", "")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*,
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' ||
                       oi.quantity || ':' || oi.price || ':' ||
                       COALESCE(oi.cook_telegram, '')
                   ) as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.id = ?
            GROUP BY o.id
        ''', (order_id,))
        order = cursor.fetchone()

    if not order:
        await query.edit_message_text("❌ Заказ не найден")
        return

    order = dict(order)

    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"status_{order_id}_confirmed"),
            InlineKeyboardButton("👨‍🍳 Готовится", callback_data=f"status_{order_id}_cooking")
        ],
        [
            InlineKeyboardButton("🎉 Готов", callback_data=f"status_{order_id}_ready"),
            InlineKeyboardButton("📦 Доставлен", callback_data=f"status_{order_id}_delivered")
        ],
        [
            InlineKeyboardButton("❌ Отменить", callback_data=f"status_{order_id}_cancelled")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        format_order(order),
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def update_order_status(query, data):
    """Обновить статус заказа"""
    parts = data.split("_")
    order_id = parts[1]
    new_status = parts[2]

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE orders SET status = ? WHERE id = ?',
            (new_status, order_id)
        )
        conn.commit()

        cursor.execute('''
            SELECT o.*,
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' ||
                       oi.quantity || ':' || oi.price || ':' ||
                       COALESCE(oi.cook_telegram, '')
                   ) as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.id = ?
            GROUP BY o.id
        ''', (order_id,))
        order = dict(cursor.fetchone())

    keyboard = [
        [InlineKeyboardButton("📝 Подробнее", callback_data=f"order_detail_{order_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"✅ <b>Статус обновлен!</b>\n\n{format_order(order)}",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def show_stats(query):
    """Показать статистику"""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as count FROM orders')
        total_orders = cursor.fetchone()['count']

        cursor.execute('''
            SELECT status, COUNT(*) as count, SUM(total_amount) as total
            FROM orders
            GROUP BY status
        ''')
        status_stats = cursor.fetchall()

        cursor.execute('SELECT SUM(total_amount) as total FROM orders')
        total_amount = cursor.fetchone()['total'] or 0

        cursor.execute('''
            SELECT COUNT(*) as count, SUM(total_amount) as total
            FROM orders
            WHERE DATE(created_at) = DATE('now')
        ''')
        today = cursor.fetchone()

        cursor.execute('SELECT COUNT(*) as count FROM products')
        total_products = cursor.fetchone()['count']

    stats_text = f"""
📊 <b>Статистика HomeMade</b>

📦 Всего заказов: {total_orders}
🍽️ Блюд в меню: {total_products}
💰 Общая сумма: {total_amount:.1f} AED

<b>По статусам:</b>
"""

    status_emoji = {
        'pending': '🕐', 'confirmed': '✅', 'cooking': '👨‍🍳',
        'ready': '🎉', 'delivered': '📦', 'cancelled': '❌'
    }

    for stat in status_stats:
        emoji = status_emoji.get(stat['status'], '❓')
        stats_text += f"{emoji} {stat['status']}: {stat['count']} ({stat['total']:.1f} AED)\n"

    stats_text += f"\n📅 Сегодня: {today['count']} заказов ({today['total'] or 0:.1f} AED)"

    await query.edit_message_text(stats_text, parse_mode='HTML')


def create_application():
    """Создать и настроить application"""
    if not BOT_TOKEN:
        print("❌ ОШИБКА: Установите BOT_TOKEN!")
        return None

    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))

    return application


def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        print("❌ ОШИБКА: Установите BOT_TOKEN в .env файле!")
        return

    print("🤖 Запуск Telegram бота...")
    print(f"👥 Админы: {ADMIN_IDS}")

    # Инициализируем базу данных
    init_database()
    add_missing_columns()
    print("✅ База данных инициализирована")

    application = create_application()

    if application:
        print("✅ Бот запущен и готов к работе!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
