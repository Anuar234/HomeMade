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

app = FastAPI(title="Home Food Abu Dhabi")

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
    """Возвращает фронтенд приложение"""
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
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                padding: 16px; 
                background: #f8f9fa;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .search-bar {
                margin-bottom: 20px;
            }
            .search-input {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
            }
            .products-grid {
                display: grid;
                gap: 16px;
            }
            .product-card { 
                background: white; 
                border-radius: 12px; 
                padding: 16px; 
                box-shadow: 0 2px 12px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .product-card:hover {
                transform: translateY(-2px);
            }
            .product-image { 
                width: 100%; 
                height: 200px; 
                border-radius: 8px; 
                object-fit: cover; 
                margin-bottom: 12px; 
            }
            .product-name {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            .product-description {
                color: #666;
                margin-bottom: 12px;
                line-height: 1.4;
            }
            .product-cook {
                color: #888;
                font-size: 14px;
                margin-bottom: 12px;
            }
            .product-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .price { 
                font-size: 20px; 
                font-weight: 700; 
                color: #0088ff; 
            }
            .buy-button { 
                background: #0088ff; 
                color: white; 
                border: none; 
                padding: 10px 20px; 
                border-radius: 8px; 
                cursor: pointer; 
                font-weight: 600;
                transition: all 0.2s;
            }
            .buy-button:hover {
                background: #0066cc;
                transform: scale(1.05);
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            .modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                padding: 20px;
            }
            .modal-content {
                background: white;
                border-radius: 12px;
                padding: 24px;
                max-width: 400px;
                width: 100%;
            }
            .form-group {
                margin-bottom: 16px;
            }
            .form-label {
                display: block;
                margin-bottom: 6px;
                font-weight: 600;
            }
            .form-input {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
            }
            .modal-buttons {
                display: flex;
                gap: 12px;
                margin-top: 20px;
            }
            .btn {
                flex: 1;
                padding: 12px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
            }
            .btn-cancel {
                background: #f5f5f5;
                border: 1px solid #ddd;
            }
            .btn-confirm {
                background: #0088ff;
                color: white;
                border: none;
            }
        </style>
    </head>
    <body>
        <div id="app">
            <div class="header">
                <h1>🍽️ Home Food Abu Dhabi</h1>
                <p>Домашняя еда от местных поваров</p>
            </div>
            
            <div class="search-bar">
                <input 
                    v-model="searchQuery"
                    type="text" 
                    class="search-input" 
                    placeholder="🔍 Поиск блюд..."
                >
            </div>
            
            <div v-if="loading" class="loading">
                Загрузка продуктов...
            </div>
            
            <div v-else class="products-grid">
                <div 
                    v-for="product in filteredProducts" 
                    :key="product.id"
                    class="product-card"
                >
                    <lottie-player
                src="static/stickers_animations/burger.json"
                background="transparent"
                speed="1"
                style="width: 120px; height: 120px; margin: 10px auto;"
                loop
                autoplay>
            </lottie-player>
                    <div class="product-name">{{ product.name }}</div>
                    <div class="product-description">{{ product.description }}</div>
                    <div class="product-cook">👨‍🍳 {{ product.cook_name }}</div>
                    <div class="product-footer">
                        <span class="price">{{ product.price }} AED</span>
                        <button class="buy-button" @click="openOrderModal(product)">
                            Заказать
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Модальное окно -->
            <div v-if="showModal" class="modal" @click.self="closeModal">
                <div class="modal-content">
                    <h3 style="margin-bottom: 20px;">Оформить заказ</h3>
                    
                    <div class="form-group">
                        <label class="form-label">Блюдо:</label>
                        <div>{{ selectedProduct?.name }} - {{ selectedProduct?.price }} AED</div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Ваше имя:</label>
                        <input v-model="orderForm.name" type="text" class="form-input" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Телефон:</label>
                        <input v-model="orderForm.phone" type="tel" class="form-input" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Адрес:</label>
                        <input v-model="orderForm.address" type="text" class="form-input" required>
                    </div>
                    
                    <div class="modal-buttons">
                        <button class="btn btn-cancel" @click="closeModal">Отмена</button>
                        <button class="btn btn-confirm" @click="submitOrder">Заказать</button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const { createApp, ref, computed, onMounted } = Vue;
            
            createApp({
                setup() {
                    const products = ref([]);
                    const loading = ref(true);
                    const searchQuery = ref('');
                    const showModal = ref(false);
                    const selectedProduct = ref(null);
                    const orderForm = ref({
                        name: '',
                        phone: '',
                        address: ''
                    });
                    
                    const filteredProducts = computed(() => {
                        if (!searchQuery.value) return products.value;
                        return products.value.filter(product => 
                            product.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                            product.description.toLowerCase().includes(searchQuery.value.toLowerCase())
                        );
                    });
                    
                    const loadProducts = async () => {
                        try {
                            const response = await fetch('/api/products');
                            if (response.ok) {
                                products.value = await response.json();
                            }
                        } catch (error) {
                            console.error('Error loading products:', error);
                        } finally {
                            loading.value = false;
                        }
                    };
                    
                    const openOrderModal = (product) => {
                        selectedProduct.value = product;
                        showModal.value = true;
                    };
                    
                    const closeModal = () => {
                        showModal.value = false;
                        selectedProduct.value = null;
                        orderForm.value = { name: '', phone: '', address: '' };
                    };
                    
                    const submitOrder = async () => {
                        if (!orderForm.value.name || !orderForm.value.phone || !orderForm.value.address) {
                            alert('Пожалуйста, заполните все поля');
                            return;
                        }
                        
                        try {
                            const orderData = {
                                customer_name: orderForm.value.name,
                                customer_phone: orderForm.value.phone,
                                customer_address: orderForm.value.address,
                                items: [{
                                    product_id: selectedProduct.value.id,
                                    quantity: 1
                                }],
                                total_amount: selectedProduct.value.price
                            };
                            
                            const response = await fetch('/api/orders', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify(orderData)
                            });
                            
                            if (response.ok) {
                                alert('Заказ успешно оформлен! Мы с вами свяжемся.');
                                closeModal();
                            }
                        } catch (error) {
                            console.error('Error submitting order:', error);
                            alert('Ошибка при оформлении заказа');
                        }
                    };
                    
                    onMounted(() => {
                        loadProducts();
                    });
                    
                    return {
                        products,
                        loading,
                        searchQuery,
                        filteredProducts,
                        showModal,
                        selectedProduct,
                        orderForm,
                        openOrderModal,
                        closeModal,
                        submitOrder
                    };
                }
            }).mount('#app');
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