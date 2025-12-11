"""
Products API routes
"""
from fastapi import APIRouter
from typing import List, Optional
import json
from psycopg2.extras import RealDictCursor

from api.models import Product
from database import db

router = APIRouter()

# Compatibility wrapper for existing code
get_db = db.get_connection


@router.get("/api/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    print(f"🔍 API request: category={category}")
    print(f"🔗 Database: {'PostgreSQL' if db.use_postgres else 'SQLite'}")

    with get_db() as conn:
        # ВАЖНО: Для PostgreSQL используем RealDictCursor
        if db.use_postgres:
            from psycopg2.extras import RealDictCursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()

        if category:
            if db.use_postgres:
                query = "SELECT * FROM products WHERE LOWER(category) = LOWER(%s)"
            else:
                query = "SELECT * FROM products WHERE LOWER(category) = LOWER(?)"

            cursor.execute(query, (category,))
            print(f"📝 Query executed with category={category}")
        else:
            cursor.execute("SELECT * FROM products")
            print(f"📝 Query: SELECT all products")

        rows = cursor.fetchall()
        print(f"📊 Found {len(rows)} products")

        products = []
        for row in rows:
            product = dict(row)

            print(f"  📦 Product: {product.get('id')} - {product.get('name')}")

            # Обработка ingredients
            if product.get('ingredients'):
                try:
                    product['ingredients'] = json.loads(product['ingredients'])
                except Exception as e:
                    print(f"  ⚠️ Failed to parse ingredients: {e}")
                    product['ingredients'] = []
            else:
                product['ingredients'] = []

            products.append(product)

    print(f"✅ Returning {len(products)} products")
    return products
