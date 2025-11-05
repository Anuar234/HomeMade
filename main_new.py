"""
FastAPI приложение для HomeMade Food
Переработанная версия с уведомлениями в Telegram
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
from datetime import datetime

from src.config import API_HOST, API_PORT
from src.database import get_db, init_database, add_missing_columns
from src.bot.utils.notifications import send_order_notification_to_admins, send_order_status_to_user

app = FastAPI(title="HomeMade Food Abu Dhabi")

app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS для работы с Telegram Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === MODELS ===
class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    image: str
    cook_telegram: Optional[str] = None
    cook_name: Optional[str] = None
    cook_phone: Optional[str] = None
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


# === SEED DATA ===
def seed_products(conn):
    """Заполнение БД начальными данными"""
    products = [
        {
            "id": "1",
            "name": "Домашние пельмени",
            "description": "Сочные пельмени с говядиной и свининой, как в России",
            "price": 25.0,
            "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300",
            "cook_telegram": "turlubay",
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
            "cook_telegram": "turlubay",
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
            "cook_telegram": "turlubay",
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
            "cook_telegram": "turlubay",
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
            "cook_telegram": "turlubay",
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
            "cook_telegram": "turlubay",
            "cook_name": "Джованни Росси",
            "cook_phone": "+971502222222",
            "category": "pizza",
            "ingredients": '["Тесто", "Томатный соус", "Моцарелла", "Базилик", "Оливковое масло"]'
        }
    ]

    cursor = conn.cursor()
    for product in products:
        cursor.execute('''
            INSERT OR IGNORE INTO products
            (id, name, description, price, image, cook_telegram, cook_name, cook_phone, category, ingredients)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product['id'],
            product['name'],
            product['description'],
            product['price'],
            product['image'],
            product['cook_telegram'],
            product['cook_name'],
            product['cook_phone'],
            product['category'],
            product['ingredients']
        ))
    conn.commit()


# Инициализируем БД при старте
init_database()
add_missing_columns()

with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM products')
    if cursor.fetchone()['count'] == 0:
        seed_products(conn)
        print("✅ БД заполнена тестовыми данными")


# === ROUTES ===
@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница"""
    return HTMLResponse("""
    <html>
    <body style="text-align: center; padding: 50px; font-family: sans-serif;">
        <h1>🍽️ HomeMade Abu Dhabi</h1>
        <p>API работает! Добро пожаловать в сервис домашней еды.</p>
        <div style="margin-top: 30px;">
            <a href="/app" style="background: #0088ff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 10px; display: inline-block;">
                📱 Открыть приложение
            </a>
            <br><br>
            <a href="/api/products" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 10px; display: inline-block;">
                📋 API продуктов
            </a>
        </div>
    </body>
    </html>
    """)


@app.get("/app", response_class=HTMLResponse)
async def get_app():
    """Мини-апп с категориями"""
    # Читаем содержимое из старого main.py (строки 241-410)
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
        # Извлекаем HTML между return HTMLResponse(""" и """)
        start = content.find('return HTMLResponse("""', content.find('@app.get("/app"'))
        end = content.find('""")', start + 24)
        html_content = content[start+24:end]
        return HTMLResponse(html_content)


@app.get("/app/{category}", response_class=HTMLResponse)
async def get_app_category(category: str):
    """Страница категории"""
    # Читаем содержимое из старого main.py
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
        start = content.find('return HTMLResponse(f"""', content.find('@app.get("/app/{category}")'))
        end = content.find('""")', start + 25)
        html_template = content[start+25:end]

    category_names = {
        "burger": "Бургеры",
        "pizza": "Пицца",
        "plov": "Плов",
        "soup": "Супы",
        "pelmeni": "Пельмени",
        "khachapuri": "Хачапури"
    }

    category_display = category_names.get(category.lower(), category.capitalize())
    return HTMLResponse(html_template.replace("{category_display}", category_display).replace("{category}", category))


@app.get("/api/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    """Получить все продукты или по категории"""
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
            if product['ingredients']:
                try:
                    product['ingredients'] = json.loads(product['ingredients'])
                except:
                    product['ingredients'] = []
            else:
                product['ingredients'] = []
            products.append(product)

        return products


@app.post("/api/orders", response_model=Order)
async def create_order(order: Order):
    """Создать новый заказ с уведомлениями"""
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
            INSERT INTO orders
            (id, customer_name, customer_telegram, customer_phone, customer_address,
             user_telegram_id, total_amount, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id,
            order.customer_name,
            order.customer_telegram,
            order.customer_phone,
            order.customer_address,
            order.user_telegram_id,
            total,
            order.status,
            created_at.isoformat()
        ))

        # Сохраняем элементы заказа
        for item in order.items:
            cursor.execute('SELECT * FROM products WHERE id = ?', (item.product_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute('''
                    INSERT INTO order_items
                    (order_id, product_id, product_name, quantity, price, cook_telegram, cook_name, cook_phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order_id,
                    item.product_id,
                    row['name'],
                    item.quantity,
                    row['price'],
                    row['cook_telegram'],
                    row['cook_name'],
                    row['cook_phone']
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

    # Отправляем уведомления асинхронно
    import asyncio
    asyncio.create_task(send_order_notification_to_admins(full_order))

    if order.user_telegram_id:
        asyncio.create_task(send_order_status_to_user(order.user_telegram_id, full_order))

    return order


@app.get("/api/orders")
async def get_orders():
    """Получить все заказы"""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT o.*,
                   GROUP_CONCAT(
                       oi.product_id || ':' || oi.product_name || ':' ||
                       oi.quantity || ':' || oi.price || ':' ||
                       COALESCE(oi.cook_telegram, '') || ':' ||
                       COALESCE(oi.cook_name, '') || ':' ||
                       COALESCE(oi.cook_phone, '')
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
                    if len(parts) >= 4:
                        items.append({
                            'product_id': parts[0],
                            'product_name': parts[1],
                            'quantity': int(parts[2]),
                            'price': float(parts[3]),
                            'cook_telegram': parts[4] if len(parts) > 4 else '',
                            'cook_name': parts[5] if len(parts) > 5 else '',
                            'cook_phone': parts[6] if len(parts) > 6 else ''
                        })

            order['items'] = items
            del order['items_data']

            orders.append(order)

        return orders


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
