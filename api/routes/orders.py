"""
Orders API routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
import asyncio

from api.models import Order
from api.notifications import send_telegram_notifications, send_status_update_notification
from database import db

try:
    from psycopg2.extras import RealDictCursor
except ImportError:
    RealDictCursor = None

router = APIRouter()

# Compatibility wrapper for existing code
get_db = db.get_connection


def get_cursor(conn):
    """Get cursor with dict support for both SQLite and PostgreSQL"""
    if db.use_postgres and RealDictCursor:
        return conn.cursor(cursor_factory=RealDictCursor)
    else:
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        return conn.cursor()


def fix_query(query: str) -> str:
    """Convert ? placeholders to %s for PostgreSQL"""
    if db.use_postgres:
        return query.replace('?', '%s')
    return query


def get_agg_func():
    """Get the appropriate aggregation function for the current database"""
    if db.use_postgres:
        return "STRING_AGG(oi.product_id || ':' || oi.product_name || ':' || oi.quantity || ':' || oi.price || ':', ',')"
    else:
        return "GROUP_CONCAT(oi.product_id || ':' || oi.product_name || ':' || oi.quantity || ':' || oi.price || ':')"


@router.post("/api/orders", response_model=Order)
async def create_order(order: Order):
    """Создать новый заказ в БД"""
    order_id = str(uuid.uuid4())[:8]  # Короткий ID
    created_at = datetime.now()

    # Вычисляем общую сумму
    total = 0
    with get_db() as conn:
        cursor = get_cursor(conn)

        for item in order.items:
            cursor.execute(fix_query('SELECT * FROM products WHERE id = ?'), (item.product_id,))
            row = cursor.fetchone()
            if row:
                total += float(row['price']) * item.quantity

        # Сохраняем заказ
        cursor.execute(fix_query('''
            INSERT INTO orders (id, customer_name, customer_phone, customer_address,
                               customer_telegram, user_telegram_id, total_amount, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''), (
            order_id,
            order.customer_name,
            order.customer_phone,
            order.customer_address,
            order.customer_telegram,
            order.user_telegram_id,
            total,
            order.status,
            created_at.isoformat()
        ))

        # Сохраняем элементы заказа с информацией о продукте и поваре
        for item in order.items:
            cursor.execute(fix_query('SELECT * FROM products WHERE id = ?'), (item.product_id,))
            row = cursor.fetchone()
            if row:
                # Конвертируем Row в dict для безопасного доступа
                row_dict = dict(row)
                cursor.execute(fix_query('''
                    INSERT INTO order_items (order_id, product_id, product_name, quantity, price, cook_name, cook_phone, cook_telegram)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                '''), (
                    order_id,
                    item.product_id,
                    row_dict['name'],
                    item.quantity,
                    row_dict['price'],
                    row_dict.get('cook_name', ''),
                    row_dict.get('cook_phone', ''),
                    row_dict.get('cook_telegram', '')
                ))

        conn.commit()

        # Получаем полный заказ для уведомлений
        # Use STRING_AGG for PostgreSQL or GROUP_CONCAT for SQLite
        if db.use_postgres:
            concat_query = '''
                SELECT o.*,
                       STRING_AGG(
                           oi.product_id || ':' || oi.product_name || ':' ||
                           oi.quantity || ':' || oi.price || ':' ||
                           COALESCE(oi.cook_telegram, ''), ','
                       ) as items_data
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.id = %s
                GROUP BY o.id
            '''
        else:
            concat_query = '''
                SELECT o.*,
                       GROUP_CONCAT(
                           oi.product_id || ':' || oi.product_name || ':' ||
                           oi.quantity || ':' || oi.price || ':' ||
                           COALESCE(oi.cook_telegram, '')
                       ) as items_data
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.id = ?
                GROUP BY o.id
            '''
        cursor.execute(concat_query, (order_id,))
        full_order = dict(cursor.fetchone())

    order.id = order_id
    order.total_amount = total
    order.created_at = created_at.isoformat()

    # 🔥 ОТПРАВЛЯЕМ УВЕДОМЛЕНИЯ!
    asyncio.create_task(send_telegram_notifications(full_order))

    return order


@router.get("/api/orders")
async def get_orders():
    """Получить все заказы из БД"""
    with get_db() as conn:
        cursor = get_cursor(conn)
        agg_func = get_agg_func()

        cursor.execute(f'''
            SELECT o.*,
                   {agg_func} as items_data
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.created_at DESC
        ''')

        rows = cursor.fetchall()

        orders = []
        for row in rows:
            order = dict(row)

            # Парсим items
            items = []
            if order['items_data']:
                for item_str in order['items_data'].split(','):
                    parts = item_str.split(':')
                    items.append({
                        'product_id': parts[0],
                        'product_name': parts[1],
                        'quantity': int(parts[2]),
                        'price': float(parts[3]),
                        'cook_name': parts[4] if len(parts) > 4 else '',
                        'cook_phone': parts[5] if len(parts) > 5 else ''
                    })

            order['items'] = items
            del order['items_data']

            orders.append(order)

        return orders


@router.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """Получить конкретный заказ из БД"""
    with get_db() as conn:
        cursor = get_cursor(conn)

        cursor.execute(fix_query('SELECT * FROM orders WHERE id = ?'), (order_id,))
        order_row = cursor.fetchone()

        if not order_row:
            raise HTTPException(status_code=404, detail="Order not found")

        order = dict(order_row)

        # Получаем items
        cursor.execute(fix_query('''
            SELECT oi.*, p.name as product_name
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        '''), (order_id,))

        items = [dict(row) for row in cursor.fetchall()]
        order['items'] = items

        return order


@router.put("/api/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    """Обновить статус заказа"""
    valid_statuses = ['pending', 'confirmed', 'cooking', 'ready', 'delivered', 'cancelled']

    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    with get_db() as conn:
        cursor = get_cursor(conn)
        cursor.execute(fix_query('UPDATE orders SET status = ? WHERE id = ?'), (status, order_id))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")

        conn.commit()

        # Получаем данные заказа для уведомления
        # Use STRING_AGG for PostgreSQL or GROUP_CONCAT for SQLite
        if db.use_postgres:
            concat_query = '''
                SELECT o.*,
                       STRING_AGG(
                           oi.product_id || ':' || oi.product_name || ':' ||
                           oi.quantity || ':' || oi.price || ':' ||
                           COALESCE(oi.cook_telegram, ''), ','
                       ) as items_data
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.id = %s
                GROUP BY o.id
            '''
        else:
            concat_query = '''
                SELECT o.*,
                       GROUP_CONCAT(
                           oi.product_id || ':' || oi.product_name || ':' ||
                           oi.quantity || ':' || oi.price || ':' ||
                           COALESCE(oi.cook_telegram, '')
                       ) as items_data
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.id = ?
                GROUP BY o.id
            '''
        cursor.execute(concat_query, (order_id,))
        order = cursor.fetchone()

    if order:
        order_dict = dict(order)
        # 🔥 Отправляем уведомление о смене статуса
        asyncio.create_task(send_status_update_notification(order_dict))

    return {"message": "Order status updated", "order_id": order_id, "status": status}


@router.delete("/api/orders/{order_id}")
async def delete_order(order_id: str):
    """Удалить заказ из БД"""
    with get_db() as conn:
        cursor = get_cursor(conn)

        # Удаляем items заказа
        cursor.execute(fix_query('DELETE FROM order_items WHERE order_id = ?'), (order_id,))

        # Удаляем сам заказ
        cursor.execute(fix_query('DELETE FROM orders WHERE id = ?'), (order_id,))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")

        conn.commit()

    return {"message": "Order deleted", "order_id": order_id}
