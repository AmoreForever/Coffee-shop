from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from coffeeapp.core.config import settings
from coffeeapp.core.scheduler import setup_scheduler
from coffeeapp.api.v1.endpoints import users, auth, products, categories, cart, orders, chat
from coffeeapp.api.v1.endpoints.chat import router as chat_router
from coffeeapp.core.security import SecurityMiddleware, SQLInjectionMiddleware
from starlette_csrf import CSRFMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from coffeeapp.db.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация БД при запуске
    init_db()
    # Настройка планировщика при запуске
    scheduler = setup_scheduler()
    scheduler.start()
    yield
    # Очистка ресурсов при выключении
    # Здесь можно добавить cleanup код

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Настройка CORS с более строгими параметрами
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Добавляем middleware безопасности
app.add_middleware(SecurityMiddleware)
app.add_middleware(SQLInjectionMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  
)

# Добавляем CSRF защиту только в продакшене
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        CSRFMiddleware, 
        secret=settings.SECRET_KEY
    )

# Подключение роутеров API v1
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)

app.include_router(
    products.router,
    prefix=f"{settings.API_V1_STR}/products",
    tags=["products"]
)

app.include_router(
    categories.router,
    prefix=f"{settings.API_V1_STR}/categories",
    tags=["categories"]
)

app.include_router(
    cart.router,
    prefix=f"{settings.API_V1_STR}",
    tags=["cart"]
)

app.include_router(
    orders.router,
    prefix=f"{settings.API_V1_STR}/orders",
    tags=["orders"]
)

app.include_router(chat_router)

# Кастомизация OpenAPI схемы
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="API для сети кофеен на вынос",
        routes=app.routes,
    )
    
    # Добавляем Bearer Auth в схему безопасности
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    
    openapi_schema["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Корневой эндпоинт
@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в API сети кофеен",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Эндпоинт для проверки работоспособности
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True  
    )
