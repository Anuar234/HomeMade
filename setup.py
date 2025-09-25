#!/usr/bin/env python3
"""
Скрипт для быстрой настройки Home Food Abu Dhabi app
"""

import os

# HTML содержимое (вставьте ваш HTML код сюда)
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home Food Abu Dhabi</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <!-- Вставьте ваши стили и JS код сюда -->
</head>
<body>
    <div id="app">
        <div class="app">
            <h1>🍽️ Home Food Abu Dhabi</h1>
            <p>Если вы видите это - фронтенд подключен!</p>
        </div>
    </div>
</body>
</html>'''

def setup():
    """Создает необходимые файлы и папки"""
    
    # Создаем папку static
    if not os.path.exists('static'):
        os.makedirs('static')
        print("✅ Создана папка static/")
    
    # Создаем index.html
    with open('static/index.html', 'w', encoding='utf-8') as f:
        f.write(HTML_CONTENT)
    print("✅ Создан static/index.html")
    
    print("\n🚀 Готово! Теперь:")
    print("1. Замените содержимое static/index.html на полный HTML код")
    print("2. Запустите: uvicorn main:app --reload")
    print("3. Откройте: http://localhost:8000/app")

if __name__ == "__main__":
    setup()