from fastapi  import APIRouter

router = APIRouter(prefix="/products",
                   tags=["products"],
                   )

@router.get('/')
async def get_all_products():
    """
    Get all products
    """
    return {"message": "все товары"}

@router.post("/")
async def create_product():
    """
    Создать новый продукт
    """
    return {"message": "Новый продукт"}

@router.get('/category/{category_id}')
async def get_products_by_category(category_id: int):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    return {"message": f"Товары в категории {category_id} (заглушка)"}

@router.get("/{product_id}")
async def get_product(product_id: int):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    return {"message": f"Детали товара {product_id} (заглушка)"}

@router.put("/{product_id}")
async def create_product(product_id: int):
    """
    ОБновляем продукт 

    """
    return {"message": f"Обновили продукт {product_id}"}

@router.delete("/{product_id}")
async def delete_product(product_id: int):
    """
    Удаляем продукт
    """
    return {"message": f"Удалили продукт {product_id}"}












