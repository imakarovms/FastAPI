from fastapi import FastAPI
from app.routers import categories, products, users, cart

app = FastAPI(title="Ecommerce FastAPI",
              version="0.1.0")

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(cart.router)

@app.get("/")
async def root():
    """
    Корневой маршрут, АПИ работает
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}











