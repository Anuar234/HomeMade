#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для массового добавления продуктов в базу данных
"""

import sys
import io

# Установим UTF-8 кодировку для stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import add_product

# Список всех продуктов для добавления
products = [
    # ПЕЛЬМЕНИ (pelmeni)
    {
        "name": "Манты замороженные",
        "description": "Сочные манты с мясной начинкой, готовятся на пару",
        "price": 120.0,
        "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Мясо", "Лук", "Тесто", "Специи"]'
    },
    {
        "name": "Вареники с грибами и картошкой",
        "description": "Домашние вареники с грибами и картофелем",
        "price": 100.0,
        "image": "https://images.unsplash.com/photo-1626200419199-391ae4be7a41?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Картофель", "Грибы", "Лук", "Тесто"]'
    },
    {
        "name": "Вареники с картошкой",
        "description": "Классические вареники с картофельной начинкой",
        "price": 90.0,
        "image": "https://images.unsplash.com/photo-1626200419199-391ae4be7a41?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Картофель", "Лук", "Тесто"]'
    },
    {
        "name": "Вареники с жареным луком и картошкой",
        "description": "Вареники с картошкой и ароматным жареным луком",
        "price": 100.0,
        "image": "https://images.unsplash.com/photo-1626200419199-391ae4be7a41?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Картофель", "Лук жареный", "Тесто"]'
    },
    {
        "name": "Вареники с творогом и вишней",
        "description": "Сладкие вареники с творогом и вишней",
        "price": 100.0,
        "image": "https://images.unsplash.com/photo-1571064247530-4146bc1a081b?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Творог", "Вишня", "Тесто", "Сахар"]'
    },
    {
        "name": "Вареники с творогом",
        "description": "Классические вареники с творожной начинкой",
        "price": 90.0,
        "image": "https://images.unsplash.com/photo-1571064247530-4146bc1a081b?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Творог", "Тесто", "Сахар"]'
    },
    {
        "name": "Пельмени г/к микс говядина и курица",
        "description": "Пельмени с мясной начинкой из говядины и курицы",
        "price": 85.0,
        "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Говядина", "Курица", "Лук", "Тесто"]'
    },
    {
        "name": "Пельмени с говядиной",
        "description": "Классические пельмени с говяжьей начинкой",
        "price": 85.0,
        "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Говядина", "Лук", "Тесто", "Специи"]'
    },
    {
        "name": "Пельмени с курицей",
        "description": "Пельмени с куриной начинкой",
        "price": 80.0,
        "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Курица", "Лук", "Тесто", "Специи"]'
    },
    {
        "name": "Манты с тыквой (с мясом)",
        "description": "Манты с мясом стейк, луком и тыквой",
        "price": 120.0,
        "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Мясо стейк", "Тыква", "Лук", "Тесто", "Специи"]'
    },
    {
        "name": "Пельмени из шпината",
        "description": "Пельмени с тестом из шпината",
        "price": 100.0,
        "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Шпинат", "Мясо", "Лук", "Тесто"]'
    },
    {
        "name": "Манты с тыквой",
        "description": "Манты с тыквенной начинкой",
        "price": 80.0,
        "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Тыква", "Лук", "Тесто", "Специи"]'
    },
    {
        "name": "Кюрзе",
        "description": "Традиционные дагестанские кюрзе",
        "price": 80.0,
        "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Мясо", "Лук", "Тесто", "Специи"]'
    },
    {
        "name": "Голубцы замороженные",
        "description": "Голубцы с мясной начинкой в капустных листьях",
        "price": 120.0,
        "image": "https://images.unsplash.com/photo-1544025162-d76694265947?w=300&q=80",
        "category": "pelmeni",
        "ingredients": '["Капуста", "Мясо", "Рис", "Томатный соус"]'
    },

    # ХАЧАПУРИ И ВЫПЕЧКА (khachapuri)
    {
        "name": "Самса",
        "description": "Узбекская самса с мясной начинкой",
        "price": 120.0,
        "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Мясо", "Лук", "Слоеное тесто", "Специи"]'
    },
    {
        "name": "Мясной пирог с картошкой",
        "description": "Домашний пирог с мясом и картофелем, 700г",
        "price": 90.0,
        "image": "https://images.unsplash.com/photo-1619040484735-e7730e09d0b5?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Мясо", "Картофель", "Тесто", "Лук"]'
    },
    {
        "name": "Пирожки с мясом замороженные",
        "description": "Пирожки с мясной начинкой для духовки",
        "price": 85.0,
        "image": "https://images.unsplash.com/photo-1619040484735-e7730e09d0b5?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Мясо", "Лук", "Тесто"]'
    },
    {
        "name": "Сосиски в тесте мини",
        "description": "Мини сосиски в тесте, 20 штук",
        "price": 80.0,
        "image": "https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Сосиски", "Тесто"]'
    },
    {
        "name": "Сосиски в тесте замороженные",
        "description": "Сосиски в тесте, 10 штук",
        "price": 80.0,
        "image": "https://images.unsplash.com/photo-1621939514649-280e2ee25f60?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Сосиски", "Тесто"]'
    },
    {
        "name": "Блинчики с мясом жареные",
        "description": "Жареные блинчики с мясной начинкой",
        "price": 85.0,
        "image": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Мясо", "Блины", "Лук"]'
    },
    {
        "name": "Блинчики с творогом жареные",
        "description": "Жареные блинчики с творожной начинкой",
        "price": 85.0,
        "image": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Творог", "Блины", "Сахар"]'
    },
    {
        "name": "Мини пиццы",
        "description": "Мини пиццы ассорти, 10 штук",
        "price": 80.0,
        "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Тесто", "Сыр", "Томатный соус", "Начинки"]'
    },
    {
        "name": "Блинчики с яйцом и луком",
        "description": "Блинчики с яично-луковой начинкой",
        "price": 70.0,
        "image": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Яйцо", "Лук", "Блины"]'
    },
    {
        "name": "Блинчики с ветчиной и сыром",
        "description": "Блинчики с ветчиной и сыром",
        "price": 80.0,
        "image": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Ветчина", "Сыр", "Блины"]'
    },
    {
        "name": "Блины",
        "description": "Обычные блины, 15 штук",
        "price": 50.0,
        "image": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300&q=80",
        "category": "khachapuri",
        "ingredients": '["Мука", "Яйцо", "Молоко", "Сахар"]'
    },

    # ПЛОВ И ОСНОВНЫЕ БЛЮДА (plov)
    {
        "name": "Курица под рисом",
        "description": "Курица под рисом, 1.5-1.8 кг",
        "price": 200.0,
        "image": "https://images.unsplash.com/photo-1596040033229-a0b3b7f5c777?w=300&q=80",
        "category": "plov",
        "ingredients": '["Курица", "Рис", "Морковь", "Лук", "Специи"]'
    },
    {
        "name": "Куриные котлеты",
        "description": "Куриные котлеты, 10 штук (1 кг)",
        "price": 100.0,
        "image": "https://images.unsplash.com/photo-1619740455993-9e08c7e5e1e7?w=300&q=80",
        "category": "plov",
        "ingredients": '["Курица", "Лук", "Специи", "Хлеб"]'
    },
    {
        "name": "Котлеты из мяса",
        "description": "Котлеты из мяса (говядина, лук, специи), 10 штук (1 кг)",
        "price": 120.0,
        "image": "https://images.unsplash.com/photo-1619740455993-9e08c7e5e1e7?w=300&q=80",
        "category": "plov",
        "ingredients": '["Мясо", "Лук", "Соль", "Черный перец"]'
    },
    {
        "name": "Люля из говядины",
        "description": "Люля-кебаб из говядины, 12 штук (1 кг)",
        "price": 120.0,
        "image": "https://images.unsplash.com/photo-1529042410759-befb1204b468?w=300&q=80",
        "category": "plov",
        "ingredients": '["Говядина", "Лук", "Специи"]'
    },
    {
        "name": "Узбекский плов",
        "description": "Настоящий узбекский плов с мясом, 2 кг",
        "price": 250.0,
        "image": "https://images.unsplash.com/photo-1596040033229-a0b3b7f5c777?w=300&q=80",
        "category": "plov",
        "ingredients": '["Рис", "Баранина", "Морковь", "Лук", "Специи"]'
    },

    # СУПЫ (soup)
    {
        "name": "Фрикадельки из говядины для супа",
        "description": "Фрикадельки из говядины для приготовления супа, 500г",
        "price": 60.0,
        "image": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=300&q=80",
        "category": "soup",
        "ingredients": '["Говядина", "Лук", "Специи"]'
    },

    # ДЕСЕРТЫ (dessert)
    {
        "name": "Булочки сладкие сдобные",
        "description": "Сладкие сдобные булочки, 10 штук",
        "price": 80.0,
        "image": "https://images.unsplash.com/photo-1586444248902-2f64eddc13df?w=300&q=80",
        "category": "dessert",
        "ingredients": '["Мука", "Сахар", "Яйцо", "Молоко", "Дрожжи"]'
    },
    {
        "name": "Сырное печенье",
        "description": "Сырное печенье, 30 штук",
        "price": 80.0,
        "image": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=300&q=80",
        "category": "dessert",
        "ingredients": '["Сыр", "Мука", "Масло", "Яйцо"]'
    },
    {
        "name": "Сырники",
        "description": "Сырники из творога, 10 штук",
        "price": 60.0,
        "image": "https://images.unsplash.com/photo-1625938145043-21545e3d639f?w=300&q=80",
        "category": "dessert",
        "ingredients": '["Творог", "Мука", "Яйцо", "Сахар"]'
    },

    # ЗАКУСКИ И САЛАТЫ (salad)
    {
        "name": "Мимоза с тунцом",
        "description": "Салат Мимоза с тунцом, 1 кг",
        "price": 100.0,
        "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=300&q=80",
        "category": "salad",
        "ingredients": '["Тунец", "Картофель", "Морковь", "Яйцо", "Майонез"]'
    },
    {
        "name": "Паштет из куриной печени",
        "description": "Домашний паштет из куриной печени, 400г",
        "price": 60.0,
        "image": "https://images.unsplash.com/photo-1625938145312-32a1e355c3e9?w=300&q=80",
        "category": "salad",
        "ingredients": '["Куриная печень", "Лук", "Морковь", "Масло", "Специи"]'
    },
    {
        "name": "Капуста квашеная 500г",
        "description": "Квашеная капуста домашнего приготовления, 500г",
        "price": 30.0,
        "image": "https://images.unsplash.com/photo-1623428187969-5da2dcea5ebf?w=300&q=80",
        "category": "salad",
        "ingredients": '["Капуста", "Морковь", "Соль"]'
    },
    {
        "name": "Капуста квашеная 1кг",
        "description": "Квашеная капуста домашнего приготовления, 1 кг",
        "price": 60.0,
        "image": "https://images.unsplash.com/photo-1623428187969-5da2dcea5ebf?w=300&q=80",
        "category": "salad",
        "ingredients": '["Капуста", "Морковь", "Соль"]'
    },
]

def main():
    """Добавляем все продукты в базу данных"""
    print("=" * 60)
    print("Добавление продуктов в базу данных...")
    print("=" * 60)

    success_count = 0
    error_count = 0

    for i, product in enumerate(products, 1):
        try:
            product_id = add_product(**product)
            print(f"✅ [{i}/{len(products)}] {product['name']} (ID: {product_id})")
            success_count += 1
        except Exception as e:
            print(f"❌ [{i}/{len(products)}] {product['name']} - Ошибка: {e}")
            error_count += 1

    print("=" * 60)
    print(f"Завершено! Успешно: {success_count}, Ошибок: {error_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
