"""
API endpoints для продуктов
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models.schemas import Product, APIResponse
from database.data import data_manager

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/", response_model=List[Product])
async def get_products(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Лимит результатов"),
    offset: Optional[int] = Query(0, ge=0, description="Смещение для пагинации")
):
    """
    Получить список продуктов с возможностью фильтрации и поиска
    """
    try:
        if category:
            products = data_manager.get_products_by_category(category)
        else:
            products = data_manager.get_all_products()
        
        # Поиск по названию и описанию
        if search:
            search_lower = search.lower()
            products = [
                p for p in products 
                if search_lower in p["name"].lower() or search_lower in p["description"].lower()
            ]
        
        # Пагинация
        if offset:
            products = products[offset:]
        if limit:
            products = products[:limit]
        
        return products
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении продуктов: {str(e)}")

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """
    Получить конкретный продукт по ID
    """
    try:
        product = data_manager.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        return product
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении продукта: {str(e)}")

@router.post("/", response_model=Product)
async def create_product(product: Product):
    """
    Создать новый продукт (только для администраторов)
    """
    try:
        # Проверяем, что продукт с таким ID не существует
        existing = data_manager.get_product_by_id(product.id)
        if existing:
            raise HTTPException(status_code=400, detail="Продукт с таким ID уже существует")
        
        created_product = data_manager.add_product(product.dict())
        return created_product
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании продукта: {str(e)}")

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: str, updates: dict):
    """
    Обновить продукт (только для администраторов)
    """
    try:
        updated_product = data_manager.update_product(product_id, updates)
        if not updated_product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        return updated_product
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении продукта: {str(e)}")

@router.delete("/{product_id}", response_model=APIResponse)
async def delete_product(product_id: str):
    """
    Удалить продукт (только для администраторов)
    """
    try:
        product = data_manager.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        
        data_manager.delete_product(product_id)
        return APIResponse(message="Продукт успешно удален")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении продукта: {str(e)}")

@router.get("/categories/list")
async def get_categories():
    """
    Получить список всех категорий
    """
    try:
        products = data_manager.get_all_products()
        categories = list(set(p["category"] for p in products))
        
        # Маппинг категорий с их отображаемыми названиями
        category_mapping = {
            "burger": {"name": "burger", "label": "Бургеры", "icon": "/static/stickers_animations/burger.json"},
            "pizza": {"name": "pizza", "label": "Пицца", "icon": "/static/stickers_animations/pizza.json"},
            "plov": {"name": "plov", "label": "Плов", "icon": "/static/stickers_animations/cake.json"},
            "soup": {"name": "soup", "label": "Супы", "icon": "/static/stickers_animations/cookie.json"},
            "pelmeni": {"name": "pelmeni", "label": "Пельмени", "icon": "/static/stickers_animations/pie.json"},
            "khachapuri": {"name": "khachapuri", "label": "Хачапури", "icon": "/static/stickers_animations/donut.json"},
        }
        
        result = []
        for cat in categories:
            if cat in category_mapping:
                result.append(category_mapping[cat])
            else:
                result.append({
                    "name": cat,
                    "label": cat.capitalize(),
                    "icon": "/static/stickers_animations/burger.json"  # дефолтная иконка
                })
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении категорий: {str(e)}")

@router.get("/stats/summary")
async def get_products_stats():
    """
    Получить статистику по продуктам
    """
    try:
        products = data_manager.get_all_products()
        
        # Группировка по категориям
        categories_stats = {}
        total_products = len(products)
        
        for product in products:
            category = product["category"]
            if category not in categories_stats:
                categories_stats[category] = {
                    "count": 0,
                    "avg_price": 0,
                    "min_price": float('inf'),
                    "max_price": 0
                }
            
            stats = categories_stats[category]
            stats["count"] += 1
            stats["min_price"] = min(stats["min_price"], product["price"])
            stats["max_price"] = max(stats["max_price"], product["price"])
        
        # Подсчет средней цены
        for category, stats in categories_stats.items():
            category_products = [p for p in products if p["category"] == category]
            stats["avg_price"] = sum(p["price"] for p in category_products) / len(category_products)
        
        return {
            "total_products": total_products,
            "categories_count": len(categories_stats),
            "categories_stats": categories_stats,
            "overall_avg_price": sum(p["price"] for p in products) / total_products if total_products > 0 else 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении статистики: {str(e)}")