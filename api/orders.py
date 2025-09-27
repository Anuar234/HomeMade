"""
API endpoints для заказов
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from models.schemas import Order, APIResponse
from database.data import data_manager
from datetime import datetime

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/", response_model=Order)
async def create_order(order: Order):
    """
    Создать новый заказ
    """
    try:
        # Валидация товаров в заказе
        for item in order.items:
            product = data_manager.get_product_by_id(item.product_id)
            if not product:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Продукт с ID {item.product_id} не найден"
                )
        
        # Создание заказа
        order_data = order.dict()
        order_data["created_at"] = datetime.now()
        
        created_order = data_manager.create_order(order_data)
        
        return created_order
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании заказа: {str(e)}")

@router.get("/", response_model=List[Order])
async def get_orders(
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    customer_phone: Optional[str] = Query(None, description="Фильтр по телефону клиента"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Лимит результатов"),
    offset: Optional[int] = Query(0, ge=0, description="Смещение для пагинации")
):
    """
    Получить список заказов с фильтрацией
    """
    try:
        orders = data_manager.get_all_orders()
        
        # Фильтрация по статусу
        if status:
            orders = [o for o in orders if o.get("status") == status]
        
        # Фильтрация по телефону
        if customer_phone:
            orders = [o for o in orders if o.get("customer_phone") == customer_phone]
        
        # Сортировка по дате создания (новые сначала)
        orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Пагинация
        if offset:
            orders = orders[offset:]
        if limit:
            orders = orders[:limit]
        
        return orders
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении заказов: {str(e)}")

@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """
    Получить конкретный заказ по ID
    """
    try:
        order = data_manager.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        return order
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении заказа: {str(e)}")

@router.patch("/{order_id}/status", response_model=APIResponse)
async def update_order_status(order_id: str, status_data: dict = Body(...)):
    """
    Обновить статус заказа
    """
    try:
        new_status = status_data.get("status")
        if not new_status:
            raise HTTPException(status_code=400, detail="Поле 'status' обязательно")
            
        # Валидация статуса
        valid_statuses = ["pending", "confirmed", "preparing", "ready", "delivered", "cancelled"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Неверный статус. Доступные: {', '.join(valid_statuses)}"
            )
        
        order = data_manager.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        
        updated_order = data_manager.update_order(order_id, {"status": new_status})
        return APIResponse(message=f"Статус заказа изменен на '{new_status}'")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении статуса: {str(e)}")

@router.delete("/{order_id}", response_model=APIResponse)
async def cancel_order(order_id: str):
    """
    Отменить заказ
    """
    try:
        order = data_manager.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        
        if order.get("status") in ["delivered", "cancelled"]:
            raise HTTPException(
                status_code=400, 
                detail="Нельзя отменить доставленный или уже отмененный заказ"
            )
        
        data_manager.update_order(order_id, {"status": "cancelled"})
        return APIResponse(message="Заказ успешно отменен")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при отмене заказа: {str(e)}")

@router.get("/stats/summary")
async def get_orders_stats():
    """
    Получить статистику по заказам
    """
    try:
        orders = data_manager.get_all_orders()
        
        # Статистика по статусам
        status_stats = {}
        total_revenue = 0
        total_orders = len(orders)
        
        for order in orders:
            status = order.get("status", "unknown")
            if status not in status_stats:
                status_stats[status] = {"count": 0, "total_amount": 0}
            
            status_stats[status]["count"] += 1
            status_stats[status]["total_amount"] += order.get("total_amount", 0)
            
            if status not in ["cancelled"]:
                total_revenue += order.get("total_amount", 0)
        
        # Средний чек
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "average_order_value": avg_order_value,
            "status_breakdown": status_stats,
            "completion_rate": (
                status_stats.get("delivered", {}).get("count", 0) / total_orders * 100 
                if total_orders > 0 else 0
            )
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении статистики заказов: {str(e)}")

@router.get("/customer/{customer_phone}")
async def get_customer_orders(customer_phone: str):
    """
    Получить все заказы конкретного клиента
    """
    try:
        orders = data_manager.get_all_orders()
        customer_orders = [o for o in orders if o.get("customer_phone") == customer_phone]
        
        # Сортировка по дате создания (новые сначала)
        customer_orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "customer_phone": customer_phone,
            "total_orders": len(customer_orders),
            "orders": customer_orders
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении заказов клиента: {str(e)}")