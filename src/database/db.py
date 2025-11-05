"""
Модуль для работы с базой данных
"""
import sqlite3
from contextlib import contextmanager
from typing import Optional
from src.config import DATABASE


@contextmanager
def get_db():
    """Контекстный менеджер для работы с БД"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Инициализация базы данных"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customer_name TEXT,
                customer_telegram TEXT,
                customer_address TEXT,
                customer_phone TEXT,
                user_telegram_id INTEGER,
                total_amount REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица позиций заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT,
                product_id TEXT,
                product_name TEXT,
                quantity INTEGER,
                price REAL,
                cook_telegram TEXT,
                cook_name TEXT,
                cook_phone TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        ''')

        # Таблица блюд
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                price REAL,
                image TEXT,
                cook_telegram TEXT,
                cook_name TEXT,
                cook_phone TEXT,
                category TEXT,
                ingredients TEXT
            )
        ''')

        conn.commit()


def add_missing_columns():
    """Добавляет недостающие колонки в существующую БД"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Проверяем и добавляем user_telegram_id в orders
        try:
            cursor.execute("SELECT user_telegram_id FROM orders LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE orders ADD COLUMN user_telegram_id INTEGER")
            print("✅ Добавлена колонка user_telegram_id в таблицу orders")

        # Проверяем и добавляем customer_name в orders
        try:
            cursor.execute("SELECT customer_name FROM orders LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE orders ADD COLUMN customer_name TEXT")
            print("✅ Добавлена колонка customer_name в таблицу orders")

        # Проверяем и добавляем cook_telegram в order_items
        try:
            cursor.execute("SELECT cook_telegram FROM order_items LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE order_items ADD COLUMN cook_telegram TEXT")
            print("✅ Добавлена колонка cook_telegram в таблицу order_items")

        # Проверяем и добавляем cook_telegram в products
        try:
            cursor.execute("SELECT cook_telegram FROM products LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE products ADD COLUMN cook_telegram TEXT")
            print("✅ Добавлена колонка cook_telegram в таблицу products")

        conn.commit()
