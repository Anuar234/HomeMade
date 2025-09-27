"""
HTML шаблон главной страницы приложения
"""
from fastapi.responses import HTMLResponse

def get_main_app_template() -> str:
    """Возвращает HTML шаблон главной страницы"""
    return """
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
                        {{cat.label}}
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
    """

def get_root_page_template() -> str:
    """Возвращает HTML шаблон корневой страницы"""
    return """
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
            <a href="/docs" style="background: #17a2b8; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 10px; display: inline-block;">
                📖 Документация API
            </a>
        </div>
    </body>
    </html>
    """