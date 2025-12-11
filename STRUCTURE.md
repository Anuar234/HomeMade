# 📁 Структура проекта Home Food Abu Dhabi

Проект реорганизован для лучшей читаемости и поддержки. Монолитные файлы разбиты на логические модули.

## 📂 Структура файлов

```
HomeMade/
├── 📁 bot/                    # Telegram Bot модуль
│   ├── __init__.py           # Экспорт create_application
│   ├── config.py             # Конфигурация: BOT_TOKEN, ADMIN_IDS
│   ├── constants.py          # Константы: статусы, категории, эмодзи
│   ├── utils.py              # Утилиты: permissions, formatters, validators
│   └── main.py               # Основной файл бота (импортирует модули)
│
├── 📁 api/                    # FastAPI Application модуль
│   ├── __init__.py           # Экспорт create_app
│   ├── config.py             # Конфигурация FastAPI, CORS, static files
│   ├── models.py             # Pydantic модели: Product, Order, OrderItem
│   └── main.py               # Основной файл API (импортирует модули)
│
├── 📁 database/               # Database модуль
│   └── __init__.py           # DatabaseAdapter, query functions
│
├── 📁 static/                 # Статические файлы (CSS, JS, images)
│
├── 🐍 bot.py                  # ← DEPRECATED: Теперь используйте bot/main.py
├── 🐍 main.py                 # ← DEPRECATED: Теперь используйте api/main.py
├── 🐍 database.py             # ← DEPRECATED: Теперь используйте database/
├── 🐍 start.py                # Entrypoint для Railway (не изменялся)
│
├── requirements.txt
├── Procfile
├── .env
└── README.md
```

## 📦 Модули

### 🤖 bot/ - Telegram Bot

**bot/config.py** (27 строк)
- Загрузка `BOT_TOKEN`, `ADMIN_IDS` из environment
- Определение типа БД (PostgreSQL/SQLite)
- Валидация конфигурации при запуске

**bot/constants.py** (54 строки)
- Conversation states (NAME, DESCRIPTION, PRICE, etc.)
- STATUS_EMOJI - эмодзи для статусов заказов
- STATUS_NAMES - названия статусов на русском
- CATEGORIES - список категорий продуктов
- ERROR_MESSAGES - шаблоны сообщений об ошибках

**bot/utils.py** (145 строк)
- `is_admin()` - проверка прав администратора
- `format_order()` - форматирование заказа для отображения
- `format_stats()` - форматирование статистики
- `validate_product_name()` - валидация названия
- `validate_product_description()` - валидация описания
- `validate_price()` - валидация и парсинг цены
- `validate_image_url()` - валидация URL изображения
- `validate_telegram_username()` - валидация Telegram username

**bot/main.py** (импортирует модули выше)
- Handlers для команд: `/start`, `/help`, `/orders`, `/pending`, `/stats`, `/products`
- ConversationHandler для добавления продуктов
- Callback handlers для inline кнопок
- `create_application()` - фабрика для создания Application

### 🌐 api/ - FastAPI Application

**api/config.py** (34 строки)
- `CachedStaticFiles` - класс для кэширования static files
- `configure_app()` - настройка CORS и middleware

**api/models.py** (38 строк)
- `Product` - Pydantic модель продукта
- `OrderItem` - модель элемента заказа
- `Order` - модель заказа

**api/main.py** (импортирует модули выше)
- HTML routes: `/`, `/app`, `/app/{category}`
- API routes:
  - `GET /api/products` - получить продукты
  - `POST /api/orders` - создать заказ
  - `GET /api/orders` - список заказов
  - `GET /api/orders/{id}` - конкретный заказ
  - `PUT /api/orders/{id}/status` - обновить статус
  - `DELETE /api/orders/{id}` - удалить заказ
- Telegram уведомления (async)

### 💾 database/ - Database Module

**database/__init__.py** (417 строк)
- `DatabaseAdapter` - универсальный адаптер для SQLite/PostgreSQL
- `get_connection()` - context manager для соединений
- `execute_query()` - выполнение SQL запросов
- `init_database()` - инициализация таблиц
- `seed_initial_products()` - заполнение начальными данными
- Query функции: `get_all_products()`, `get_product_by_id()`, `add_product()`, `create_order()`, и т.д.

## 🔄 Миграция со старой структуры

### Старый код (bot.py):
```python
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [...]

def is_admin(update):
    ...

def format_order(order):
    ...
```

### Новый код (bot/main.py):
```python
from .config import BOT_TOKEN, ADMIN_IDS
from .utils import is_admin, format_order
from .constants import STATUS_EMOJI, CATEGORIES
```

## ✅ Преимущества новой структуры

1. **Читаемость** - каждый модуль < 200 строк, легко понять
2. **Maintainability** - изменения в одном месте, не трогают другие
3. **Тестируемость** - каждый модуль можно тестировать отдельно
4. **Scalability** - легко добавлять новые функции
5. **Onboarding** - новые разработчики быстрее разбираются
6. **Code Reuse** - утилиты используются в разных частях

## 🚀 Как запустить

### Локально (разработка):
```bash
python start.py
```

### Railway (production):
Procfile уже настроен:
```
web: python start.py
```

## 📝 Следующие шаги (Future Improvements)

- [ ] Разделить `api/main.py` на routes/products.py и routes/orders.py
- [ ] Разделить `bot/main.py` на handlers/commands.py и handlers/products.py
- [ ] Создать api/notifications/ для Telegram уведомлений
- [ ] Добавить тесты (pytest) для каждого модуля
- [ ] Создать database/queries.py для SQL запросов
- [ ] Добавить logging module

## 🤝 Contributing

При добавлении нового функционала:
1. Определите, к какому модулю он относится
2. Если модуль слишком большой (>300 строк), разделите его
3. Обновите этот файл STRUCTURE.md
4. Добавьте docstrings для новых функций
