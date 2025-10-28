import asyncio
import sqlite3
import os
import json
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
    ConversationHandler,
)

# Попытка загрузить из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS_STR = os.getenv("ADMIN_IDS")
    ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]
    DATABASE = os.getenv("DATABASE", "homefood.db")
except:
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    ADMIN_IDS = [123456789]
    DATABASE = "homefood.db"

# === CONVERSATION STATES ===
(NAME, DESCRIPTION, PRICE, IMAGE, COOK_TELEGRAM, 
 CATEGORY, INGREDIENTS, CONFIRM) = range(8)

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

def init_database():
    """Инициализация базы данных"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Таблица продуктов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image TEXT,
                cook_telegram TEXT,
                category TEXT,
                ingredients TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица заказов с user_telegram_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_telegram_id INTEGER,
                customer_telegram TEXT,
                customer_address TEXT,
                customer_phone TEXT,
                total_amount REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица позиций заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT,
                product_id TEXT,
                product_name TEXT,
                quantity INTEGER,
                price REAL,
                cook_telegram TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        ''')
        
        # Проверяем, есть ли колонка user_telegram_id (для миграции старых БД)
        cursor.execute("PRAGMA table_info(orders)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_telegram_id' not in columns:
            print("🔄 Migrating database: adding user_telegram_id column...")
            cursor.execute('ALTER TABLE orders ADD COLUMN user_telegram_id INTEGER')
        
        conn.commit()

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
        'pending': 'Ожидает подтверждения',
        'confirmed': 'Подтвержден',
        'cooking': 'Готовится',
        'ready': 'Готов к получению',
        'delivered': 'Доставлен',
        'cancelled': 'Отменен'
    }
    
    emoji = status_emoji.get(order['status'], '❓')
    status_name = status_names.get(order['status'], order['status'])
    
    items_text = ""
    if order.get('items_data'):
        for item_str in order['items_data'].split(','):
            parts = item_str.split(':')
            product_name = parts[1] if len(parts) > 1 else 'Продукт'
            quantity = parts[2] if len(parts) > 2 else '0'
            price = parts[3] if len(parts) > 3 else '0'
            cook_telegram = parts[4] if len(parts) > 4 else ''
            
            cook_info = f" (👨‍🍳 @{cook_telegram})" if cook_telegram else ""
            items_text += f"  • {product_name} x{quantity} = {price} AED{cook_info}\n"
    
    created = datetime.fromisoformat(order['created_at']).strftime('%d.%m.%Y %H:%M')
    
    # Добавляем информацию о пользователе для админов
    user_info = ""
    if order.get('customer_telegram'):
        user_info = f"👤 <b>Telegram:</b> @{order['customer_telegram']}\n"
    
    return f"""
📋 <b>Заказ #{order['id'][:8]}</b>
{emoji} <b>Статус:</b> {status_name}

{user_info}📍 <b>Адрес:</b> {order.get('customer_address', 'Не указан')}
📞 <b>Телефон:</b> {order.get('customer_phone', 'Не указан')}

🛒 <b>Состав заказа:</b>
{items_text}
💰 <b>Итого:</b> {order['total_amount']} AED

🕐 <b>Создан:</b> {created}
"""

async def notify_user_status_change(application, order_id: str, new_status: str):
    """Отправить уведомление пользователю об изменении статуса заказа"""
    try:
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
            
            if not order or not order['user_telegram_id']:
                return
            
            order = dict(order)
            user_id = order['user_telegram_id']
            
            # Формируем сообщение для пользователя
            status_messages = {
                'confirmed': '✅ Ваш заказ подтвержден и принят в работу!',
                'cooking': '👨‍🍳 Ваш заказ готовится!',
                'ready': '🎉 Ваш заказ готов! Можете забирать.',
                'delivered': '📦 Заказ доставлен. Приятного аппетита!',
                'cancelled': '❌ К сожалению, ваш заказ отменен. Свяжитесь с поддержкой для уточнения.'
            }
            
            status_message = status_messages.get(new_status, f'Статус заказа изменен на: {new_status}')
            
            message = f"""
🔔 <b>Обновление заказа</b>

{status_message}

{format_order(order)}
"""
            
            await application.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML'
            )
            
    except Exception as e:
        print(f"Error sending notification to user: {e}")

# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id

    not_admin_keyboard = [
        [InlineKeyboardButton("🍱 Открыть меню", url="https://homemade-production.up.railway.app/app")],
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
    """Обработчик команды /help"""
    if not is_admin(update.effective_user.id):
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
                       COALESCE(oi.cook_telegram, '')
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

# === PRODUCT MANAGEMENT ===
async def products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все блюда"""
    if not is_admin(update.effective_user.id):
        return
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY category, name')
        products = [dict(row) for row in cursor.fetchall()]
    
    if not products:
        await update.message.reply_text("🍽️ Меню пока пустое. Используйте /addproduct для добавления блюд.")
        return
    
    # Группируем по категориям
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

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления блюда"""
    query = update.callback_query
    
    if query:
        await query.answer()
        if not is_admin(query.from_user.id):
            await query.edit_message_text("❌ У вас нет доступа")
            return ConversationHandler.END
        message = query.message
    else:
        if not is_admin(update.effective_user.id):
            return ConversationHandler.END
        message = update.message
    
    # Инициализируем временное хранилище
    context.user_data['new_product'] = {}
    
    await message.reply_text(
        "🍽️ <b>Добавление нового блюда</b>\n\n"
        "Шаг 1 из 8\n"
        "Введите <b>название блюда</b>:\n\n"
        "Например: Домашние пельмени\n\n"
        "Отправьте /cancel для отмены",
        parse_mode='HTML'
    )
    
    return NAME

async def product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение названия"""
    context.user_data['new_product']['name'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Название: <b>{update.message.text}</b>\n\n"
        "Шаг 2 из 8\n"
        "Введите <b>описание блюда</b>:\n\n"
        "Например: Сочные пельмени с говядиной и свининой, как в России",
        parse_mode='HTML'
    )
    
    return DESCRIPTION

async def product_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение описания"""
    context.user_data['new_product']['description'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Описание сохранено\n\n"
        "Шаг 3 из 8\n"
        "Введите <b>цену в AED</b> (только число):\n\n"
        "Например: 25",
        parse_mode='HTML'
    )
    
    return PRICE

async def product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение цены"""
    try:
        price = float(update.message.text)
        if price <= 0:
            raise ValueError
        
        context.user_data['new_product']['price'] = price
        
        await update.message.reply_text(
            f"✅ Цена: <b>{price} AED</b>\n\n"
            "Шаг 4 из 8\n"
            "Отправьте <b>ссылку на изображение блюда</b>:\n\n"
            "Можно использовать ссылки с Unsplash, Imgur и т.д.\n"
            "Например: https://images.unsplash.com/photo-1234567890",
            parse_mode='HTML'
        )
        
        return IMAGE
        
    except ValueError:
        await update.message.reply_text(
            "❌ Ошибка! Введите корректное число.\n"
            "Например: 25 или 35.5"
        )
        return PRICE

async def product_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение изображения"""
    image_url = update.message.text
    
    # Простая валидация URL
    if not (image_url.startswith('http://') or image_url.startswith('https://')):
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте полную ссылку, начинающуюся с http:// или https://"
        )
        return IMAGE
    
    context.user_data['new_product']['image'] = image_url
    
    await update.message.reply_text(
        f"✅ Изображение сохранено\n\n"
        "Шаг 5 из 7\n"
        "Введите <b>Telegram username повара</b> (без @):\n\n"
        "Например: turlubay",
        parse_mode='HTML'
    )
    
    return COOK_TELEGRAM

async def product_cook_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение Telegram username повара"""
    telegram_username = update.message.text.replace('@', '').strip()
    
    if not telegram_username:
        await update.message.reply_text(
            "❌ Пожалуйста, введите корректный Telegram username"
        )
        return COOK_TELEGRAM
    
    context.user_data['new_product']['cook_telegram'] = telegram_username
    
    keyboard = [
        [InlineKeyboardButton("🍔 burger", callback_data="cat_burger")],
        [InlineKeyboardButton("🍕 pizza", callback_data="cat_pizza")],
        [InlineKeyboardButton("🍚 plov", callback_data="cat_plov")],
        [InlineKeyboardButton("🍲 soup", callback_data="cat_soup")],
        [InlineKeyboardButton("🥟 pelmeni", callback_data="cat_pelmeni")],
        [InlineKeyboardButton("🥖 khachapuri", callback_data="cat_khachapuri")],
        [InlineKeyboardButton("🍰 dessert", callback_data="cat_dessert")],
        [InlineKeyboardButton("🥗 salad", callback_data="cat_salad")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Telegram: <b>@{telegram_username}</b>\n\n"
        "Шаг 6 из 7\n"
        "Выберите <b>категорию блюда</b>:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    return CATEGORY

async def product_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение категории"""
    query = update.callback_query
    await query.answer()
    
    category = query.data.replace('cat_', '')
    context.user_data['new_product']['category'] = category
    
    await query.edit_message_text(
        f"✅ Категория: <b>{category}</b>\n\n"
        "Шаг 7 из 7\n"
        "Введите <b>ингредиенты</b> через запятую:\n\n"
        "Например: Мука, Яйцо, Говядина, Свинина, Лук, Соль, Перец",
        parse_mode='HTML'
    )
    
    return INGREDIENTS

async def product_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение ингредиентов"""
    ingredients_str = update.message.text
    ingredients_list = [ing.strip() for ing in ingredients_str.split(',')]
    
    context.user_data['new_product']['ingredients'] = json.dumps(ingredients_list, ensure_ascii=False)
    
    # Формируем превью
    product = context.user_data['new_product']
    
    preview = f"""
📋 <b>Предпросмотр блюда:</b>

🍽️ <b>Название:</b> {product['name']}
📝 <b>Описание:</b> {product['description']}
💰 <b>Цена:</b> {product['price']} AED
🖼️ <b>Изображение:</b> {product['image'][:50]}...
👨‍🍳 <b>Повар:</b> @{product['cook_telegram']}
📂 <b>Категория:</b> {product['category']}
🥘 <b>Ингредиенты:</b> {', '.join(ingredients_list[:5])}{'...' if len(ingredients_list) > 5 else ''}

Всё верно?
"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, сохранить", callback_data="save_product"),
            InlineKeyboardButton("❌ Отменить", callback_data="cancel_product")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(preview, reply_markup=reply_markup, parse_mode='HTML')
    
    return CONFIRM

async def save_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение блюда в БД"""
    query = update.callback_query
    await query.answer()
    
    product = context.user_data.get('new_product')
    
    if not product:
        await query.edit_message_text("❌ Ошибка: данные блюда не найдены")
        return ConversationHandler.END
    
    # Генерируем ID
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(CAST(id AS INTEGER)) as max_id FROM products WHERE id NOT LIKE "%-%"')
        result = cursor.fetchone()
        new_id = str((result['max_id'] or 0) + 1)
        
        # Сохраняем
        cursor.execute('''
            INSERT INTO products (id, name, description, price, image, cook_telegram, category, ingredients)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            new_id,
            product['name'],
            product['description'],
            product['price'],
            product['image'],
            product['cook_telegram'],
            product['category'],
            product['ingredients']
        ))
        conn.commit()
    
    await query.edit_message_text(
        f"✅ <b>Блюдо успешно добавлено!</b>\n\n"
        f"ID: {new_id}\n"
        f"Название: {product['name']}\n"
        f"Цена: {product['price']} AED\n"
        f"Категория: {product['category']}\n\n"
        f"Теперь оно доступно в мини-аппе!",
        parse_mode='HTML'
    )
    
    # Очищаем данные
    context.user_data.clear()
    
    return ConversationHandler.END

async def cancel_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена добавления"""
    query = update.callback_query if update.callback_query else None
    
    if query:
        await query.answer()
        await query.edit_message_text("❌ Добавление блюда отменено")
    else:
        await update.message.reply_text("❌ Добавление блюда отменено")
    
    context.user_data.clear()
    return ConversationHandler.END

# === CALLBACK HANDLERS ===
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # Обработка "Мои заказы" для обычных пользователей
    if data == "my_orders":
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
                LIMIT 10
            ''', (user_id,))
            orders = [dict(row) for row in cursor.fetchall()]

        if not orders:
            await query.edit_message_text(
                "📭 <b>У тебя пока нет заказов</b>\n\n"
                "Открой меню и сделай свой первый заказ! 🍽️",
                parse_mode='HTML'
            )
            return

        await query.edit_message_text(
            f"📦 <b>Твои последние заказы ({len(orders)})</b>",
            parse_mode='HTML'
        )

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
        return

    # Только для админов
    if not is_admin(user_id):
        not_admin_keyboard = [
            [InlineKeyboardButton("🍱 Открыть меню", url="https://homemade-production.up.railway.app/app")],
            [InlineKeyboardButton("📦 Мои заказы", callback_data="my_orders")],
            [InlineKeyboardButton("💬 Связаться с поддержкой", url="https://t.me/sekeww")],
        ]
        await query.edit_message_text(
            "👋 Привет!\n\n"
            "Добро пожаловать в <b>HomeMade</b> — место, где вкус и уют встречаются прямо у тебя дома 🍲\n\n"
            "📱 Здесь ты можешь заказать домашнюю еду, приготовленную с любовью. Всё просто — выбирай, заказывай и наслаждайся 😋\n\n"
            "Готов начать?",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(not_admin_keyboard)
        )
        return
    
    # Управление меню
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
    
    # Список блюд
    if data == "list_products":
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM products')
            count = cursor.fetchone()['count']
        
        await query.edit_message_text(
            f"🍽️ В меню <b>{count}</b> блюд\n\n"
            "Используйте /products для просмотра",
            parse_mode='HTML'
        )
        return
    
    # Назад в главное меню
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
    
    # Показать все заказы
    if data == "orders_all":
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
    
    # Показать новые заказы
    elif data == "orders_pending":
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
    
    # Показать заказы в работе
    elif data == "orders_cooking":
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
        
        # Разные кнопки для админов и пользователей
        if is_admin(user_id):
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
        else:
            keyboard = [
                [InlineKeyboardButton("🔙 К моим заказам", callback_data="my_orders")]
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
                'UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
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
        
        # Отправляем уведомление пользователю
        await notify_user_status_change(context.application, order_id, new_status)
        
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
    
    # Удаление блюда - показать список
    elif data == "delete_product_list":
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, category, price FROM products ORDER BY category, name LIMIT 20')
            products = [dict(row) for row in cursor.fetchall()]
        
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
    
    # Подтверждение удаления
    elif data.startswith("delete_prod_"):
        product_id = data.replace("delete_prod_", "")
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM products WHERE id = ?', (product_id,))
            product = cursor.fetchone()
            
            if product:
                cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                conn.commit()
                await query.edit_message_text(
                    f"✅ Блюдо <b>{product['name']}</b> удалено из меню",
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text("❌ Блюдо не найдено")

def create_application():
    """Создать и настроить application без запуска"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ОШИБКА: Установите BOT_TOKEN!")
        return None
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler для добавления продукта
    add_product_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_product_start, pattern="^add_product$"),
            CommandHandler("addproduct", add_product_start)
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_name)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_description)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_price)],
            IMAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_image)],
            COOK_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_cook_telegram)],
            CATEGORY: [CallbackQueryHandler(product_category, pattern="^cat_")],
            INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_ingredients)],
            CONFIRM: [
                CallbackQueryHandler(save_product, pattern="^save_product$"),
                CallbackQueryHandler(cancel_product, pattern="^cancel_product$")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_product),
            CallbackQueryHandler(cancel_product, pattern="^cancel_product$")
        ],
    )
    
    # Регистрируем обработчики
    application.add_handler(add_product_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("orders", orders_command))
    application.add_handler(CommandHandler("pending", pending_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("products", products_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    return application

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
    
    # Инициализируем базу данных
    init_database()
    print("✅ База данных инициализирована")
    
    application = create_application()
    
    if application:
        print("✅ Бот запущен и готов к работе!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()