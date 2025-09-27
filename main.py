"""
Главный файл приложения Home Food Abu Dhabi
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Импорты конфигурации и компонентов
from config import settings
from api.products import router as products_router
from api.orders import router as orders_router  
from api.cart import router as cart_router
from templates.main_app import get_main_app_template, get_root_page_template
from templates.category_app import get_category_app_template
from utils.helpers import get_category_display_name

# Создание приложения FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API для сервиса домашней еды в Абу-Даби"
)

# Подключение статических файлов
try:
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
except RuntimeError:
    # Если папка static не существует, создаем заглушку
    import os
    if not os.path.exists(settings.STATIC_DIR):
        os.makedirs(settings.STATIC_DIR)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Настройка CORS для Telegram Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Подключение роутеров API
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(cart_router)

# Основные маршруты приложения
@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с информацией об API"""
    return HTMLResponse(get_root_page_template())

@app.get("/app", response_class=HTMLResponse)
async def get_app():
    """Главная страница приложения с категориями"""
    return HTMLResponse(get_main_app_template())

@app.get("/app/{category}", response_class=HTMLResponse)
async def get_app_category(category: str):
    """Страница категории товаров"""
    try:
        category_display = get_category_display_name(category)
        template = get_category_app_template(category, category_display)
        return HTMLResponse(template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке страницы: {str(e)}")

# Дополнительные маршруты для информации
@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION
    }

@app.get("/info")
async def app_info():
    """Информация о приложении"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "Сервис домашней еды в Абу-Даби",
        "features": [
            "Каталог домашних блюд",
            "Заказ через WhatsApp",
            "Корзина покупок",
            "Фильтрация по категориям",
            "Поиск блюд",
            "Информация о поварах"
        ],
        "categories": [
            "Бургеры", "Пицца", "Плов", "Супы", 
            "Пельмени", "Хачапури", "Десерты", "Напитки"
        ]
    }

# Обработка ошибок
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Обработчик ошибки 404"""
    return HTMLResponse(
        content="""
        <html>
        <body style="text-align: center; padding: 50px; font-family: sans-serif;">
            <h1>🍽️ Страница не найдена</h1>
            <p>Извините, запрашиваемая страница не существует.</p>
            <a href="/app" style="background: #0088ff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px;">
                🏠 Вернуться на главную
            </a>
        </body>
        </html>
        """,
        status_code=404
    )

@app.exception_handler(500)
async def server_error_handler(request, exc):
    """Обработчик ошибки 500"""
    return HTMLResponse(
        content="""
        <html>
        <body style="text-align: center; padding: 50px; font-family: sans-serif;">
            <h1>🍽️ Ошибка сервера</h1>
            <p>Произошла внутренняя ошибка сервера. Пожалуйста, попробуйте позже.</p>
            <a href="/app" style="background: #0088ff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px;">
                🏠 Вернуться на главную
            </a>
        </body>
        </html>
        """,
        status_code=500
    )

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.HOST, 
        port=settings.PORT,
        reload=settings.DEBUG
    )