#!/usr/bin/env python3
"""
Скрипт для обновления структуры шаблонов
"""
import os
import shutil

def update_templates():
    """Обновляет структуру шаблонов"""
    
    print("🔄 Обновление структуры шаблонов...")
    
    # Создаем папку templates если её нет
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("✅ Создана папка templates/")
    
    # Удаляем старые Python файлы с шаблонами
    old_files = [
        'templates/main_app.py',
        'templates/category_app.py'
    ]
    
    for file_path in old_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Удален {file_path}")
    
    # Создаем новый __init__.py для templates
    init_content = '''# templates/__init__.py
"""
HTML шаблоны приложения
"""
'''
    
    with open('templates/__init__.py', 'w', encoding='utf-8') as f:
        f.write(init_content)
    print("✅ Обновлен templates/__init__.py")
    
    print("\n📋 Следующие шаги:")
    print("1. Установите Jinja2: pip install jinja2")
    print("2. Создайте HTML файлы из артефактов выше:")
    print("   - templates/index.html")
    print("   - templates/main_app.html") 
    print("   - templates/category_app.html")
    print("3. Замените содержимое main.py")
    print("4. Обновите requirements.txt")
    print("5. Запустите: uvicorn main:app --reload")
    
    print("\n✨ Готово! Шаблоны разделены на отдельные HTML файлы.")

if __name__ == "__main__":
    update_templates()