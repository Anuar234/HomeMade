"""
Database wrapper for bot operations
"""

from database import (
    db,
    get_all_products,
    get_product_by_id,
    get_products_by_category,
    add_product,
    delete_product,
    get_all_orders,
    get_order_by_id,
    update_order_status,
    log_activity,
)

# Re-export for convenience
__all__ = [
    'db',
    'get_all_products',
    'get_product_by_id',
    'get_products_by_category',
    'add_product',
    'delete_product',
    'get_all_orders',
    'get_order_by_id',
    'update_order_status',
    'log_activity',
]


def get_orders_by_status(status: str):
    """Get orders filtered by status"""
    all_orders = get_all_orders()
    return [order for order in all_orders if order.get('status') == status]


def get_orders_by_user(user_telegram_id: int):
    """Get orders for specific user"""
    all_orders = get_all_orders()
    return [order for order in all_orders if order.get('user_telegram_id') == user_telegram_id]


def get_order_stats():
    """Get order statistics"""
    orders = get_all_orders()

    stats = {
        'total': len(orders),
        'by_status': {},
        'total_revenue': 0
    }

    for order in orders:
        status = order.get('status', 'unknown')
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        stats['total_revenue'] += order.get('total_amount', 0)

    return stats
