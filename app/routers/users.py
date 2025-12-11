from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.products import Product 
from app.schemas import UserCreate, UserResponce
from app.models.categories import Category 
from app.models.users import User 

from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db

from app.auth import hash_password

router = APIRouter(prefix="/users",
                   tags=["users"],
                   )

@router.get('/', response_model= list[UserResponce], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Get all users
    """
    stmt = await db.scalars(select(User).where(User.is_active == True))
    users = stmt.all()
    return users

@router.post("/", response_model=UserResponce, status_code=status.HTTP_201_CREATED)
async def create_product(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создать нового пользователя
    """

    result = await db.scalars(select(User).where(User.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")

    # Создание объекта пользователя с хешированным паролем
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )

    # Добавление в сессию и сохранение в базе
    db.add(db_user)
    await db.commit()
    return db_user













