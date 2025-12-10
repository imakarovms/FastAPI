from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import Category 
from app.schemas import CategoryCreate, CategoryResponce
from app.db_depends import get_db

router = APIRouter(prefix="/categories",
                   tags=["categories"],
                   )

@router.get('/', response_model=list[CategoryResponce], status_code=status.HTTP_200_OK)
async def get_all_categories(db:Session = Depends(get_db)):
    """
    Get all categories
    """
    stmt = select(Category).where(Category.is_active == True)
    categories = db.scalars(stmt).all()
    return categories
    

@router.post("/", response_model=CategoryResponce, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Создать новую категорию
    """
    #Проверяем есть ли родительская категория, если указан
    if category.parent_id is not None:
        stmt = select(Category).where(Category.id == category.parent_id,
                                           Category.is_active == True)
        parent = db.scalars(stmt).first()

        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")
    
    # Создание новой категории
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=CategoryCreate, status_code=status.HTTP_200_OK)
async def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    """
    ОБновляем категрию 

    """
    stmt = select(Category).where(Category.id == category_id, Category.is_active == True)
    db_category = db.scalars(stmt).first()

    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.parent_id is not None:
        parent_stmt = select(Category).where(Category.id == category.parent_id,
                                           Category.is_active == True)
        parent = db.scalars(parent_stmt).first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")
        
    #Обновляем 
    db.execute(
    update(Category)
    .where(Category.id == category_id)
    .values(**category.model_dump())
    )
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Удаляем категорию
    """
    stmt = select(Category).where(Category.id == category_id, Category.is_active == True)
    category = db.scalars(stmt).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    db.execute(update(Category).where(Category.id == category_id).values(is_active=False))
    db.commit()

    return {"status": "success", "message": "Category marked as inactive"}











