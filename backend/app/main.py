from fastapi import FastAPI
from app.routers import categories, products, users, cart, orders
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ecommerce FastAPI",
              version="0.1.0")
@app.get("/health")
async def health_check():
    return {"status": "ok", "database": "connected"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Vue CLI dev server
    "http://localhost:80",    # Nginx
        "http://nginx",           # Для Docker-сети
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры 
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(cart.router)
app.include_router(orders.router)

# Монтируем медиа-файлы
app.mount("/media", StaticFiles(directory="media"), name="media")

@app.get("/")
async def root():
    """
    Корневой маршрут, АПИ работает
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}














