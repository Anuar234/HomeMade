"""
Модели данных для БД
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Product:
    """Модель продукта"""
    id: str
    name: str
    description: str
    price: float
    image: str
    cook_telegram: Optional[str] = None
    cook_name: Optional[str] = None
    cook_phone: Optional[str] = None
    category: Optional[str] = None
    ingredients: Optional[List[str]] = None


@dataclass
class OrderItem:
    """Модель элемента заказа"""
    product_id: str
    product_name: str
    quantity: int
    price: float
    cook_telegram: Optional[str] = None
    cook_name: Optional[str] = None
    cook_phone: Optional[str] = None


@dataclass
class Order:
    """Модель заказа"""
    id: str
    customer_name: Optional[str] = None
    customer_telegram: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    user_telegram_id: Optional[int] = None
    total_amount: float = 0.0
    status: str = "pending"
    created_at: Optional[datetime] = None
    items: Optional[List[OrderItem]] = None
