from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, status
from sqlalchemy import select, update, func, desc, update
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
from app.models.products import Product 
from app.schemas import ProductResponce, ProductCreate, ProductList
from app.models.categories import Category 
from app.auth import get_current_seller
from app.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from typing import Optional
from app.db_depends import get_async_db


router = APIRouter(prefix="/products",
                   tags=["products"],
                   )


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_ROOT = BASE_DIR / "media" / "products"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 097 152 байт

@router.get("/", response_model=ProductList)
async def get_all_products(
    page: int = Query(1, ge=1, description="Номер страницы для пагинации"),
    page_size: int = Query(20, ge=1, le=100, description="Количество товаров на странице"),
    category_id: Optional[int] = Query(
        None, description="ID категории для фильтрации"
    ),
    min_price: Optional[float] = Query(
        None, ge=0, description="Минимальная цена товара"
    ),
    max_price: Optional[float] = Query(
        None, ge=0, description="Максимальная цена товара"
    ),
    in_stock: Optional[bool] = Query(
        None, description="true — только товары в наличии, false — только без остатка"
    ),
    seller_id: Optional[int] = Query(
        None, description="ID продавца для фильтрации"
    ),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Возвращает список всех активных товаров с поддержкой фильтров и пагинации.
    
    Фильтры применяются последовательно:
    - category_id: фильтрация по категории
    - min_price/max_price: фильтрация по ценовому диапазону
    - in_stock: фильтрация по наличию товара
    - seller_id: фильтрация по продавцу
    
    Пагинация:
    - page: номер страницы (начиная с 1)
    - page_size: количество элементов на странице (максимум 100)
    """
    # Проверка логики min_price <= max_price
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price не может быть больше max_price",
        )
    
    # Валидация существования категории
    if category_id is not None:
        from app.models.categories import Category
        category_exists = await db.scalar(
            select(func.count()).where(Category.id == category_id, Category.is_active == True)
        )
        if category_exists == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Категория с ID {category_id} не существует или неактивна",
            )
    
    # Валидация существования продавца
    if seller_id is not None:
        from app.models.users import User
        seller_exists = await db.scalar(
            select(func.count()).where(User.id == seller_id, User.is_active == True, User.role == "seller")
        )
        if seller_exists == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Продавец с ID {seller_id} не существует или неактивен",
            )

    # Формируем список фильтров
    filters = [Product.is_active == True]

    if category_id is not None:
        filters.append(Product.category_id == category_id)
    if min_price is not None:
        filters.append(Product.price >= Decimal(str(min_price)))
    if max_price is not None:
        filters.append(Product.price <= Decimal(str(max_price)))
    if in_stock is True:
        filters.append(Product.stock > 0)
    elif in_stock is False:
        filters.append(Product.stock == 0)
    if seller_id is not None:
        filters.append(Product.seller_id == seller_id)

    # Подсчёт общего количества с учётом фильтров
    total_stmt = select(func.count()).select_from(Product).where(*filters)
    total = await db.scalar(total_stmt) or 0

    # Проверка валидности номера страницы
    max_page = (total + page_size - 1) // page_size
    if page > max_page and total > 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Страница {page} не существует. Максимальный номер страницы: {max_page}",
        )

    # Выборка товаров с фильтрами и пагинацией
    products_stmt = (
        select(Product)
        .where(*filters)
        .order_by(Product.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = (await db.scalars(products_stmt)).all()
    
    # Явное преобразование ORM-объектов в Pydantic модели
    product_items = [
        ProductResponce.model_validate(item) 
        for item in items
    ]

    return ProductList(
        items=product_items,
        total=total,
        page=page,
        page_size=page_size
    )
    
@router.post("/", response_model=ProductResponce, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: ProductCreate = Depends(ProductCreate.as_form),
        image: UploadFile | None = File(None),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_seller)
):
    """
    Создаёт новый товар, привязанный к текущему продавцу (только для 'seller').
    """

    category_result = await db.scalars(
        select(Category).where(Category.id == product.category_id,
                                    Category.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")

    # Сохранение изображения (если есть)
    image_url = await save_product_image(image) if image else None

    # Создание товара
    db_product = Product(
        **product.model_dump(),
        seller_id=current_user.id,
        image_url=image_url,
    )

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.get('/categories/{category_id}', response_model=list[ProductResponce], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    # Проверяем существование активной категории
    category_stmt = select(Category).where(
        Category.id == category_id,
        Category.is_active == True
    )
    category_result = await db.execute(category_stmt)
    db_category = category_result.scalars().first()

    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Получаем активные товары в категории
    product_stmt = select(Product).where(
        Product.is_active == True,
        Product.category_id == category_id
    )
    product_result = await db.execute(product_stmt)
    products = product_result.scalars().all()
    
    return products



@router.get("/{product_id}", response_model=ProductResponce)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    # Проверяем, существует ли активный товар
    product_result = await db.scalars(
        select(Product).where(Product.id == product_id, Product.is_active == True)
    )
    product = product_result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    # Проверяем, существует ли активная категория
    category_result = await db.scalars(
        select(Category).where(Category.id == product.category_id,
                                    Category.is_active == True)
    )
    category = category_result.first()
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")

    return product


from sqlalchemy import update

@router.put("/{product_id}", response_model=ProductResponce)
async def update_product(
        product_id: int,
        product: ProductCreate = Depends(ProductCreate.as_form),
        image: UploadFile | None = File(None),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_seller)
):
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller').
    """
    result = await db.scalars(select(Product).where(Product.id == product_id))
    db_product = result.first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only update your own products")
    category_result = await db.scalars(
        select(Category).where(Category.id == product.category_id,
                                    Category.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or inactive")

    await db.execute(
        update(Product).where(Product.id == product_id).values(**product.model_dump())
    )

    if image:
        remove_product_image(db_product.image_url)
        db_product.image_url = await save_product_image(image)

    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", response_model=ProductResponce)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_seller)
):
    """
    Выполняет мягкое удаление товара, если он принадлежит текущему продавцу (только для 'seller').
    """
    result = await db.scalars(
        select(Product).where(Product.id == product_id, Product.is_active == True)
    )
    product = result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")
    await db.execute(
        update(Product).where(Product.id == product_id).values(is_active=False)
    )
    remove_product_image(product.image_url)

    await db.commit()
    await db.refresh(product)
    return product

async def save_product_image(file: UploadFile) -> str:
    """
    Сохраняет изображение товара и возвращает относительный URL.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only JPG, PNG or WebP images are allowed")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Image is too large")

    extension = Path(file.filename or "").suffix.lower() or ".jpg"
    file_name = f"{uuid.uuid4()}{extension}"
    file_path = MEDIA_ROOT / file_name
    file_path.write_bytes(content)

    return f"/media/products/{file_name}"

def remove_product_image(url: str | None) -> None:
    """
    Удаляет файл изображения, если он существует.
    """
    if not url:
        return
    relative_path = url.lstrip("/")
    file_path = BASE_DIR / relative_path
    if file_path.exists():
        file_path.unlink()











