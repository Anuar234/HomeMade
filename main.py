from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
import os
from datetime import datetime

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

# Модели данных
class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    image: str
    cook_name: str
    cook_phone: str
    category: str

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    id: Optional[str] = None
    customer_name: str
    customer_phone: str
    customer_address: str
    items: List[OrderItem]
    total_amount: float
    status: str = "pending"
    created_at: Optional[datetime] = None

# Временное хранилище
products_db = [
    {
        "id": "1",
        "name": "Домашние пельмени",
        "description": "Сочные пельмени с говядиной и свининой, как в России",
        "price": 25.0,
        "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300",
        "cook_name": "Анна Петрова",
        "cook_phone": "+971501234567",
        "category": "Основные блюда"
    },
    {
        "id": "2", 
        "name": "Узбекский плов",
        "description": "Настоящий узбекский плов с бараниной и специями",
        "price": 30.0,
        "image": "https://images.unsplash.com/photo-1596040033229-a0b3b7f5c777?w=300",
        "cook_name": "Фарход Алиев",
        "cook_phone": "+971507654321",
        "category": "Основные блюда"
    },
    {
        "id": "3",
        "name": "Домашний борщ",
        "description": "Украинский борщ с говядиной и сметаной",
        "price": 18.0,
        "image": "https://images.unsplash.com/photo-1571064247530-4146bc1a081b?w=300",
        "cook_name": "Оксана Коваль",
        "cook_phone": "+971509876543",
        "category": "Супы"
    },
    {
        "id": "4",
        "name": "Хачапури по-аджарски",
        "description": "Грузинский хачапури с сыром и яйцом",
        "price": 22.0,
        "image": "https://images.unsplash.com/photo-1627662235973-4d265e175fc1?w=300",
        "cook_name": "Нино Джавахишвили",
        "cook_phone": "+971508765432",
        "category": "Выпечка"
    }
]

orders_db = []

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
        <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
        <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
        <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
        padding: 12px;
        background: #f8f9fa;
        margin: 0;
    }

    .header {
        text-align: center;
        margin-bottom: 16px;
    }

    .search-input {
        width: 100%;
        padding: 10px 14px;
        border-radius: 10px;
        border: 1px solid #ddd;
        font-size: 16px;
        margin-bottom: 20px;
    }

    .icons-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr); /* 2 колонки для мобилы */
        gap: 16px;
        justify-items: center;
    }

    .icon-card {
        background: white;
        border-radius: 14px;
        padding: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        max-width: 150px; /* ограничение чтобы карточки не были слишком большими */
        transition: transform 0.2s;
    }

    .icon-card:hover {
        transform: scale(1.03);
    }

    .icon-card lottie-player {
        width: 100px;
        height: 100px;
    }

    .category-btn {
        margin-top: 10px;
        padding: 10px 14px;
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-size: 15px;
        font-weight: 600;
        width: 100%;
        transition: background 0.2s, transform 0.1s;
    }

    .category-btn:hover {
        background: #45a049;
        transform: translateY(-2px);
    }

    /* 🔥 Адаптив для совсем маленьких экранов */
    @media (max-width: 400px) {
        .icon-card {
            max-width: 130px;
            padding: 12px;
        }

        .icon-card lottie-player {
            width: 80px;
            height: 80px;
        }

        .category-btn {
            font-size: 14px;
            padding: 8px 12px;
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
            Перейти
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
                    { name: "burger", icon: "/static/stickers_animations/burger.json" },
                    { name: "pizza", icon: "/static/stickers_animations/pizza.json" },
                    { name: "plov", icon: "/static/stickers_animations/cake.json" },
                    { name: "soup", icon: "/static/stickers_animations/cookie.json" },
                    { name: "samsa", icon: "/static/stickers_animations/pie.json" },
                    { name: "shashlik", icon: "/static/stickers_animations/donut.json" },
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
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{{{ category }}}} - Home Food Abu Dhabi</title>
        <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
        <style>
            body {{ font-family: sans-serif; padding: 16px; background: #f8f9fa; }}
            .product-card {{ background:white; border-radius:12px; padding:16px; margin-bottom:16px; box-shadow:0 2px 12px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <div id="app">
            <h2>Категория: {category}</h2>
            <div v-for="p in products" :key="p.id" class="product-card">
                <h3>{{{{ p.name }}}}</h3>
                <p>{{{{ p.description }}}}</p>
                <strong>{{{{ p.price }}}} AED</strong>
            </div>
        </div>

        <script>
        const {{ createApp, ref, onMounted }} = Vue;
        createApp({{
            setup() {{
                const products = ref([]);
                const load = async () => {{
                    const res = await fetch('/api/products/{category}');
                    products.value = await res.json();
                }};
                onMounted(load);
                return {{ products }};
            }}
        }}).mount('#app');
        </script>
    </body>
    </html>
    """)



@app.get("/api/products", response_model=List[Product])
async def get_products():
    """Получить все продукты"""
    return products_db


@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Получить конкретный продукт"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/api/orders", response_model=Order)
async def create_order(order: Order):
    """Создать новый заказ"""
    order.id = str(uuid.uuid4())
    order.created_at = datetime.now()
    
    total = 0
    for item in order.items:
        product = next((p for p in products_db if p["id"] == item.product_id), None)
        if product:
            total += product["price"] * item.quantity
    
    order.total_amount = total
    
    order_dict = order.dict()
    order_dict["created_at"] = order.created_at.isoformat()
    orders_db.append(order_dict)
    
    return order

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)