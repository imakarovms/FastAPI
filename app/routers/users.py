from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.products import Product 
from app.schemas import UserCreate, UserResponce
from app.models.categories import Category 
from app.models.users import User 
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import hash_password, verify_password, create_access_token

from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db

router = APIRouter(prefix="/users",
                   tags=["users"],
                   )

@router.get('/', response_model= list[UserResponce], status_code=status.HTTP_200_OK)
async def get_all_users(db: AsyncSession = Depends(get_async_db)):
    """
    Get all users
    """
    stmt = await db.scalars(select(User).where(User.is_active == True))
    users = stmt.all()
    return users

@router.post("/", response_model=UserResponce, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создать нового пользователя
    """

    result = await db.scalars(select(User).where(User.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,

                            detail="User with this email exists")

    # Создание объекта пользователя с хешированным паролем
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        is_active=True,
        role=user.role
    )

    # Добавление в сессию и сохранение в базе
    db.add(db_user)
    await db.commit()
    return db_user

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_db)):
    """
    Аутентифицирует пользователя и возвращает JWT с email, role и id.
    """
    result = await db.scalars(
        select(User).where(User.email == form_data.username, User.is_active == True))
    user = result.first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.delete("/{user_id}", response_model=UserResponce)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Выполняет мягкое удаление пользователя.
    """
    result = await db.scalars(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or inactive")
 
    await db.execute(update(User).where(User.id == user_id).values(is_active=False))
    await db.commit() # Для возврата is_active = False
    return user










