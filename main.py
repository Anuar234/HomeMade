"""
FastAPI Application для Home Food Abu Dhabi
Модульная версия - использует api/ модули
"""

from fastapi import FastAPI

# Import from api modules
from api.config import configure_app
from api.routes import products_router, orders_router, frontend_router

# Import database
from database import db

# Create FastAPI app
app = FastAPI(title="Home Food Abu Dhabi")

# Configure app (CORS, static files, middleware)
configure_app(app)

# Register routers
app.include_router(frontend_router)  # HTML routes (/, /app, /app/{category})
app.include_router(products_router)  # /api/products
app.include_router(orders_router)    # /api/orders/*

# Print startup info
print("=" * 50)
print("FastAPI Application Started")
print("=" * 50)
print(f"   Database: {'PostgreSQL' if db.use_postgres else 'SQLite'}")
print(f"   Routes registered:")
print(f"     - Frontend: /, /app, /app/{{category}}")
print(f"     - API Products: /api/products")
print(f"     - API Orders: /api/orders/*")
print("=" * 50)


# For local development
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI in development mode...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
