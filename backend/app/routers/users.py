from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update

from app.schemas import UserCreate, UserResponce, RefreshTokenRequest
from app.models.users import User 
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token
import jwt
from app.config import SECRET_KEY, ALGORITHM
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db

router = APIRouter(prefix="/api/users",
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
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

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

@router.post("/refresh_token")
async def refresh_token(body: RefreshTokenRequest,
                        db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет refresh-токен, принимая старый refresh-токен в теле запроса.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    old_refresh_token = body.refresh_token

    try:
        payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        # Проверяем, что токен действительно refresh
        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        # refresh-токен истёк
        raise credentials_exception
    except jwt.PyJWTError:
        # подпись неверна или токен повреждён
        raise credentials_exception

    # Проверяем, что пользователь существует и активен
    result = await db.scalars(
        select(User).where(
            User.email == email,
            User.is_active == True
        )
    )
    user = result.first()
    if user is None:
        raise credentials_exception

    # Генерируем новый refresh-токен
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }    

@router.post("/access_token")
async def access_token(body: RefreshTokenRequest,
                        db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет access-токен, принимая старый refresh-токен в теле запроса.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    old_refresh_token = body.refresh_token

    try:
        payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        # Проверяем, что токен действительно refresh
        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.PyJWTError:
        # подпись неверна или токен повреждён
        raise credentials_exception

    # Проверяем, что пользователь существует и активен
    result = await db.scalars(
        select(User).where(
            User.email == email,
            User.is_active == True
        )
    )
    user = result.first()
    if user is None:
        raise credentials_exception

    # Генерируем новый access-токен
    new_access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }    







