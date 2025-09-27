"""
HTML шаблон страницы категории
"""

def get_category_app_template(category: str, category_display: str) -> str:
    """Возвращает HTML шаблон страницы категории"""
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{category_display} - Home Food Abu Dhabi</title>
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
            
            .empty-state {{
                text-align: center;
                padding: 40px;
                color: rgba(255,255,255,0.8);
            }}
            
            .empty-state h3 {{
                margin-bottom: 16px;
                font-size: 24px;
            }}
            
            .empty-state p {{
                margin-bottom: 24px;
                font-size: 16px;
                opacity: 0.8;
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
                <div v-if="products.length === 0" class="empty-state">
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
            <div v-if="showCart" class="modal" @click="showCart = false">
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
                    
                    <button class="checkout-btn" @click="checkout">
                        ✨ Оформить заказ
                    </button>
                </div>
            </div>
        </div>

    <script>
        const {{{{ createApp, ref, computed, onMounted }}}} = Vue;
        createApp({{{{
            setup() {{{{
                const products = ref([]);
                const quantities = ref({{}});
                const cart = ref([]);
                const showCart = ref(false);
                const categoryName = ref('{category_display}');

                const cartItems = computed(() => cart.value);
                const cartTotal = computed(() => cart.value.reduce((sum, item) => sum + (item.price * item.quantity), 0));
                const cartItemsCount = computed(() => cart.value.reduce((sum, item) => sum + item.quantity, 0));

                const getQuantity = (productId) => quantities.value[productId] || 0;

                const increaseQuantity = (productId) => {{{{
                    if (!quantities.value[productId]) quantities.value[productId] = 0;
                    quantities.value[productId]++;
                }}}};

                const decreaseQuantity = (productId) => {{{{
                    if (quantities.value[productId] > 0) {{{{
                        quantities.value[productId]--;
                    }}}}
                }}}};

                const addToCart = (product) => {{{{
                    const quantity = getQuantity(product.id);
                    if (quantity > 0) {{{{
                        const existingItem = cart.value.find(item => item.id === product.id);
                        if (existingItem) {{{{
                            existingItem.quantity += quantity;
                        }}}} else {{{{
                            cart.value.push({{{{
                                id: product.id,
                                name: product.name,
                                price: product.price,
                                quantity: quantity,
                                cook_name: product.cook_name,
                                cook_phone: product.cook_phone
                            }}}});
                        }}}}
                        quantities.value[product.id] = 0;
                    }}}}
                }}}};

                const contactCook = (product) => {{{{
                    const message = `Здравствуйте! Интересует "${{product.name}}" за ${{product.price}} AED. Можно оформить заказ?`;
                    const whatsappUrl = `https://wa.me/${{product.cook_phone.replace(/[^0-9]/g, '')}}?text=${{encodeURIComponent(message)}}`;
                    window.open(whatsappUrl, '_blank');
                }}}};

                const checkout = () => {{{{
                    if (cart.value.length === 0) return;
                    
                    // Группировка по поварам
                    const ordersByCook = {{}};
                    cart.value.forEach(item => {{{{
                        if (!ordersByCook[item.cook_phone]) {{{{
                            ordersByCook[item.cook_phone] = {{{{
                                cook_name: item.cook_name,
                                cook_phone: item.cook_phone,
                                items: []
                            }}}};
                        }}}}
                        ordersByCook[item.cook_phone].items.push(item);
                    }}}});

                    // Отправка заказов каждому повару
                    Object.values(ordersByCook).forEach(order => {{{{
                        const orderText = order.items.map(item => 
                            `${{item.name}} x${{item.quantity}} = ${{(item.price * item.quantity).toFixed(1)}} AED`
                        ).join('\\n');
                        
                        const total = order.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
                        const message = `🛒 ЗАКАЗ\\n\\n${{orderText}}\\n\\n💰 Итого: ${{total.toFixed(1)}} AED\\n\\nПожалуйста, подтвердите заказ!`;
                        const whatsappUrl = `https://wa.me/${{order.cook_phone.replace(/[^0-9]/g, '')}}?text=${{encodeURIComponent(message)}}`;
                        window.open(whatsappUrl, '_blank');
                    }}}});

                    // Очистка корзины
                    cart.value = [];
                    showCart.value = false;
                    alert('Заказ отправлен! Повара свяжутся с вами в WhatsApp.');
                }}}};

                const goBack = () => {{{{
                    window.location.href = '/app';
                }}}};

                const load = async () => {{{{
                    try {{{{
                        const res = await fetch('/api/products?category={category}');
                        const data = await res.json();
                        products.value = data;
                        
                        if (data.length === 0) {{{{
                            console.log('No products found for category: {category}');
                        }}}}
                    }}}} catch (error) {{{{
                        console.error('Ошибка загрузки:', error);
                    }}}}
                }}}};

                onMounted(load);

                return {{{{ 
                    products, 
                    quantities, 
                    cart,
                    showCart,
                    categoryName,
                    cartItems,
                    cartTotal,
                    cartItemsCount,
                    getQuantity,
                    increaseQuantity, 
                    decreaseQuantity,
                    addToCart,
                    contactCook,
                    checkout,
                    goBack
                }}}};
            }}}}
        }}}}).mount('#app');
    </script>
    </body>
    </html>
    """