"""
Вспомогательные функции
"""
from typing import Dict, Any, List
import re
import uuid
from datetime import datetime

def generate_unique_id() -> str:
    """Генерация уникального ID"""
    return str(uuid.uuid4())

def validate_phone_number(phone: str) -> bool:
    """Валидация номера телефона UAE"""
    pattern = r'^\+971\d{9}$'
    return re.match(pattern, phone) is not None

def format_phone_number(phone: str) -> str:
    """Форматирование номера телефона"""
    # Удаляем все символы кроме цифр и +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Если номер начинается с 971, добавляем +
    if cleaned.startswith('971') and len(cleaned) == 12:
        return '+' + cleaned
    
    # Если номер начинается с 0, заменяем на +971
    if cleaned.startswith('0') and len(cleaned) == 10:
        return '+971' + cleaned[1:]
    
    return cleaned

def calculate_total_amount(items: List[Dict[str, Any]], products: List[Dict[str, Any]]) -> float:
    """Подсчет общей суммы заказа"""
    total = 0.0
    products_dict = {p['id']: p for p in products}
    
    for item in items:
        product = products_dict.get(item['product_id'])
        if product:
            total += product['price'] * item['quantity']
    
    return round(total, 2)

def get_category_display_name(category: str) -> str:
    """Получить отображаемое название категории"""
    category_names = {
        "burger": "Бургеры",
        "pizza": "Пицца", 
        "plov": "Плов",
        "soup": "Супы",
        "pelmeni": "Пельмени",
        "khachapuri": "Хачапури",
        "samsa": "Самса",
        "shashlik": "Шашлык",
        "dessert": "Десерты",
        "drink": "Напитки"
    }
    return category_names.get(category.lower(), category.capitalize())

def sanitize_string(text: str, max_length: int = None) -> str:
    """Очистка и валидация строки"""
    if not text:
        return ""
    
    # Удаляем лишние пробелы
    text = text.strip()
    
    # Ограничиваем длину
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

def format_currency(amount: float, currency: str = "AED") -> str:
    """Форматирование валюты"""
    return f"{amount:.2f} {currency}"

def create_whatsapp_message(order_items: List[Dict], cook_name: str = None) -> str:
    """Создание сообщения для WhatsApp заказа"""
    message_parts = ["🛒 ЗАКАЗ"]
    
    if cook_name:
        message_parts.append(f"Повар: {cook_name}")
    
    message_parts.append("")
    
    total = 0
    for item in order_items:
        line_total = item['price'] * item['quantity']
        total += line_total
        message_parts.append(f"{item['name']} x{item['quantity']} = {line_total:.1f} AED")
    
    message_parts.extend([
        "",
        f"💰 Итого: {total:.1f} AED",
        "",
        "Пожалуйста, подтвердите заказ!"
    ])
    
    return "\n".join(message_parts)

def get_whatsapp_url(phone: str, message: str) -> str:
    """Создание URL для WhatsApp"""
    # Очищаем номер телефона
    clean_phone = re.sub(r'[^\d]', '', phone)
    if clean_phone.startswith('971'):
        clean_phone = clean_phone
    else:
        clean_phone = '971' + clean_phone.lstrip('0')
    
    from urllib.parse import quote
    return f"https://wa.me/{clean_phone}?text={quote(message)}"

def paginate_results(items: List[Any], page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """Пагинация результатов"""
    if page < 1:
        page = 1
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_items = items[start_idx:end_idx]
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    return {
        "items": paginated_items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

def search_products(products: List[Dict], query: str) -> List[Dict]:
    """Поиск продуктов по запросу"""
    if not query:
        return products
    
    query_lower = query.lower()
    results = []
    
    for product in products:
        # Поиск в названии
        if query_lower in product.get('name', '').lower():
            results.append(product)
            continue
        
        # Поиск в описании
        if query_lower in product.get('description', '').lower():
            results.append(product)
            continue
        
        # Поиск в ингредиентах
        ingredients = product.get('ingredients', [])
        if any(query_lower in ingredient.lower() for ingredient in ingredients):
            results.append(product)
            continue
        
        # Поиск по имени повара
        if query_lower in product.get('cook_name', '').lower():
            results.append(product)
            continue
    
    return results

def validate_order_data(order_data: Dict[str, Any]) -> List[str]:
    """Валидация данных заказа"""
    errors = []
    
    # Проверка обязательных полей
    required_fields = ['customer_name', 'customer_phone', 'customer_address', 'items']
    for field in required_fields:
        if not order_data.get(field):
            errors.append(f"Поле '{field}' обязательно для заполнения")
    
    # Валидация телефона
    if order_data.get('customer_phone'):
        if not validate_phone_number(order_data['customer_phone']):
            errors.append("Неверный формат номера телефона")
    
    # Валидация товаров
    items = order_data.get('items', [])
    if not items:
        errors.append("В заказе должен быть хотя бы один товар")
    else:
        for i, item in enumerate(items):
            if not item.get('product_id'):
                errors.append(f"Товар {i+1}: отсутствует product_id")
            if not isinstance(item.get('quantity'), int) or item.get('quantity', 0) <= 0:
                errors.append(f"Товар {i+1}: количество должно быть положительным числом")
    
    return errors

def generate_session_id() -> str:
    """Генерация ID сессии"""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

def is_valid_category(category: str) -> bool:
    """Проверка валидности категории"""
    valid_categories = [
        "burger", "pizza", "plov", "soup", "pelmeni", "khachapuri",
        "samsa", "shashlik", "dessert", "drink", "salad", "side"
    ]
    return category.lower() in valid_categories