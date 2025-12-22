from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import Category 
from app.schemas import CategoryCreate, CategoryResponce


from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db

router = APIRouter(prefix="/api/categories",
                   tags=["categories"],
                   )

@router.get('/', response_model=list[CategoryResponce], status_code=status.HTTP_200_OK)
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    """
    Get all active categories
    """
    stmt = select(Category).where(Category.is_active == True)
    result = await db.scalars(stmt)
    categories = result.all()
    return categories

@router.post("/", response_model=CategoryResponce, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Create a new category
    """
    # Проверка существования родительской категории, если указан parent_id
    if category.parent_id is not None:
        stmt = select(Category).where(
            Category.id == category.parent_id,
            Category.is_active == True
        )
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent category with id {category.parent_id} not found"
            )
    
    # Создание новой категории
    db_category = Category(
        name=category.name,
        parent_id=category.parent_id,
        is_active=True  # Убедитесь, что по умолчанию активна
    )
    
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)  # Обязательно для получения сгенерированного id
    return db_category

@router.put("/{category_id}", response_model=CategoryCreate, status_code=status.HTTP_200_OK)
async def update_category(category_id: int, category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    """
    ОБновляем категрию 

    """
    stmt = select(Category).where(Category.id == category_id, Category.is_active == True)
    result = await db.scalars(stmt)
    db_category = result.first()

    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.parent_id is not None:
        parent_stmt = select(Category).where(Category.id == category.parent_id,
                                           Category.is_active == True)
        result = await db.scalars(parent_stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")
        
    #Обновляем 
    update_data = category.model_dump(exclude_unset=True)
    await db.execute(
    update(Category)
    .where(Category.id == category_id)
    .values(**update_data)
    )
    await db.commit()
    return db_category

@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Удаляем категорию
    """
    stmt = select(Category).where(Category.id == category_id,
                                       Category.is_active == True)
    result = await db.scalars(stmt)
    db_category = result.first()
    
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await db.execute(update(Category).where(Category.id == category_id).values(is_active=False))
    await db.commit()

    return {"status": "success", "message": "Category marked as inactive"}











