import asyncio
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Попытка загрузить из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8349545325:AAFdqJ5Tni7ZzC_owo_8fBQe2n0rXq46m_Q")
    ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "795821176")
    ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]
    DATABASE = os.getenv("DATABASE", "homefood.db")
except:
    # Если нет python-dotenv или .env файла, используем значения по умолчанию
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Получите у @BotFather
    ADMIN_IDS = [123456789]  # Замените на ваш Telegram ID
    DATABASE = "homefood.db"

# === DATABASE ===
@contextmanager
def get_db():
    """Контекстный менеджер для работы с БД"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# === HELPER FUNCTIONS ===
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
    
    # Парсим items
    items_text = ""
    if order.get('items_data'):
        for item_str in order['items_data'].split(','):
            parts = item_str.split(':')
            product_name = parts[1] if len(parts) > 1 else 'Продукт'
            quantity = parts[2] if len(parts) > 2 else '0'
            price = parts[3] if len(parts) > 3 else '0'
            items_text += f"  • {product_name} x{quantity} = {price} AED\n"
    
    created = datetime.fromisoformat(order['created_at']).strftime('%d.%m.%Y %H:%M')
    
    return f"""
📋 <b>Заказ #{order['id'][:8]}</b>
{emoji} <b>Статус:</b> {status_name}

👤 <b>Клиент:</b> {order['customer_name']}
📱 <b>Телефон:</b> {order['customer_phone']}
📍 <b>Адрес:</b> {order['customer_address']}

🛒 <b>Состав заказа:</b>
{items_text}
💰 <b>Итого:</b> {order['total_amount']} AED

🕐 <b>Создан:</b> {created}
"""

# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ У вас нет доступа к админ-панели.\n"
            f"Ваш ID: {user_id}"
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("📦 Все заказы", callback_data="orders_all")],
        [InlineKeyboardButton("🕐 Новые заказы", callback_data="orders_pending")],
        [InlineKeyboardButton("👨‍🍳 В работе", callback_data="orders_cooking")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🍽️ <b>Home Food Admin Panel</b>\n\n"
        "Добро пожаловать в панель управления!\n"
        "Выберите действие:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    if not is_admin(update.effective_user.id):
        return
    
    help_text = """
🤖 <b>Команды бота:</b>

/start - Главное меню
/orders - Все заказы
/pending - Новые заказы
/stats - Статистика
/help - Эта справка

<b>Функции:</b>
• Просмотр всех заказов
• Изменение статуса заказов
• Просмотр статистики
• Управление заказами
"""
    await update.message.reply_text(help_text, parse_mode='HTML')

async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /orders - показать все заказы"""
    if not is_admin(update.effective_user.id):
        return
    
    with get_db() as conn:
        cursor = conn.cursor()
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
        orders = [dict(row) for row in cursor.fetchall()]
    
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
    """Обработчик команды /pending - новые заказы"""
    if not is_admin(update.effective_user.id):
        return
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*, 
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' || 
                       oi.quantity || ':' || oi.price || ':' || 
                       COALESCE(oi.cook_name, '') || ':' || COALESCE(oi.cook_phone, '')
                   ) as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status = 'pending'
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''')
        orders = [dict(row) for row in cursor.fetchall()]
    
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
    """Обработчик команды /stats - статистика"""
    if not is_admin(update.effective_user.id):
        return
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Общее количество заказов
        cursor.execute('SELECT COUNT(*) as count FROM orders')
        total_orders = cursor.fetchone()['count']
        
        # Заказы по статусам
        cursor.execute('''
            SELECT status, COUNT(*) as count, SUM(total_amount) as total
            FROM orders
            GROUP BY status
        ''')
        status_stats = cursor.fetchall()
        
        # Общая сумма
        cursor.execute('SELECT SUM(total_amount) as total FROM orders')
        total_amount = cursor.fetchone()['total'] or 0
        
        # Сегодняшние заказы
        cursor.execute('''
            SELECT COUNT(*) as count, SUM(total_amount) as total
            FROM orders
            WHERE DATE(created_at) = DATE('now')
        ''')
        today = cursor.fetchone()
    
    stats_text = f"""
📊 <b>Статистика Home Food</b>

📦 <b>Всего заказов:</b> {total_orders}
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

# === CALLBACK HANDLERS ===
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ У вас нет доступа")
        return
    
    data = query.data
    
    # Показать все заказы
    if data == "orders_all":
        with get_db() as conn:
            cursor = conn.cursor()
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
    
    # Показать новые заказы
    elif data == "orders_pending":
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT o.*, 
                       GROUP_CONCAT(
                           oi.product_id || ':' || oi.product_name || ':' || 
                           oi.quantity || ':' || oi.price || ':' || 
                           COALESCE(oi.cook_name, '') || ':' || COALESCE(oi.cook_phone, '')
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
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                format_order(order),
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    # Показать заказы в работе
    elif data == "orders_cooking":
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT o.*, 
                       GROUP_CONCAT(
                           oi.product_id || ':' || oi.product_name || ':' || 
                           oi.quantity || ':' || oi.price || ':' || 
                           COALESCE(oi.cook_name, '') || ':' || COALESCE(oi.cook_phone, '')
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
    
    # Статистика
    elif data == "stats":
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
        
        stats_text = f"""
📊 <b>Статистика</b>

📦 Всего заказов: {total_orders}
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
    
    # Подробности заказа
    elif data.startswith("order_detail_"):
        order_id = data.replace("order_detail_", "")
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT o.*, 
                       GROUP_CONCAT(
                           oi.product_id || ':' || oi.product_name || ':' || 
                           oi.quantity || ':' || oi.price || ':' || 
                           COALESCE(oi.cook_name, '') || ':' || COALESCE(oi.cook_phone, '')
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
    
    # Изменение статуса
    elif data.startswith("status_"):
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
            
            # Получаем обновленный заказ
            cursor.execute('''
                SELECT o.*, 
                       GROUP_CONCAT(
                           oi.product_id || ':' || oi.product_name || ':' || 
                           oi.quantity || ':' || oi.price || ':' || 
                           COALESCE(oi.cook_name, '') || ':' || COALESCE(oi.cook_phone, '')
                       ) as items_data
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.id = ?
                GROUP BY o.id
            ''', (order_id,))
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

# === MAIN ===
def main():
    """Запуск бота"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ОШИБКА: Установите BOT_TOKEN в коде!")
        print("1. Создайте бота у @BotFather")
        print("2. Получите токен")
        print("3. Замените YOUR_BOT_TOKEN_HERE на ваш токен")
        return
    
    if ADMIN_IDS == [123456789]:
        print("⚠️ ВНИМАНИЕ: Установите ваш Telegram ID в ADMIN_IDS!")
        print("Отправьте /start боту @userinfobot чтобы узнать свой ID")
    
    print("🤖 Запуск Telegram бота...")
    print(f"📊 База данных: {DATABASE}")
    print(f"👥 Админы: {ADMIN_IDS}")
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("orders", orders_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Запускаем бота
    print("✅ Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()