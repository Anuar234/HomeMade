import sqlite3

# Укажи путь к твоей БД
conn = sqlite3.connect("homefood.db")
cursor = conn.cursor()

# Посмотреть список всех таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Таблицы:", cursor.fetchall())

# Проверить конкретную таблицу (например, orders_info)
cursor.execute("PRAGMA table_info(orders_info);")
columns = cursor.fetchall()

print("\nСтруктура таблицы orders_info:")
for col in columns:
    print(col)
