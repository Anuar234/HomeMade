"""
Pydantic Models for API
"""

from pydantic import BaseModel
from typing import List, Optional


class Product(BaseModel):
    """Product model"""
    id: str
    name: str
    description: str
    price: float
    image: str
    category: str
    ingredients: Optional[List[str]] = []


class OrderItem(BaseModel):
    """Order item model"""
    product_id: str
    quantity: int


class Order(BaseModel):
    """Order model"""
    id: Optional[str] = None
    customer_name: str
    customer_phone: str
    customer_address: str
    customer_telegram: Optional[str] = None
    user_telegram_id: Optional[int] = None
    items: List[OrderItem]
    total_amount: Optional[float] = None
    status: str = "pending"
    created_at: Optional[str] = None
