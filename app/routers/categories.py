from fastapi  import APIRouter

router = APIRouter(prefix="/categories",
                   tags=["categories"],
                   )

@router.get('/')
async def get_all_categories():
    """
    Get all categories
    """
    return {"message": "все категории товара"}

@router.post("/")
async def create_category():
    """
    Создать новую категорию
    """
    return {"message": "Новая категрия"}

@router.put("/{category_id}")
async def update_category(category_id: int):
    """
    ОБновляем категрию 

    """
    return {"message": f"Обновили категорию {category_id}"}

@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """
    Удаляем категорию
    """
    return {"message": f"Удалили категорию {category_id}"}












