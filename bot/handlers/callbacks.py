"""
Callback Query Handlers
Handles button clicks and inline keyboard interactions
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..config import ADMIN_IDS
from ..utils import format_order

# Import from root database module (not bot.database)
from database import db

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


def fix_query(query: str) -> str:
    """Convert ? placeholders to %s for PostgreSQL"""
    if db.use_postgres:
        return query.replace('?', '%s')
    return query


def get_agg_func():
    """Get the appropriate aggregation function for the current database"""
    if db.use_postgres:
        return "STRING_AGG(oi.product_id || ':' || oi.product_name || ':' || oi.quantity || ':' || oi.price || ':', ',')"
    else:
        return "GROUP_CONCAT(oi.product_id || ':' || oi.product_name || ':' || oi.quantity || ':' || oi.price || ':')"


def get_orders_query(status_filter=None):
    """Get SQL query for fetching orders (handles PostgreSQL vs SQLite)"""
    agg_func = get_agg_func()

    # Handle single status, list of statuses, or no filter
    if status_filter:
        if isinstance(status_filter, list):
            statuses = "', '".join(status_filter)
            where_clause = f"WHERE o.status IN ('{statuses}')"
        else:
            where_clause = f"WHERE o.status = '{status_filter}'"
    else:
        where_clause = ""

    return f'''
        SELECT o.*,
               {agg_func} as items_data
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        {where_clause}
        GROUP BY o.id
        ORDER BY o.created_at DESC
        LIMIT 5
    '''


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main callback handler for all inline keyboard button presses
    Routes to appropriate action based on callback_data
    """
    query = update.callback_query
    await query.answer()

    not_admin_keyboard = [
        [InlineKeyboardButton("🍱 Открыть меню", url="https://homemade-production.up.railway.app/app")],
        [InlineKeyboardButton("Мои заказы", callback_data="my_orders")],
        [InlineKeyboardButton("Связаться с поддержкой", url="https://t.me/sekeww")],
    ]

    # Check if user is admin for most operations
    if query.from_user.id not in ADMIN_IDS:
        await query.edit_message_text(
            "👋 Привет!\n\n"
            "Добро пожаловать в <b>HomeMade</b> — место, где вкус и уют встречаются прямо у тебя дома 🍲\n\n"
            "📱 Здесь ты можешь заказать домашнюю еду, приготовленную с любовью. Всё просто — выбирай, заказывай и наслаждайся 😋\n\n"
            "Готов начать?",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(not_admin_keyboard)
        )
        return

    data = query.data

    # === MENU MANAGEMENT ===
    if data == "menu_manage":
        keyboard = [
            [InlineKeyboardButton("➕ Добавить блюдо", callback_data="add_product")],
            [InlineKeyboardButton("📋 Список блюд", callback_data="list_products")],
            [InlineKeyboardButton("🗑️ Удалить блюдо", callback_data="delete_product_list")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🍽️ <b>Управление меню</b>\n\nВыберите действие:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return

    # === LIST PRODUCTS ===
    if data == "list_products":
        with get_db() as conn:
            cursor = get_cursor(conn)
            cursor.execute('SELECT COUNT(*) as count FROM products')
            count = cursor.fetchone()['count']

        await query.edit_message_text(
            f"🍽️ В меню <b>{count}</b> блюд\n\n"
            "Используйте /products для просмотра",
            parse_mode='HTML'
        )
        return

    # === BACK TO MAIN ===
    if data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("📦 Все заказы", callback_data="orders_all")],
            [InlineKeyboardButton("🕐 Новые заказы", callback_data="orders_pending")],
            [InlineKeyboardButton("👨‍🍳 В работе", callback_data="orders_cooking")],
            [InlineKeyboardButton("🍽️ Управление меню", callback_data="menu_manage")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🍽️ <b>Home Food Admin Panel</b>\n\nВыберите действие:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return

    # === ALL ORDERS ===
    if data == "orders_all":
        with get_db() as conn:
            cursor = get_cursor(conn)
            cursor.execute(get_orders_query())
            orders = cursor.fetchall()

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

    # === PENDING ORDERS ===
    elif data == "orders_pending":
        with get_db() as conn:
            cursor = get_cursor(conn)
            cursor.execute(get_orders_query('pending'))
            orders = cursor.fetchall()

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

    # === COOKING ORDERS ===
    elif data == "orders_cooking":
        with get_db() as conn:
            cursor = get_cursor(conn)
            cursor.execute(get_orders_query(['confirmed', 'cooking']))
            orders = cursor.fetchall()

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

    # === MY ORDERS (for regular users) ===
    elif data == "my_orders":
        user_id = query.from_user.id

        with get_db() as conn:
            cursor = get_cursor(conn)
            agg_func = get_agg_func()
            query_sql = f'''
                SELECT o.*,
                       {agg_func} as items_data
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_telegram_id = {fix_query('?')}
                GROUP BY o.id
                ORDER BY o.created_at DESC
                LIMIT 5
            '''
            cursor.execute(query_sql, (user_id,))
            orders = cursor.fetchall()

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

    # === STATISTICS ===
    elif data == "stats":
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
📊 <b>Статистика</b>

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

    # === ORDER DETAILS ===
    elif data.startswith("order_detail_"):
        order_id = data.replace("order_detail_", "")

        with get_db() as conn:
            cursor = get_cursor(conn)
            agg_func = get_agg_func()
            query_sql = f'''
                SELECT o.*,
                       {agg_func} as items_data
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.id = {fix_query('?')}
                GROUP BY o.id
            '''
            cursor.execute(query_sql, (order_id,))
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
            ],
            [
                InlineKeyboardButton("🔙 Назад", callback_data="orders_all")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            format_order(order),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    # === CHANGE ORDER STATUS ===
    elif data.startswith("status_"):
        parts = data.split("_")
        order_id = parts[1]
        new_status = parts[2]

        with get_db() as conn:
            cursor = get_cursor(conn)
            cursor.execute(
                fix_query('UPDATE orders SET status = ?, created_at = CURRENT_TIMESTAMP WHERE id = ?'),
                (new_status, order_id)
            )
            conn.commit()

            agg_func = get_agg_func()
            query_sql = f'''
                SELECT o.*,
                       {agg_func} as items_data
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.id = {fix_query('?')}
                GROUP BY o.id
            '''
            cursor.execute(query_sql, (order_id,))
            order = dict(cursor.fetchone())

        keyboard = [
            [InlineKeyboardButton("📝 Подробнее", callback_data=f"order_detail_{order_id}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="orders_all")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"✅ <b>Статус обновлен!</b>\n\n{format_order(order)}",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    # === DELETE PRODUCT LIST ===
    elif data == "delete_product_list":
        with get_db() as conn:
            cursor = get_cursor(conn)
            cursor.execute('SELECT id, name, category, price FROM products ORDER BY category, name LIMIT 20')
            products = cursor.fetchall()

        if not products:
            await query.edit_message_text("🍽️ Меню пустое, нечего удалять")
            return

        keyboard = []
        for p in products:
            keyboard.append([InlineKeyboardButton(
                f"🗑️ {p['name']} ({p['price']} AED)",
                callback_data=f"delete_prod_{p['id']}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 Отмена", callback_data="menu_manage")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🗑️ <b>Удалить блюдо</b>\n\nВыберите блюдо для удаления:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    # === CONFIRM DELETE PRODUCT ===
    elif data.startswith("delete_prod_"):
        product_id = data.replace("delete_prod_", "")

        with get_db() as conn:
            cursor = get_cursor(conn)
            cursor.execute(fix_query('SELECT name FROM products WHERE id = ?'), (product_id,))
            product = cursor.fetchone()

            if product:
                cursor.execute(fix_query('DELETE FROM products WHERE id = ?'), (product_id,))
                conn.commit()
                await query.edit_message_text(
                    f"✅ Блюдо <b>{product['name']}</b> удалено из меню",
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text("❌ Блюдо не найдено")
