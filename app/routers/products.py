from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.products import Product 
from app.schemas import ProductResponce, ProductCreate
from app.models.categories import Category 
from app.auth import get_current_seller
from app.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db


router = APIRouter(prefix="/products",
                   tags=["products"],
                   )

@router.get('/', response_model= list[ProductResponce], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Get all products
    """
    stmt = await db.scalars(select(Product).where(Product.is_active == True))
    products = stmt.all()
    return products

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

                  













