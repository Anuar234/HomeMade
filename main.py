from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
import os
import sqlite3
from datetime import datetime
from contextlib import contextmanager

app = FastAPI(title="Home Food Abu Dhabi!")

app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS для работы с Telegram Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === DATABASE SETUP ===
DATABASE = "homefood.db"

@contextmanager
def get_db():
    """Контекстный менеджер для работы с БД"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
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
                cook_name TEXT,
                cook_phone TEXT,
                category TEXT,
                ingredients TEXT
            )
        ''')
        
        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                customer_address TEXT,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица элементов заказа
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                cook_name TEXT,
                cook_phone TEXT,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        conn.commit()

        # Добавляем недостающие колонки
        add_missing_columns_legacy()

        # Заполняем начальными данными, если таблица пустая
        cursor.execute('SELECT COUNT(*) as count FROM products')
        if cursor.fetchone()['count'] == 0:
            seed_products(conn)

def add_missing_columns_legacy():
    """Добавляет недостающие колонки в существующую БД (для main.py)"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Добавляем customer_telegram в orders
        try:
            cursor.execute("SELECT customer_telegram FROM orders LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE orders ADD COLUMN customer_telegram TEXT")
            print("✅ Добавлена колонка customer_telegram в таблицу orders")

        # Добавляем user_telegram_id в orders
        try:
            cursor.execute("SELECT user_telegram_id FROM orders LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE orders ADD COLUMN user_telegram_id INTEGER")
            print("✅ Добавлена колонка user_telegram_id в таблицу orders")

        # Добавляем cook_telegram в products
        try:
            cursor.execute("SELECT cook_telegram FROM products LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE products ADD COLUMN cook_telegram TEXT")
            print("✅ Добавлена колонка cook_telegram в таблицу products")

        # Добавляем cook_telegram в order_items
        try:
            cursor.execute("SELECT cook_telegram FROM order_items LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE order_items ADD COLUMN cook_telegram TEXT")
            print("✅ Добавлена колонка cook_telegram в таблицу order_items")

        conn.commit()

def seed_products(conn):
    """Заполнение БД начальными данными"""
    products = [
        {
            "id": "1",
            "name": "Домашние пельмени",
            "description": "Сочные пельмени с говядиной и свининой, как в России",
            "price": 25.0,
            "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300",
            "cook_name": "Анна Петрова",
            "cook_phone": "+971501234567",
            "category": "pelmeni",
            "ingredients": '["Мука", "Яйцо", "Говядина", "Свинина", "Лук", "Соль", "Перец"]'
        },
        {
            "id": "2", 
            "name": "Узбекский плов",
            "description": "Настоящий узбекский плов с бараниной и специями",
            "price": 30.0,
            "image": "https://images.unsplash.com/photo-1596040033229-a0b3b7f5c777?w=300",
            "cook_name": "Фарход Алиев",
            "cook_phone": "+971507654321",
            "category": "plov",
            "ingredients": '["Рис", "Баранина", "Морковь", "Лук", "Чеснок", "Зира", "Масло"]'
        },
        {
            "id": "3",
            "name": "Домашний борщ",
            "description": "Украинский борщ с говядиной и сметаной",
            "price": 18.0,
            "image": "https://images.unsplash.com/photo-1571064247530-4146bc1a081b?w=300",
            "cook_name": "Оксана Коваль",
            "cook_phone": "+971509876543",
            "category": "soup",
            "ingredients": '["Свекла", "Говядина", "Капуста", "Картофель", "Морковь", "Лук", "Сметана"]'
        },
        {
            "id": "4",
            "name": "Хачапури по-аджарски",
            "description": "Грузинский хачапури с сыром и яйцом",
            "price": 22.0,
            "image": "https://images.unsplash.com/photo-1627662235973-4d265e175fc1?w=300",
            "cook_name": "Нино Джавахишвили",
            "cook_phone": "+971508765432",
            "category": "khachapuri",
            "ingredients": '["Мука", "Сыр", "Яйцо", "Молоко", "Масло"]'
        },
        {
            "id": "5",
            "name": "Домашний бургер",
            "description": "Сочный бургер с говяжьей котлетой и свежими овощами",
            "price": 35.0,
            "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300",
            "cook_name": "Михаил Сидоров",
            "cook_phone": "+971501111111",
            "category": "burger",
            "ingredients": '["Булочка", "Говядина", "Сыр", "Салат", "Помидор", "Лук", "Соус"]'
        },
        {
            "id": "6",
            "name": "Пицца Маргарита",
            "description": "Классическая итальянская пицца с моцареллой и базиликом",
            "price": 28.0,
            "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300",
            "cook_name": "Джованни Росси",
            "cook_phone": "+971502222222",
            "category": "pizza",
            "ingredients": '["Тесто", "Томатный соус", "Моцарелла", "Базилик", "Оливковое масло"]'
        }
    ]
    
    cursor = conn.cursor()
    for product in products:
        cursor.execute('''
            INSERT INTO products (id, name, description, price, image, cook_name, cook_phone, category, ingredients)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product['id'],
            product['name'],
            product['description'],
            product['price'],
            product['image'],
            product['cook_name'],
            product['cook_phone'],
            product['category'],
            product['ingredients']
        ))
    conn.commit()

# Инициализируем БД при старте
init_db()

# === TELEGRAM NOTIFICATIONS ===
async def send_telegram_notifications(order: dict):
    """Отправка уведомлений в Telegram о новом заказе"""
    try:
        from dotenv import load_dotenv
        load_dotenv()

        BOT_TOKEN = os.getenv("BOT_TOKEN")
        ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
        ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]

        if not BOT_TOKEN:
            print("⚠️ BOT_TOKEN не установлен, уведомления не отправлены")
            return

        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)

        # Форматируем заказ для отображения
        status_emoji = {
            'pending': '🕐',
            'confirmed': '✅',
            'cooking': '👨‍🍳',
            'ready': '🎉',
            'delivered': '📦',
            'cancelled': '❌'
        }

        emoji = status_emoji.get(order.get('status', 'pending'), '🕐')

        items_text = ""
        if order.get('items_data'):
            for item_str in order['items_data'].split(','):
                parts = item_str.split(':')
                if len(parts) >= 4:
                    product_name = parts[1]
                    quantity = parts[2]
                    price = parts[3]
                    cook_telegram = parts[4] if len(parts) > 4 else ''

                    cook_info = f" (👨‍🍳 @{cook_telegram})" if cook_telegram else ""
                    items_text += f"  • {product_name} x{quantity} = {price} AED{cook_info}\n"

        created = datetime.fromisoformat(order['created_at']).strftime('%d.%m.%Y %H:%M')

        customer_telegram = order.get('customer_telegram', 'Не указан')
        telegram_display = f"@{customer_telegram}" if customer_telegram and customer_telegram != 'Не указан' else customer_telegram

        # Сообщение для админов
        admin_message = f"""
🔔 <b>НОВЫЙ ЗАКАЗ!</b>

📋 <b>Заказ #{order['id']}</b>
{emoji} <b>Статус:</b> Ожидает обработки

👤 <b>Имя:</b> {order.get('customer_name', 'Не указано')}
📱 <b>Telegram:</b> {telegram_display}
📍 <b>Адрес:</b> {order.get('customer_address', 'Не указан')}
📞 <b>Телефон:</b> {order.get('customer_phone', 'Не указан')}

🛒 <b>Состав заказа:</b>
{items_text}
💰 <b>Итого:</b> {order['total_amount']} AED

🕐 <b>Создан:</b> {created}

<b>Пожалуйста, обработайте заказ через /start</b>
"""

        # Сообщение для пользователя
        user_message = f"""
✅ <b>Ваш заказ создан!</b>

📋 <b>Заказ #{order['id']}</b>
{emoji} <b>Статус:</b> Ожидает подтверждения

🛒 <b>Состав заказа:</b>
{items_text}
💰 <b>Итого:</b> {order['total_amount']} AED

📍 <b>Адрес доставки:</b> {order.get('customer_address', 'Не указан')}

<b>Мы свяжемся с вами в ближайшее время!</b>
Вы можете отслеживать статус заказа через /start → "Мои заказы"
"""

        # Отправляем админам
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    parse_mode='HTML'
                )
                print(f"✅ Уведомление отправлено админу {admin_id}")
            except Exception as e:
                print(f"❌ Ошибка отправки админу {admin_id}: {e}")

        # Отправляем пользователю
        user_telegram_id = order.get('user_telegram_id')
        if user_telegram_id:
            try:
                await bot.send_message(
                    chat_id=user_telegram_id,
                    text=user_message,
                    parse_mode='HTML'
                )
                print(f"✅ Уведомление отправлено пользователю {user_telegram_id}")
            except Exception as e:
                print(f"❌ Ошибка отправки пользователю {user_telegram_id}: {e}")
                print(f"   Возможно, пользователь не написал боту /start")
        else:
            print("⚠️ user_telegram_id не указан, уведомление пользователю не отправлено")

    except Exception as e:
        print(f"❌ Ошибка отправки уведомлений: {e}")
        import traceback
        traceback.print_exc()

async def send_status_update_notification(order: dict):
    """Отправка уведомления пользователю об изменении статуса заказа"""
    try:
        from dotenv import load_dotenv
        load_dotenv()

        BOT_TOKEN = os.getenv("BOT_TOKEN")
        user_telegram_id = order.get('user_telegram_id')

        if not BOT_TOKEN:
            print("⚠️ BOT_TOKEN не установлен, уведомление не отправлено")
            return

        if not user_telegram_id:
            print("⚠️ user_telegram_id не указан, уведомление не отправлено")
            return

        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)

        # Статусы на русском
        status_names = {
            'pending': '🕐 Ожидает обработки',
            'confirmed': '✅ Подтвержден',
            'cooking': '👨‍🍳 Готовится',
            'ready': '🎉 Готов к получению',
            'delivered': '📦 Доставлен',
            'cancelled': '❌ Отменен'
        }

        status = order.get('status', 'pending')
        status_text = status_names.get(status, status)

        items_text = ""
        if order.get('items_data'):
            for item_str in order['items_data'].split(','):
                parts = item_str.split(':')
                if len(parts) >= 4:
                    product_name = parts[1]
                    quantity = parts[2]
                    items_text += f"  • {product_name} x{quantity}\n"

        message = f"""
📢 <b>Обновление статуса заказа</b>

📋 <b>Заказ #{order['id']}</b>
{status_text}

🛒 <b>Состав:</b>
{items_text}
💰 <b>Итого:</b> {order['total_amount']} AED

📍 <b>Адрес:</b> {order.get('customer_address', 'Не указан')}
"""

        # Дополнительная информация в зависимости от статуса
        if status == 'confirmed':
            message += "\n<b>Ваш заказ принят в работу!</b> Ожидайте начала приготовления."
        elif status == 'cooking':
            message += "\n<b>Ваш заказ готовится!</b> Скоро всё будет готово 👨‍🍳"
        elif status == 'ready':
            message += "\n<b>Ваш заказ готов!</b> Ожидайте доставку 🎉"
        elif status == 'delivered':
            message += "\n<b>Приятного аппетита!</b> Спасибо за заказ! 😊"
        elif status == 'cancelled':
            message += "\n<b>Заказ отменен.</b> Если у вас есть вопросы, свяжитесь с поддержкой."

        await bot.send_message(
            chat_id=user_telegram_id,
            text=message,
            parse_mode='HTML'
        )
        print(f"✅ Уведомление о статусе '{status}' отправлено пользователю {user_telegram_id}")

    except Exception as e:
        print(f"❌ Ошибка отправки уведомления о статусе: {e}")
        print(f"   Возможно, пользователь не написал боту /start")

# === MODELS ===
class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    image: str
    cook_name: str
    cook_phone: str
    category: str
    ingredients: Optional[List[str]] = []

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    id: Optional[str] = None
    customer_name: str
    customer_phone: str
    customer_address: str
    customer_telegram: Optional[str] = None
    user_telegram_id: Optional[int] = None
    items: List[OrderItem]
    total_amount: Optional[float] = None
    status: str = "pending"
    created_at: Optional[str] = None

# === ROUTES ===

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с приложением"""
    return HTMLResponse("""
    <html>
    <body style="text-align: center; padding: 50px; font-family: sans-serif;">
        <h1>🍽️ Home Food Abu Dhabi</h1>
        <p>API работает! Добро пожаловать в сервис домашней еды.</p>
        <div style="margin-top: 30px;">
            <a href="/app" style="background: #0088ff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 10px; display: inline-block;">
                📱 Открыть приложение
            </a>
            <br><br>
            <a href="/api/products" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 10px; display: inline-block;">
                📋 API продуктов
            </a>
            <br><br>
            <a href="/api/orders" style="background: #ffc107; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 10px; display: inline-block;">
                📦 Все заказы
            </a>
        </div>
    </body>
    </html>
    """)

@app.get("/app", response_class=HTMLResponse)
async def get_app():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Home Food Abu Dhabi</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
        <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
        <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
        padding: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: 0;
        min-height: 100vh;
    }

    .header {
        text-align: center;
        margin-bottom: 16px;
        color: white;
    }

    .search-input {
        width: 100%;
        padding: 12px 16px;
        border-radius: 15px;
        border: none;
        font-size: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        background: rgba(255,255,255,0.9);
    }

    .icons-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        justify-items: center;
    }

    .icon-card {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        max-width: 150px;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.2);
    }

    .icon-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }

    .icon-card lottie-player {
        width: 100px;
        height: 100px;
    }

    .category-btn {
        margin-top: 10px;
        padding: 12px 20px;
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border: none;
        border-radius: 15px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .category-btn:hover {
        background: linear-gradient(45deg, #45a049, #4CAF50);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(76,175,80,0.4);
    }

    @media (max-width: 400px) {
        .icon-card {
            max-width: 130px;
            padding: 16px;
        }

        .icon-card lottie-player {
            width: 80px;
            height: 80px;
        }

        .category-btn {
            font-size: 12px;
            padding: 10px 16px;
        }
    }
</style>

    </head>
    <body>
        <div id="app">
            <div class="header">
                <h2>🍽️ Home Food Abu Dhabi</h2>
                <input 
                    v-model="searchQuery"
                    type="text"
                    class="search-input"
                    placeholder="🔍 Найти блюдо..."
                >
            </div>

            <div class="icons-grid">
    <div 
        v-for="cat in categories" 
        :key="cat.name" 
        class="icon-card"
    >
        <lottie-player
            :src="cat.icon"
            background="transparent"
            speed="1"
            style="width: 120px; height: 120px; margin: 0 auto;"
            loop autoplay>
        </lottie-player>

        <button class="category-btn" @click="goToCategory(cat)">
            {{ cat.label }}
        </button>
    </div>
</div>

        </div>

        <script>
        const { createApp, ref } = Vue;
        createApp({
            setup() {
                const searchQuery = ref('');
                const categories = ref([
                    { name: "burger", label: "Бургеры", icon: "/static/stickers_animations/burger.json" },
                    { name: "pizza", label: "Пицца", icon: "/static/stickers_animations/pizza.json" },
                    { name: "plov", label: "Плов", icon: "/static/stickers_animations/cake.json" },
                    { name: "soup", label: "Супы", icon: "/static/stickers_animations/cookie.json" },
                    { name: "pelmeni", label: "Пельмени", icon: "/static/stickers_animations/pie.json" },
                    { name: "khachapuri", label: "Хачапури", icon: "/static/stickers_animations/donut.json" },
                ]);

                const goToCategory = (cat) => {
                    window.location.href = `/app/${cat.name}?q=${encodeURIComponent(searchQuery.value)}`;
                };

                return { searchQuery, categories, goToCategory };
            }
        }).mount('#app');
        </script>
    </body>
    </html>
    """)

@app.get("/app/{category}")
async def get_app_category(category: str):
    category_names = {
        "burger": "Бургеры",
        "pizza": "Пицца", 
        "plov": "Плов",
        "soup": "Супы",
        "pelmeni": "Пельмени",
        "khachapuri": "Хачапури",
        "samsa": "Самса",
        "shashlik": "Шашлык"
    }
    
    category_display = category_names.get(category.lower(), category.capitalize())
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{category_display} - Home Food Abu Dhabi</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                padding: 0;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            
            .header {{
                background: rgba(255,255,255,0.95);
                backdrop-filter: blur(10px);
                padding: 16px;
                box-shadow: 0 2px 20px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                position: sticky;
                top: 0;
                z-index: 100;
            }}
            
            .header h2 {{
                margin: 0;
                color: #333;
                text-align: center;
                font-size: 24px;
            }}
            
            .back-btn {{
                background: #6c63ff;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 14px;
                cursor: pointer;
                margin-bottom: 10px;
                transition: all 0.3s ease;
            }}
            
            .back-btn:hover {{
                background: #5a52d5;
                transform: translateY(-1px);
            }}
            
            .cart-summary {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #ff6b6b;
                color: white;
                border-radius: 50px;
                padding: 12px 20px;
                box-shadow: 0 4px 20px rgba(255,107,107,0.3);
                cursor: pointer;
                font-weight: bold;
                z-index: 1000;
                transition: all 0.3s ease;
            }}
            
            .cart-summary:hover {{
                transform: scale(1.05);
                box-shadow: 0 6px 25px rgba(255,107,107,0.4);
            }}
            
            .products-container {{
                padding: 0 16px 100px 16px;
            }}
            
            .product-card {{ 
                background: rgba(255,255,255,0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.2);
            }}
            
            .product-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(0,0,0,0.15);
            }}
            
            .product-header {{
                display: flex;
                gap: 15px;
                margin-bottom: 15px;
            }}
            
            .product-img {{ 
                width: 100px;
                height: 80px;
                object-fit: cover;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                flex-shrink: 0;
            }}
            
            .product-info {{
                flex: 1;
            }}
            
            .product-name {{
                font-size: 18px;
                font-weight: bold;
                color: #333;
                margin: 0 0 5px 0;
            }}
            
            .product-description {{
                color: #666;
                font-size: 14px;
                line-height: 1.4;
                margin: 0;
            }}
            
            .price {{
                font-size: 20px;
                color: #4CAF50;
                font-weight: bold;
                margin: 10px 0;
            }}
            
            .ingredients-section {{
                background: rgba(241,245,249,0.8);
                border-radius: 12px;
                padding: 12px;
                margin: 15px 0;
            }}
            
            .ingredients-title {{
                font-size: 14px;
                font-weight: bold;
                color: #333;
                margin-bottom: 8px;
            }}
            
            .ingredients-list {{ 
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                margin: 0;
                padding: 0;
                list-style: none;
            }}
            
            .ingredient-tag {{
                background: rgba(255,255,255,0.8);
                border: 1px solid #ddd;
                border-radius: 20px;
                padding: 4px 10px;
                font-size: 12px;
                color: #555;
            }}
            
            .quantity-controls {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin: 15px 0;
            }}
            
            .quantity-btn {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: 2px solid #ddd;
                background: white;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .quantity-btn:hover {{
                border-color: #4CAF50;
                color: #4CAF50;
            }}
            
            .quantity-display {{
                font-size: 18px;
                font-weight: bold;
                min-width: 30px;
                text-align: center;
            }}
            
            .action-buttons {{
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }}
            
            .add-to-cart-btn {{
                flex: 1;
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .add-to-cart-btn:hover {{
                background: linear-gradient(45deg, #45a049, #4CAF50);
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(76,175,80,0.4);
            }}
            
            .add-to-cart-btn:disabled {{
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }}
            
            .contact-btn {{
                background: #ff9800;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .contact-btn:hover {{
                background: #e68900;
                transform: translateY(-2px);
            }}
            
            .cook-info {{
                background: rgba(255,245,230,0.8);
                border-radius: 12px;
                padding: 12px;
                margin-top: 15px;
                border-left: 4px solid #ff9800;
            }}
            
            .cook-name {{
                font-weight: bold;
                color: #333;
                margin-bottom: 4px;
            }}
            
            .cook-phone {{
                color: #666;
                font-size: 14px;
            }}
            
            .modal {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                backdrop-filter: blur(5px);
            }}
            
            .modal-content {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                max-width: 400px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            
            .modal-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }}
            
            .modal-close {{
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #999;
            }}
            
            .cart-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }}
            
            .form-group {{
                margin-bottom: 20px;
            }}
            
            .form-label {{
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
                font-size: 14px;
            }}
            
            .form-input {{
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 14px;
                transition: border-color 0.3s;
                box-sizing: border-box;
            }}
            
            .form-input:focus {{
                outline: none;
                border-color: #4CAF50;
            }}
            
            .checkout-btn {{
                width: 100%;
                background: linear-gradient(45deg, #ff6b6b, #ee5a6f);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                margin-top: 20px;
                transition: all 0.3s ease;
            }}
            
            .checkout-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(255,107,107,0.4);
            }}
            
            .checkout-btn:disabled {{
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }}
            
            .back-to-cart-btn {{
                width: 100%;
                background: #6c63ff;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px;
                font-size: 14px;
                cursor: pointer;
                margin-top: 10px;
                transition: all 0.3s ease;
            }}
            
            .back-to-cart-btn:hover {{
                background: #5a52d5;
            }}
            
            .success-message {{
                background: #4CAF50;
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }}
            
            .error-message {{
                background: #ff6b6b;
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }}
            
            @media (max-width: 480px) {{
                .product-header {{
                    flex-direction: column;
                }}
                
                .product-img {{
                    width: 100%;
                    height: 120px;
                }}
                
                .action-buttons {{
                    flex-direction: column;
                }}
            }}
        </style>
    </head>
    <body>
        <div id="app">
            <div class="header">
                <button class="back-btn" @click="goBack">← Назад</button>
                <h2>{{{{ categoryName }}}}</h2>
            </div>
            
            <div class="products-container">
                <div v-if="products.length === 0" style="text-align: center; padding: 40px; color: rgba(255,255,255,0.8);">
                    <h3>🍽️ Пока нет блюд в этой категории</h3>
                    <p>Скоро здесь появятся вкусные предложения!</p>
                    <button class="back-btn" @click="goBack" style="margin-top: 20px;">← Вернуться к категориям</button>
                </div>
                
                <div v-for="p in products" :key="p.id" class="product-card">
                    <div class="product-header">
                        <img :src="p.image" class="product-img" :alt="p.name" />
                        <div class="product-info">
                            <h3 class="product-name">{{{{ p.name }}}}</h3>
                            <p class="product-description">{{{{ p.description }}}}</p>
                            <div class="price">{{{{ p.price }}}} AED</div>
                        </div>
                    </div>
                    
                    <div class="ingredients-section" v-if="p.ingredients && p.ingredients.length">
                        <div class="ingredients-title">🥘 Состав:</div>
                        <ul class="ingredients-list">
                            <li v-for="ing in p.ingredients" :key="ing" class="ingredient-tag">
                                {{{{ ing }}}}
                            </li>
                        </ul>
                    </div>
                    
                    <div class="quantity-controls">
                        <button class="quantity-btn" @click="decreaseQuantity(p.id)">−</button>
                        <span class="quantity-display">{{{{ getQuantity(p.id) }}}}</span>
                        <button class="quantity-btn" @click="increaseQuantity(p.id)">+</button>
                    </div>
                    
                    <div class="action-buttons">
                        <button class="add-to-cart-btn" @click="addToCart(p)" :disabled="getQuantity(p.id) === 0">
                            🛒 Добавить в корзину ({{{{ (p.price * getQuantity(p.id)).toFixed(1) }}}} AED)
                        </button>
                        <button class="contact-btn" @click="contactCook(p)">
                            📞
                        </button>
                    </div>
                    
                    <div class="cook-info">
                        <div class="cook-name">👩‍🍳 {{{{ p.cook_name }}}}</div>
                        <div class="cook-phone">📞 {{{{ p.cook_phone }}}}</div>
                    </div>
                </div>
            </div>
            
            <!-- Корзина -->
            <div v-if="cartTotal > 0" class="cart-summary" @click="showCart = true">
                🛒 {{{{ cartItemsCount }}}} ({{{{ cartTotal.toFixed(1) }}}} AED)
            </div>
            
            <!-- Модальное окно корзины -->
            <div v-if="showCart && !showCheckoutForm" class="modal" @click="showCart = false">
                <div class="modal-content" @click.stop>
                    <div class="modal-header">
                        <h3>🛒 Корзина</h3>
                        <button class="modal-close" @click="showCart = false">&times;</button>
                    </div>
                    
                    <div v-for="item in cartItems" :key="item.id" class="cart-item">
                        <div>
                            <strong>{{{{ item.name }}}}</strong><br>
                            <small>{{{{ item.price }}}} AED × {{{{ item.quantity }}}}</small>
                        </div>
                        <div>
                            <strong>{{{{ (item.price * item.quantity).toFixed(1) }}}} AED</strong>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; font-size: 18px; font-weight: bold;">
                        Итого: {{{{ cartTotal.toFixed(1) }}}} AED
                    </div>
                    
                    <button class="checkout-btn" @click="proceedToCheckout">
                        ✨ Оформить заказ
                    </button>
                </div>
            </div>
            
            <!-- Модальное окно оформления заказа -->
            <div v-if="showCheckoutForm" class="modal" @click="cancelCheckout">
                <div class="modal-content" @click.stop>
                    <div class="modal-header">
                        <h3>📝 Оформление заказа</h3>
                        <button class="modal-close" @click="cancelCheckout">&times;</button>
                    </div>
                    
                    <div v-if="orderSuccess" class="success-message">
                        ✅ Заказ #{{{{ orderSuccess }}}} успешно создан!
                    </div>
                    
                    <div v-if="orderError" class="error-message">
                        ❌ {{{{ orderError }}}}
                    </div>
                    
                    <form @submit.prevent="submitOrder">
                        <div class="form-group">
                            <label class="form-label">👤 Ваше имя *</label>
                            <input 
                                type="text" 
                                class="form-input" 
                                v-model="customerInfo.name"
                                placeholder="Введите ваше имя"
                                required
                            />
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">📱 Телефон *</label>
                            <input 
                                type="tel" 
                                class="form-input" 
                                v-model="customerInfo.phone"
                                placeholder="+971501234567"
                                required
                            />
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">📍 Адрес доставки *</label>
                            <input 
                                type="text" 
                                class="form-input" 
                                v-model="customerInfo.address"
                                placeholder="Район, улица, дом"
                                required
                            />
                        </div>
                        
                        <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                            <strong>Ваш заказ:</strong>
                            <div v-for="item in cartItems" :key="item.id" style="margin-top: 10px;">
                                {{{{ item.name }}}} × {{{{ item.quantity }}}} = {{{{ (item.price * item.quantity).toFixed(1) }}}} AED
                            </div>
                            <div style="margin-top: 10px; font-size: 18px; font-weight: bold; color: #4CAF50;">
                                Итого: {{{{ cartTotal.toFixed(1) }}}} AED
                            </div>
                        </div>
                        
                        <button type="submit" class="checkout-btn" :disabled="isSubmitting">
                            {{{{ isSubmitting ? '⏳ Оформляем...' : '✅ Подтвердить заказ' }}}}
                        </button>
                        
                        <button type="button" class="back-to-cart-btn" @click="backToCart">
                            ← Вернуться в корзину
                        </button>
                    </form>
                </div>
            </div>
        </div>

    <script>
        const {{ createApp, ref, computed, onMounted }} = Vue;
        createApp({{
            setup() {{
                const products = ref([]);
                const quantities = ref({{}});
                const cart = ref([]);
                const showCart = ref(false);
                const showCheckoutForm = ref(false);
                const isSubmitting = ref(false);
                const orderSuccess = ref(null);
                const orderError = ref(null);
                const categoryName = ref('{category_display}');
                
                const customerInfo = ref({{
                    name: '',
                    phone: '',
                    address: ''
                }});

                const cartItems = computed(() => cart.value);
                const cartTotal = computed(() => cart.value.reduce((sum, item) => sum + (item.price * item.quantity), 0));
                const cartItemsCount = computed(() => cart.value.reduce((sum, item) => sum + item.quantity, 0));

                const getQuantity = (productId) => quantities.value[productId] || 0;

                const increaseQuantity = (productId) => {{
                    if (!quantities.value[productId]) quantities.value[productId] = 0;
                    quantities.value[productId]++;
                }};

                const decreaseQuantity = (productId) => {{
                    if (quantities.value[productId] > 0) {{
                        quantities.value[productId]--;
                    }}
                }};

                const addToCart = (product) => {{
                    const quantity = getQuantity(product.id);
                    if (quantity > 0) {{
                        const existingItem = cart.value.find(item => item.id === product.id);
                        if (existingItem) {{
                            existingItem.quantity += quantity;
                        }} else {{
                            cart.value.push({{
                                id: product.id,
                                name: product.name,
                                price: product.price,
                                quantity: quantity,
                                cook_name: product.cook_name,
                                cook_phone: product.cook_phone
                            }});
                        }}
                        quantities.value[product.id] = 0;
                    }}
                }};

                const contactCook = (product) => {{
                    const message = `Здравствуйте! Интересует "${{product.name}}" за ${{product.price}} AED. Можно оформить заказ?`;
                    const whatsappUrl = `https://wa.me/${{product.cook_phone.replace(/[^0-9]/g, '')}}?text=${{encodeURIComponent(message)}}`;
                    window.open(whatsappUrl, '_blank');
                }};

                const proceedToCheckout = () => {{
                    showCart.value = false;
                    showCheckoutForm.value = true;
                    orderSuccess.value = null;
                    orderError.value = null;
                }};

                const backToCart = () => {{
                    showCheckoutForm.value = false;
                    showCart.value = true;
                }};

                const cancelCheckout = () => {{
                    showCheckoutForm.value = false;
                    customerInfo.value = {{ name: '', phone: '', address: '' }};
                    orderSuccess.value = null;
                    orderError.value = null;
                }};

                const submitOrder = async () => {{
                    if (cart.value.length === 0) return;

                    isSubmitting.value = true;
                    orderError.value = null;

                    try {{
                        // Получаем данные пользователя из Telegram WebApp
                        const tg = window.Telegram?.WebApp;
                        const user = tg?.initDataUnsafe?.user;

                        // Подготавливаем данные заказа
                        const orderData = {{
                            customer_name: customerInfo.value.name,
                            customer_phone: customerInfo.value.phone,
                            customer_address: customerInfo.value.address,
                            customer_telegram: user?.username || '',
                            user_telegram_id: user?.id || null,
                            items: cart.value.map(item => ({{
                                product_id: item.id,
                                quantity: item.quantity
                            }})),
                            total_amount: cartTotal.value,
                            status: "pending"
                        }};
                        
                        // Отправляем заказ в API
                        const response = await fetch('/api/orders', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json'
                            }},
                            body: JSON.stringify(orderData)
                        }});
                        
                        if (!response.ok) {{
                            throw new Error('Ошибка при создании заказа');
                        }}
                        
                        const savedOrder = await response.json();
                        
                        // Показываем успешное сообщение
                        orderSuccess.value = savedOrder.id;
                        
                        // Отправляем уведомления в WhatsApp каждому повару
                        const ordersByCook = {{}};
                        cart.value.forEach(item => {{
                            if (!ordersByCook[item.cook_phone]) {{
                                ordersByCook[item.cook_phone] = {{
                                    cook_name: item.cook_name,
                                    cook_phone: item.cook_phone,
                                    items: []
                                }};
                            }}
                            ordersByCook[item.cook_phone].items.push(item);
                        }});

                        Object.values(ordersByCook).forEach(order => {{
                            const orderText = order.items.map(item => 
                                `${{item.name}} x${{item.quantity}} = ${{(item.price * item.quantity).toFixed(1)}} AED`
                            ).join('\\n');
                            
                            const total = order.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
                            const message = `🛒 НОВЫЙ ЗАКАЗ #${{savedOrder.id}}\\n\\n👤 ${{customerInfo.value.name}}\\n📱 ${{customerInfo.value.phone}}\\n📍 ${{customerInfo.value.address}}\\n\\n${{orderText}}\\n\\n💰 Итого: ${{total.toFixed(1)}} AED\\n\\nПожалуйста, подтвердите заказ!`;
                            const whatsappUrl = `https://wa.me/${{order.cook_phone.replace(/[^0-9]/g, '')}}?text=${{encodeURIComponent(message)}}`;
                            window.open(whatsappUrl, '_blank');
                        }});
                        
                        // Очищаем корзину через 2 секунды
                        setTimeout(() => {{
                            cart.value = [];
                            customerInfo.value = {{ name: '', phone: '', address: '' }};
                            showCheckoutForm.value = false;
                            orderSuccess.value = null;
                            alert(`✅ Заказ #${{savedOrder.id}} успешно создан!\\n\\nПовара получили уведомление и свяжутся с вами в WhatsApp.`);
                        }}, 2000);
                        
                    }} catch (error) {{
                        console.error('Ошибка:', error);
                        orderError.value = 'Произошла ошибка при создании заказа. Попробуйте еще раз.';
                    }} finally {{
                        isSubmitting.value = false;
                    }}
                }};

                const goBack = () => {{
                    window.location.href = '/app';
                }};

                const load = async () => {{
                    try {{
                        const res = await fetch('/api/products?category={category}');
                        const data = await res.json();
                        products.value = data;
                        
                        if (data.length === 0) {{
                            console.log('No products found for category: {category}');
                        }}
                    }} catch (error) {{
                        console.error('Ошибка загрузки:', error);
                    }}
                }};

                onMounted(load);

                return {{ 
                    products, 
                    quantities, 
                    cart,
                    showCart,
                    showCheckoutForm,
                    isSubmitting,
                    orderSuccess,
                    orderError,
                    categoryName,
                    customerInfo,
                    cartItems,
                    cartTotal,
                    cartItemsCount,
                    getQuantity,
                    increaseQuantity, 
                    decreaseQuantity,
                    addToCart,
                    contactCook,
                    proceedToCheckout,
                    backToCart,
                    cancelCheckout,
                    submitOrder,
                    goBack
                }};
            }}
        }}).mount('#app');
    </script>
    </body>
    </html>
    """)


@app.get("/api/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    """Получить все продукты или по категории из БД"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if category:
            cursor.execute(
                'SELECT * FROM products WHERE LOWER(category) = LOWER(?)',
                (category,)
            )
        else:
            cursor.execute('SELECT * FROM products')
        
        rows = cursor.fetchall()
        
        products = []
        for row in rows:
            product = dict(row)
            # Парсим JSON ingredients
            if product['ingredients']:
                product['ingredients'] = json.loads(product['ingredients'])
            else:
                product['ingredients'] = []
            products.append(product)
        
        return products


@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Получить конкретный продукт из БД"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product = dict(row)
        if product['ingredients']:
            product['ingredients'] = json.loads(product['ingredients'])
        else:
            product['ingredients'] = []
        
        return product


@app.post("/api/orders", response_model=Order)
async def create_order(order: Order):
    """Создать новый заказ в БД"""
    order_id = str(uuid.uuid4())[:8]  # Короткий ID
    created_at = datetime.now()

    # Вычисляем общую сумму
    total = 0
    with get_db() as conn:
        cursor = conn.cursor()

        for item in order.items:
            cursor.execute('SELECT * FROM products WHERE id = ?', (item.product_id,))
            row = cursor.fetchone()
            if row:
                total += row['price'] * item.quantity

        # Сохраняем заказ
        cursor.execute('''
            INSERT INTO orders (id, customer_name, customer_phone, customer_address,
                               customer_telegram, user_telegram_id, total_amount, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id,
            order.customer_name,
            order.customer_phone,
            order.customer_address,
            order.customer_telegram,
            order.user_telegram_id,
            total,
            order.status,
            created_at.isoformat()
        ))

        # Сохраняем элементы заказа с информацией о продукте и поваре
        for item in order.items:
            cursor.execute('SELECT * FROM products WHERE id = ?', (item.product_id,))
            row = cursor.fetchone()
            if row:
                # Конвертируем Row в dict для безопасного доступа
                row_dict = dict(row)
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, product_name, quantity, price, cook_name, cook_phone, cook_telegram)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order_id,
                    item.product_id,
                    row_dict['name'],
                    item.quantity,
                    row_dict['price'],
                    row_dict.get('cook_name', ''),
                    row_dict.get('cook_phone', ''),
                    row_dict.get('cook_telegram', '')
                ))

        conn.commit()

        # Получаем полный заказ для уведомлений
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
        full_order = dict(cursor.fetchone())

    order.id = order_id
    order.total_amount = total
    order.created_at = created_at.isoformat()

    # 🔥 ОТПРАВЛЯЕМ УВЕДОМЛЕНИЯ!
    import asyncio
    asyncio.create_task(send_telegram_notifications(full_order))

    return order


@app.get("/api/orders")
async def get_orders():
    """Получить все заказы из БД"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.*, 
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' || 
                       oi.quantity || ':' || oi.price || ':' || 
                       oi.cook_name || ':' || oi.cook_phone
                   ) as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        
        orders = []
        for row in rows:
            order = dict(row)
            
            # Парсим items
            items = []
            if order['items_data']:
                for item_str in order['items_data'].split(','):
                    parts = item_str.split(':')
                    items.append({{
                        'product_id': parts[0],
                        'product_name': parts[1],
                        'quantity': int(parts[2]),
                        'price': float(parts[3]),
                        'cook_name': parts[4] if len(parts) > 4 else '',
                        'cook_phone': parts[5] if len(parts) > 5 else ''
                    }})
            
            order['items'] = items
            del order['items_data']
            
            orders.append(order)
        
        return orders


@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """Получить конкретный заказ из БД"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order_row = cursor.fetchone()
        
        if not order_row:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = dict(order_row)
        
        # Получаем items
        cursor.execute('''
            SELECT oi.*, p.name as product_name
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        
        items = [dict(row) for row in cursor.fetchall()]
        order['items'] = items
        
        return order


@app.put("/api/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    """Обновить статус заказа"""
    valid_statuses = ['pending', 'confirmed', 'cooking', 'ready', 'delivered', 'cancelled']

    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {{valid_statuses}}")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")

        conn.commit()

        # Получаем данные заказа для уведомления
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

    if order:
        order_dict = dict(order)
        # 🔥 Отправляем уведомление о смене статуса
        import asyncio
        asyncio.create_task(send_status_update_notification(order_dict))

    return {{"message": "Order status updated", "order_id": order_id, "status": status}}


@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: str):
    """Удалить заказ из БД"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Удаляем items заказа
        cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
        
        # Удаляем сам заказ
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        conn.commit()
    
    return {{"message": "Order deleted", "order_id": order_id}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)