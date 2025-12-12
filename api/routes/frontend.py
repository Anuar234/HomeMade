"""
Frontend HTML route handlers
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
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


@router.get("/app", response_class=HTMLResponse)
async def get_app():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Home Food Abu Dhabi</title>

        <!-- Preconnect для быстрой загрузки -->
        <link rel="preconnect" href="https://telegram.org">
        <link rel="preconnect" href="https://unpkg.com">

        <!-- Скрипты для работы приложения -->
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
        <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
        <style>
    * {
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        padding: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: 0;
        min-height: 100vh;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Плавная прокрутка */
    html {
        scroll-behavior: smooth;
    }

    /* Аппаратное ускорение для анимаций */
    .icon-card, .category-btn {
        will-change: transform;
        transform: translateZ(0);
        backface-visibility: hidden;
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
            loop
            autoplay>
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


@router.get("/app/{category}")
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

        <!-- Preconnect для быстрой загрузки -->
        <link rel="preconnect" href="https://telegram.org">
        <link rel="preconnect" href="https://unpkg.com">
        <link rel="preconnect" href="https://images.unsplash.com">
        <link rel="dns-prefetch" href="https://images.unsplash.com">

        <!-- Скрипты для работы приложения -->
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                padding: 0;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }}

            /* Плавная прокрутка */
            html {{
                scroll-behavior: smooth;
            }}

            /* Аппаратное ускорение для анимаций */
            .product-card, .add-to-cart-btn, .cart-summary {{
                will-change: transform;
                transform: translateZ(0);
                backface-visibility: hidden;
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
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
            }}

            @keyframes loading {{
                0% {{ background-position: 200% 0; }}
                100% {{ background-position: -200% 0; }}
            }}

            .product-img[src] {{
                animation: none;
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
                        <img :src="p.image" class="product-img" :alt="p.name" loading="lazy" />
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
                            <label class="form-label">📍 Адрес доставки *</label>
                            <input
                                type="text"
                                class="form-input"
                                v-model="customerInfo.address"
                                placeholder="Район, улица, дом"
                                required
                            />
                        </div>

                        <div style="background: #e3f2fd; padding: 12px; border-radius: 8px; margin-bottom: 15px; font-size: 14px;">
                            <strong>📱 Ваш Telegram:</strong> @{{{{ user?.username || 'не указан' }}}}
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
                    customerInfo.value = {{ address: '' }};
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
                            customer_name: user?.first_name || user?.username || 'Клиент',
                            customer_phone: 'Telegram: @' + (user?.username || user?.id),
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
                            customerInfo.value = {{ address: '' }};
                            showCheckoutForm.value = false;
                            orderSuccess.value = null;
                            alert(`✅ Заказ #${{savedOrder.id}} успешно создан!\\n\\nМы получили ваш заказ и скоро свяжемся с вами в Telegram.`);
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
