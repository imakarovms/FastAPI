from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, update, func, desc, update
from sqlalchemy.orm import Session

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
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_seller)):
    """
    Создаёт новый товар, привязанный к текущему продавцу (только для 'seller').
    """
    category_result = await db.scalars(
        select(Category).where(Category.id == product.category_id, Category.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")
    db_product = Product(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)  # Для получения id и is_active из базы
    return db_product   

@router.get('/category/{category_id}', response_model=list[ProductResponce], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    # Проверяет, существует ли категория с указанным category_id.
    # Если нет, возвращает ошибку HTTP 404 ("Category not found").
    category_stmt = await db.scalars(select(Category).where(Category.id == category_id,
                                      Category.is_active == True))
    db_category = category_stmt.first()

    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    #Возвращает список всех активных товаров (is_active=True) в указанной категории в формате list[Product].
    product_stmt = await db.scalars(select(Product).where(Product.is_active == True,
                                         Product.category_id == category_id))
    produts = product_stmt.all()
    return produts



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
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_seller)
):
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller').
    """
    result = await db.scalars(select(Product).where(Product.id == product_id, Product.is_active == True))
    db_product = result.first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")
    category_result = await db.scalars(
        select(Category).where(Category.id == product.category_id, Category.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")
    await db.execute(
        update(Product).where(Product.id == product_id).values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(db_product)  # Для консистентности данных
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
    await db.commit()
    await db.refresh(product)  # Для возврата is_active = False
    return product

                  













