"""
API endpoints для корзины
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from models.schemas import CartItem, CartResponse, APIResponse
from database.data import data_manager
import uuid

router = APIRouter(prefix="/api/cart", tags=["cart"])

def get_session_id(x_session_id: Optional[str] = Header(None)) -> str:
    """
    Получить или создать session ID для корзины
    """
    if not x_session_id:
        return str(uuid.uuid4())
    return x_session_id

@router.post("/add", response_model=APIResponse)
async def add_to_cart(
    item: CartItem,
    session_id: str = Depends(get_session_id)
):
    """
    Добавить товар в корзину
    """
    try:
        # Проверяем, что продукт существует
        product = data_manager.get_product_by_id(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        
        result = data_manager.add_to_cart(session_id, item.product_id, item.quantity)
        
        return APIResponse(
            message="Товар добавлен в корзину",
            data={"session_id": session_id, **result}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении в корзину: {str(e)}")

@router.get("/", response_model=CartResponse)
async def get_cart(session_id: str = Depends(get_session_id)):
    """
    Получить содержимое корзины
    """
    try:
        cart_items = data_manager.get_cart(session_id)
        
        total_items = sum(item["quantity"] for item in cart_items)
        total_amount = sum(item["price"] * item["quantity"] for item in cart_items)
        
        return CartResponse(
            items=cart_items,
            total_items=total_items,
            total_amount=total_amount
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении корзины: {str(e)}")

@router.put("/update", response_model=APIResponse)
async def update_cart_item(
    item: CartItem,
    session_id: str = Depends(get_session_id)
):
    """
    Обновить количество товара в корзине
    """
    try:
        # Проверяем, что продукт существует
        product = data_manager.get_product_by_id(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        
        result = data_manager.update_cart_item(session_id, item.product_id, item.quantity)
        
        return APIResponse(
            message="Корзина обновлена",
            data=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении корзины: {str(e)}")

@router.delete("/remove/{product_id}", response_model=APIResponse)
async def remove_from_cart(
    product_id: str,
    session_id: str = Depends(get_session_id)
):
    """
    Удалить товар из корзины
    """
    try:
        result = data_manager.update_cart_item(session_id, product_id, 0)
        
        return APIResponse(
            message="Товар удален из корзины",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении из корзины: {str(e)}")

@router.delete("/clear", response_model=APIResponse)
async def clear_cart(session_id: str = Depends(get_session_id)):
    """
    Очистить корзину
    """
    try:
        result = data_manager.clear_cart(session_id)
        return APIResponse(message="Корзина очищена", data=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при очистке корзины: {str(e)}")

@router.get("/count", response_model=dict)
async def get_cart_count(session_id: str = Depends(get_session_id)):
    """
    Получить количество товаров в корзине
    """
    try:
        cart_items = data_manager.get_cart(session_id)
        total_items = sum(item["quantity"] for item in cart_items)
        
        return {"total_items": total_items}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при подсчете товаров: {str(e)}")

@router.post("/validate", response_model=APIResponse)
async def validate_cart(session_id: str = Depends(get_session_id)):
    """
    Валидация корзины перед оформлением заказа
    """
    try:
        cart_items = data_manager.get_cart(session_id)
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="Корзина пуста")
        
        # Проверяем доступность всех товаров
        unavailable_items = []
        for item in cart_items:
            product = data_manager.get_product_by_id(item["id"])
            if not product:
                unavailable_items.append(item["name"])
        
        if unavailable_items:
            return APIResponse(
                success=False,
                message=f"Некоторые товары недоступны: {', '.join(unavailable_items)}",
                data={"unavailable_items": unavailable_items}
            )
        
        total_amount = sum(item["price"] * item["quantity"] for item in cart_items)
        
        return APIResponse(
            message="Корзина готова к оформлению",
            data={
                "items_count": len(cart_items),
                "total_amount": total_amount,
                "valid": True
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при валидации корзины: {str(e)}")