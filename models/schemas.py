"""
Pydantic модели для валидации данных
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float = Field(..., gt=0, description="Цена должна быть больше 0")
    image: str
    cook_name: str
    cook_phone: str = Field(..., pattern=r'^\+971\d{9}$', description="Номер телефона в формате +971XXXXXXXXX")
    category: str
    ingredients: Optional[List[str]] = []

    class Config:
        schema_extra = {
            "example": {
                "id": "1",
                "name": "Домашние пельмени",
                "description": "Сочные пельмени с говядиной и свининой",
                "price": 25.0,
                "image": "https://example.com/image.jpg",
                "cook_name": "Анна Петрова",
                "cook_phone": "+971501234567",
                "category": "pelmeni",
                "ingredients": ["Мука", "Яйцо", "Говядина", "Свинина"]
            }
        }

class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0, description="Количество должно быть больше 0")
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": "1",
                "quantity": 2
            }
        }

class Order(BaseModel):
    id: Optional[str] = None
    customer_name: str = Field(..., min_length=2, max_length=100)
    customer_phone: str = Field(..., pattern=r'^\+971\d{9}$')
    customer_address: str = Field(..., min_length=10, max_length=500)
    items: List[OrderItem] = Field(..., min_items=1)
    total_amount: float = Field(default=0.0, ge=0)
    status: str = Field(default="pending")
    created_at: Optional[datetime] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()

    class Config:
        schema_extra = {
            "example": {
                "customer_name": "Иван Иванов",
                "customer_phone": "+971501234567",
                "customer_address": "Abu Dhabi, Marina District, Street 123",
                "items": [
                    {"product_id": "1", "quantity": 2},
                    {"product_id": "2", "quantity": 1}
                ]
            }
        }

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)

class CartResponse(BaseModel):
    items: List[dict]
    total_items: int
    total_amount: float

class APIResponse(BaseModel):
    """Стандартный ответ API"""
    success: bool = True
    message: str = "OK"
    data: Optional[dict] = None