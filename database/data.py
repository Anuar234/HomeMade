"""
Управление данными продуктов и заказов
"""
from typing import List, Optional, Dict, Any
from models.schemas import Product, Order
import uuid

class DataManager:
    """Менеджер для работы с данными"""
    
    def __init__(self):
        self.products_db = self._init_products()
        self.orders_db = []
        self.cart_db = {}  # session_id -> {product_id: quantity}
    
    def _init_products(self) -> List[Dict[str, Any]]:
        """Инициализация продуктов"""
        return [
            {
                "id": "1",
                "name": "Домашние пельмени",
                "description": "Сочные пельмени с говядиной и свининой, как в России",
                "price": 25.0,
                "image": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300",
                "cook_name": "Анна Петрова",
                "cook_phone": "+971501234567",
                "category": "pelmeni",
                "ingredients": ["Мука", "Яйцо", "Говядина", "Свинина", "Лук", "Соль", "Перец"]
            },
            {
                "id": "2", 
                "name": "Узбекский плов",
                "description": "Настоящий узбекский плов с бараниной и специями",
                "price": 30.0,
                "image": "https://images.unsplash.com/photo-1596040033229-a0b3b7f5c777?w=300",
                "cook_name": "Фарход Алиев",
                "cook_phone": "+971507654321",
                "category": "plov",
                "ingredients": ["Рис", "Баранина", "Морковь", "Лук", "Чеснок", "Зира", "Масло"]
            },
            {
                "id": "3",
                "name": "Домашний борщ",
                "description": "Украинский борщ с говядиной и сметаной",
                "price": 18.0,
                "image": "https://images.unsplash.com/photo-1571064247530-4146bc1a081b?w=300",
                "cook_name": "Оксана Коваль",
                "cook_phone": "+971509876543",
                "category": "soup",
                "ingredients": ["Свекла", "Говядина", "Капуста", "Картофель", "Морковь", "Лук", "Сметана"]
            },
            {
                "id": "4",
                "name": "Хачапури по-аджарски",
                "description": "Грузинский хачапури с сыром и яйцом",
                "price": 22.0,
                "image": "https://images.unsplash.com/photo-1627662235973-4d265e175fc1?w=300",
                "cook_name": "Нино Джавахишвили",
                "cook_phone": "+971508765432",
                "category": "khachapuri",
                "ingredients": ["Мука", "Сыр", "Яйцо", "Молоко", "Масло"]
            },
            {
                "id": "5",
                "name": "Домашний бургер",
                "description": "Сочный бургер с говяжьей котлетой и свежими овощами",
                "price": 35.0,
                "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300",
                "cook_name": "Михаил Сидоров",
                "cook_phone": "+971501111111",
                "category": "burger",
                "ingredients": ["Булочка", "Говядина", "Сыр", "Салат", "Помидор", "Лук", "Соус"]
            },
            {
                "id": "6",
                "name": "Пицца Маргарита",
                "description": "Классическая итальянская пицца с моцареллой и базиликом",
                "price": 28.0,
                "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300",
                "cook_name": "Джованни Росси",
                "cook_phone": "+971502222222",
                "category": "pizza",
                "ingredients": ["Тесто", "Томатный соус", "Моцарелла", "Базилик", "Оливковое масло"]
            }
        ]
    
    # Методы для работы с продуктами
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Получить все продукты"""
        return self.products_db
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Получить продукты по категории"""
        return [p for p in self.products_db if p["category"].lower() == category.lower()]
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Получить продукт по ID"""
        return next((p for p in self.products_db if p["id"] == product_id), None)
    
    def add_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Добавить новый продукт"""
        if not product.get("id"):
            product["id"] = str(uuid.uuid4())
        self.products_db.append(product)
        return product
    
    def update_product(self, product_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить продукт"""
        product = self.get_product_by_id(product_id)
        if product:
            product.update(updates)
            return product
        return None
    
    def delete_product(self, product_id: str) -> bool:
        """Удалить продукт"""
        self.products_db = [p for p in self.products_db if p["id"] != product_id]
        return True
    
    # Методы для работы с заказами
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать заказ"""
        if not order_data.get("id"):
            order_data["id"] = str(uuid.uuid4())
        
        # Подсчет общей суммы
        total = 0
        for item in order_data.get("items", []):
            product = self.get_product_by_id(item["product_id"])
            if product:
                total += product["price"] * item["quantity"]
        
        order_data["total_amount"] = total
        self.orders_db.append(order_data)
        return order_data
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Получить все заказы"""
        return self.orders_db
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Получить заказ по ID"""
        return next((o for o in self.orders_db if o["id"] == order_id), None)
    
    def update_order(self, order_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить заказ"""
        order = self.get_order_by_id(order_id)
        if order:
            order.update(updates)
            return order
        return None
    
    # Методы для работы с корзиной
    def add_to_cart(self, session_id: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
        """Добавить в корзину"""
        if session_id not in self.cart_db:
            self.cart_db[session_id] = {}
        
        if product_id not in self.cart_db[session_id]:
            self.cart_db[session_id][product_id] = 0
        
        self.cart_db[session_id][product_id] += quantity
        return {"message": "Added to cart", "cart": self.cart_db[session_id]}
    
    def get_cart(self, session_id: str) -> List[Dict[str, Any]]:
        """Получить содержимое корзины"""
        cart_items = []
        if session_id in self.cart_db:
            for product_id, quantity in self.cart_db[session_id].items():
                product = self.get_product_by_id(product_id)
                if product:
                    cart_items.append({
                        **product,
                        "quantity": quantity
                    })
        return cart_items
    
    def clear_cart(self, session_id: str) -> Dict[str, str]:
        """Очистить корзину"""
        if session_id in self.cart_db:
            del self.cart_db[session_id]
        return {"message": "Cart cleared"}
    
    def update_cart_item(self, session_id: str, product_id: str, quantity: int) -> Dict[str, Any]:
        """Обновить количество товара в корзине"""
        if session_id in self.cart_db and product_id in self.cart_db[session_id]:
            if quantity <= 0:
                del self.cart_db[session_id][product_id]
            else:
                self.cart_db[session_id][product_id] = quantity
        return {"message": "Cart updated", "cart": self.cart_db.get(session_id, {})}

# Создаем глобальный экземпляр менеджера данных
data_manager = DataManager()