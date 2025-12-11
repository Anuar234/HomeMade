"""
Database adapter for Home Food Abu Dhabi
Supports SQLite (local development) and PostgreSQL (Railway production)
"""

import os
import sqlite3
from typing import Optional, Any
from contextlib import contextmanager

# Определяем тип базы данных
DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    print("Using PostgreSQL database")
else:
    print("Using SQLite database")


class DatabaseAdapter:
    """Универсальный адаптер базы данных"""

    def __init__(self, db_path: str = "homefood.db"):
        self.db_path = db_path
        self.use_postgres = USE_POSTGRES
        self.database_url = DATABASE_URL

        # Инициализируем таблицы при создании
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Получить соединение с базой данных"""
        if self.use_postgres:
            # PostgreSQL connection
            conn = psycopg2.connect(self.database_url)
            try:
                yield conn
            finally:
                conn.close()
        else:
            # SQLite connection
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()

    def execute_query(self, query: str, params: tuple = (), fetch: str = None):
        """
        Выполнить SQL запрос
        fetch: None (no fetch), 'one', 'all'
        """
        with self.get_connection() as conn:
            if self.use_postgres:
                from psycopg2.extras import RealDictCursor
                cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = conn.cursor()

            cursor.execute(query, params)

            if fetch == 'one':
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch == 'all':
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return cursor.lastrowid if not self.use_postgres else cursor.rowcount

    def init_database(self):
        """Инициализировать таблицы базы данных"""
        print("Initializing database tables...")

        # Таблица продуктов (с поддержкой обеих схем: main.py и bot.py)
        if self.use_postgres:
            products_table = """
            CREATE TABLE IF NOT EXISTS products (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                image VARCHAR(500),
                category VARCHAR(100),
                ingredients TEXT,
                cook_telegram VARCHAR(100),
                cook_name VARCHAR(255),
                cook_phone VARCHAR(50)
            )
            """
        else:
            products_table = """
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image TEXT,
                category TEXT,
                ingredients TEXT,
                cook_telegram TEXT,
                cook_name TEXT,
                cook_phone TEXT
            )
            """

        # Таблица заказов
        if self.use_postgres:
            orders_table = """
            CREATE TABLE IF NOT EXISTS orders (
                id VARCHAR(50) PRIMARY KEY,
                customer_name VARCHAR(255) NOT NULL,
                customer_phone VARCHAR(50) NOT NULL,
                customer_address TEXT,
                customer_telegram VARCHAR(100),
                user_telegram_id BIGINT,
                total_amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:
            orders_table = """
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                customer_address TEXT,
                customer_telegram TEXT,
                user_telegram_id INTEGER,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

        # Таблица элементов заказа
        if self.use_postgres:
            order_items_table = """
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id VARCHAR(50) NOT NULL,
                product_id VARCHAR(50) NOT NULL,
                product_name VARCHAR(255),
                quantity INTEGER NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                cook_name VARCHAR(255),
                cook_phone VARCHAR(50),
                cook_telegram VARCHAR(100),
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
            """
        else:
            order_items_table = """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                cook_name TEXT,
                cook_phone TEXT,
                cook_telegram TEXT,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
            """

        # Таблица модерации
        if self.use_postgres:
            moderation_table = """
            CREATE TABLE IF NOT EXISTS activity_moderation (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                action_type VARCHAR(100) NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(50)
            )
            """
        else:
            moderation_table = """
            CREATE TABLE IF NOT EXISTS activity_moderation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                action_type TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT
            )
            """

        # Создаем таблицы
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(products_table)
            cursor.execute(orders_table)
            cursor.execute(order_items_table)
            cursor.execute(moderation_table)
            conn.commit()

        print("Database tables initialized successfully")

        # Проверяем, есть ли продукты, если нет - добавляем стартовые
        self.seed_initial_products()

    def get_placeholder(self, index: int = 1) -> str:
        """Получить placeholder для параметров (? для SQLite, %s для PostgreSQL)"""
        if self.use_postgres:
            return "%s"
        else:
            return "?"

    def get_returning_clause(self) -> str:
        """Получить RETURNING clause для получения ID (только PostgreSQL)"""
        if self.use_postgres:
            return "RETURNING id"
        else:
            return ""

    def seed_initial_products(self):
        """Заполнить базу начальными продуктами если пусто"""
        try:
            # Проверяем количество продуктов
            count_query = "SELECT COUNT(*) as count FROM products"
            result = self.execute_query(count_query, fetch='one')

            if result and result['count'] == 0:
                print("📦 Database is empty, adding initial products...")

                products = [
                    ("1", "Домашние пельмени", "Сочные пельмени с говядиной и свининой, как в России", 25.0,
                     "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=150&q=80&fm=webp&fit=crop",
                     "pelmeni", '["Мука", "Яйцо", "Говядина", "Свинина", "Лук"]', "", "Анна Петрова", "+971501234567"),

                    ("2", "Узбекский плов", "Настоящий узбекский плов с бараниной и специями", 30.0,
                     "https://images.unsplash.com/photo-1596040033229-a0b3b7f5c777?w=150&q=80&fm=webp&fit=crop",
                     "plov", '["Рис", "Баранина", "Морковь", "Лук", "Чеснок"]', "", "Фарход Алиев", "+971507654321"),

                    ("3", "Домашний борщ", "Украинский борщ с говядиной и сметаной", 18.0,
                     "https://images.unsplash.com/photo-1571064247530-4146bc1a081b?w=150&q=80&fm=webp&fit=crop",
                     "soup", '["Свекла", "Говядина", "Капуста", "Картофель"]', "", "Оксана Коваль", "+971509876543"),

                    ("4", "Хачапури по-аджарски", "Грузинский хачапури с сыром и яйцом", 22.0,
                     "https://images.unsplash.com/photo-1627662235973-4d265e175fc1?w=150&q=80&fm=webp&fit=crop",
                     "khachapuri", '["Мука", "Сыр", "Яйцо", "Молоко"]', "", "Нино Джавахишвили", "+971508765432"),

                    ("5", "Домашний бургер", "Сочный бургер с говяжьей котлетой и свежими овощами", 35.0,
                     "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=150&q=80&fm=webp&fit=crop",
                     "burger", '["Булочка", "Говядина", "Сыр", "Салат", "Помидор"]', "", "Михаил Сидоров", "+971501111111"),

                    ("6", "Пицца Маргарита", "Классическая итальянская пицца с моцареллой и базиликом", 28.0,
                     "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=150&q=80&fm=webp&fit=crop",
                     "pizza", '["Тесто", "Томатный соус", "Моцарелла", "Базилик"]', "", "Джованни Росси", "+971502222222"),
                ]

                placeholder = self.get_placeholder()
                insert_query = f"""
                INSERT INTO products (id, name, description, price, image, category, ingredients, cook_telegram, cook_name, cook_phone)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """

                for product in products:
                    self.execute_query(insert_query, product)
                    print(f"  ✅ Added: {product[1]} ({product[5]})")

                print(f"✅ Added {len(products)} initial products to database")
            else:
                print(f"✓ Database already has {result['count']} products")

        except Exception as e:
            print(f"⚠️ Error seeding initial products: {e}")
            import traceback
            traceback.print_exc()


# Создаем глобальный экземпляр адаптера
db = DatabaseAdapter()


# Удобные функции для работы с базой данных
def get_all_products():
    """Получить все продукты"""
    return db.execute_query("SELECT * FROM products ORDER BY id", fetch='all')


def get_product_by_id(product_id: int):
    """Получить продукт по ID"""
    placeholder = db.get_placeholder()
    query = f"SELECT * FROM products WHERE id = {placeholder}"
    return db.execute_query(query, (product_id,), fetch='one')


def get_products_by_category(category: str):
    """Получить продукты по категории"""
    placeholder = db.get_placeholder()
    query = f"SELECT * FROM products WHERE category = {placeholder} ORDER BY id"
    return db.execute_query(query, (category,), fetch='all')


def add_product(name: str, description: str, price: float, image: str,
                category: str, ingredients: str, cook_telegram: str = "",
                cook_name: str = "", cook_phone: str = ""):
    """Добавить новый продукт"""
    import uuid

    # Генерируем короткий уникальный ID
    product_id = str(uuid.uuid4())[:8]

    placeholder = db.get_placeholder()

    # Формируем query
    query = f"""
    INSERT INTO products (id, name, description, price, image, category, ingredients, cook_telegram, cook_name, cook_phone)
    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """

    # Собираем все параметры в tuple
    params = (
        product_id,
        name,
        description,
        price,
        image,
        category,
        ingredients,
        cook_telegram,
        cook_name,
        cook_phone
    )

    # Выполняем запрос
    db.execute_query(query, params)

    # Логирование для отладки
    print(f"✅ Product added to DB: ID={product_id}, Name={name}, Category={category}")

    return product_id


def delete_product(product_id: int):
    """Удалить продукт"""
    placeholder = db.get_placeholder()
    query = f"DELETE FROM products WHERE id = {placeholder}"
    return db.execute_query(query, (product_id,))


def create_order(user_id: str, user_name: str, user_phone: str, items: str,
                 total: float, delivery_address: str, payment_method: str):
    """Создать новый заказ"""
    placeholder = db.get_placeholder()

    if db.use_postgres:
        query = f"""
        INSERT INTO orders (user_id, user_name, user_phone, items, total, delivery_address, payment_method, status)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, 'pending')
        RETURNING id
        """
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id, user_name, user_phone, items, total, delivery_address, payment_method))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
    else:
        query = f"""
        INSERT INTO orders (user_id, user_name, user_phone, items, total, delivery_address, payment_method, status)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, 'pending')
        """
        return db.execute_query(query, (user_id, user_name, user_phone, items, total, delivery_address, payment_method))


def get_all_orders():
    """Получить все заказы"""
    return db.execute_query("SELECT * FROM orders ORDER BY created_at DESC", fetch='all')


def get_order_by_id(order_id: int):
    """Получить заказ по ID"""
    placeholder = db.get_placeholder()
    query = f"SELECT * FROM orders WHERE id = {placeholder}"
    return db.execute_query(query, (order_id,), fetch='one')


def update_order_status(order_id: int, status: str):
    """Обновить статус заказа"""
    placeholder = db.get_placeholder()
    query = f"UPDATE orders SET status = {placeholder} WHERE id = {placeholder}"
    return db.execute_query(query, (status, order_id))


def log_activity(user_id: str, username: str, first_name: str, last_name: str,
                 action_type: str, details: str, ip_address: str = None):
    """Логировать активность пользователя"""
    placeholder = db.get_placeholder()
    query = f"""
    INSERT INTO activity_moderation (user_id, username, first_name, last_name, action_type, details, ip_address)
    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """
    return db.execute_query(query, (user_id, username, first_name, last_name, action_type, details, ip_address))


def get_all_activity():
    """Получить всю активность"""
    return db.execute_query("SELECT * FROM activity_moderation ORDER BY timestamp DESC", fetch='all')
