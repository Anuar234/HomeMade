"""
Command Handlers
Handles bot commands like /start, /help, /orders, /pending, /stats, /products
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

from ..config import ADMIN_IDS
from ..utils import is_admin, format_order

# Import from root database module
from database import db, get_all_orders, get_all_products

try:
    from psycopg2.extras import RealDictCursor
except ImportError:
    RealDictCursor = None


def get_db():
    """Get database connection (compatibility wrapper)"""
    return db.get_connection()


def get_cursor(conn):
    """Get cursor with dict support for both SQLite and PostgreSQL"""
    if db.use_postgres and RealDictCursor:
        return conn.cursor(cursor_factory=RealDictCursor)
    else:
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        return conn.cursor()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command
    Shows different menu based on user role (admin vs regular user)
    """
    user_id = update.effective_user.id

    not_admin_keyboard = [
        [InlineKeyboardButton("🍱 Открыть меню", url="https://homemade-production.up.railway.app/app")],
        [InlineKeyboardButton("Мои заказы", callback_data="my_orders")],
        [InlineKeyboardButton("Связаться с поддержкой", url="https://t.me/sekeww")],
    ]

    if user_id not in ADMIN_IDS:
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
        [InlineKeyboardButton("🕐 Новые заказы", callback_data="orders_pending")],
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


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /help command
    Shows available commands and features (admin only)
    """
    if update.effective_user.id not in ADMIN_IDS:
        return

    help_text = """
🤖 <b>Команды бота:</b>

/start - Главное меню
/orders - Все заказы
/pending - Новые заказы
/addproduct - Добавить блюдо
/products - Список всех блюд
/stats - Статистика
/help - Эта справка

<b>Функции:</b>
• Просмотр всех заказов
• Изменение статуса заказов
• Добавление новых блюд
• Управление меню
• Просмотр статистики
"""
    await update.message.reply_text(help_text, parse_mode='HTML')


async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /orders command
    Shows all recent orders (admin only)
    """
    if update.effective_user.id not in ADMIN_IDS:
        return

    with get_db() as conn:
        cursor = get_cursor(conn)
        cursor.execute('''
            SELECT o.*,
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' ||
                       oi.quantity || ':' || oi.price || ':' ||
                       COALESCE(oi.cook_name, '') || ':' || COALESCE(oi.cook_phone, '')
                   ) as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.created_at DESC
            LIMIT 10
        ''')
        orders = cursor.fetchall()

    if not orders:
        await update.message.reply_text("📭 Заказов пока нет")
        return

    await update.message.reply_text(
        f"📦 <b>Последние {len(orders)} заказов:</b>",
        parse_mode='HTML'
    )

    for order in orders:
        keyboard = [
            [InlineKeyboardButton("📝 Подробнее", callback_data=f"order_detail_{order['id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            format_order(order),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /pending command
    Shows all pending orders (admin only)
    """
    if update.effective_user.id not in ADMIN_IDS:
        return

    with get_db() as conn:
        cursor = get_cursor(conn)
        cursor.execute('''
            SELECT o.*,
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' ||
                       oi.quantity || ':' || oi.price || ':' ||
                   ) as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status = 'pending'
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''')
        orders = cursor.fetchall()

    if not orders:
        await update.message.reply_text("✅ Новых заказов нет")
        return

    await update.message.reply_text(
        f"🕐 <b>Новых заказов: {len(orders)}</b>",
        parse_mode='HTML'
    )

    for order in orders:
        keyboard = [
            [
                InlineKeyboardButton("✅ Принять", callback_data=f"status_{order['id']}_confirmed"),
                InlineKeyboardButton("❌ Отменить", callback_data=f"status_{order['id']}_cancelled")
            ],
            [InlineKeyboardButton("📝 Подробнее", callback_data=f"order_detail_{order['id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            format_order(order),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /stats command
    Shows order statistics (admin only)
    """
    if update.effective_user.id not in ADMIN_IDS:
        return

    with get_db() as conn:
        cursor = get_cursor(conn)

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
📊 <b>Статистика Home Food</b>

📦 <b>Всего заказов:</b> {total_orders}
🍽️ <b>Блюд в меню:</b> {total_products}
💰 <b>Общая сумма:</b> {total_amount:.1f} AED

<b>По статусам:</b>
"""

    status_emoji = {
        'pending': '🕐',
        'confirmed': '✅',
        'cooking': '👨‍🍳',
        'ready': '🎉',
        'delivered': '📦',
        'cancelled': '❌'
    }

    for stat in status_stats:
        emoji = status_emoji.get(stat['status'], '❓')
        stats_text += f"{emoji} {stat['status']}: {stat['count']} ({stat['total']:.1f} AED)\n"

    stats_text += f"\n📅 <b>Сегодня:</b> {today['count']} заказов ({today['total'] or 0:.1f} AED)"

    await update.message.reply_text(stats_text, parse_mode='HTML')


async def products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /products command
    Shows all products grouped by category (admin only)
    """
    if update.effective_user.id not in ADMIN_IDS:
        return

    with get_db() as conn:
        cursor = get_cursor(conn)
        cursor.execute('SELECT * FROM products ORDER BY category, name')
        products = cursor.fetchall()

    if not products:
        await update.message.reply_text("🍽️ Меню пока пустое. Используйте /addproduct для добавления блюд.")
        return

    # Group by categories
    categories = {}
    for p in products:
        cat = p['category'] or 'Без категории'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p)

    text = "🍽️ <b>Все блюда в меню:</b>\n\n"

    for cat, items in categories.items():
        text += f"<b>📂 {cat.upper()}</b>\n"
        for p in items:
            text += f"• {p['name']} - {p['price']} AED\n"
        text += "\n"

    keyboard = [
        [InlineKeyboardButton("➕ Добавить блюдо", callback_data="add_product")],
        [InlineKeyboardButton("🗑️ Удалить блюдо", callback_data="delete_product_list")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
