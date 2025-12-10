from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.products import Product 
from app.schemas import ProductResponce, ProductCreate
from app.models.categories import Category 
from app.schemas import CategoryCreate, CategoryResponce

from app.db_depends import get_db

router = APIRouter(prefix="/products",
                   tags=["products"],
                   )

@router.get('/', response_model= list[ProductResponce], status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_db)):
    """
    Get all products
    """
    stmt = select(Product).where(Product.is_active == True)
    products = db.scalars(stmt).all()
    return products

@router.post("/", response_model=ProductResponce, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Создать новый продукт
    """
    if product.category_id is not None:
        stmt = select(Category).where(Category.id == product.category_id,
                                      Category.is_active == True)
        category = db.scalars(stmt).first()
        if category is None:
                        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )

    # Создание продукта
    db_product = Product(**product.model_dump(), is_active=True)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
    

@router.get('/category/{category_id}', response_model=list[ProductResponce], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    # Проверяет, существует ли категория с указанным category_id.
    # Если нет, возвращает ошибку HTTP 404 ("Category not found").
    category_stmt = select(Category).where(Category.id == category_id,
                                      Category.is_active == True)
    db_category = db.scalars(category_stmt).first()

    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    #Возвращает список всех активных товаров (is_active=True) в указанной категории в формате list[Product].
    product_stmt = select(Product).where(Product.is_active == True,
                                         Product.category_id == category_id)
    produts = db.scalars(product_stmt).all()
    return produts



@router.get("/{product_id}", response_model=ProductResponce, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """

    # Проверяет, существует ли активный товар (is_active=True) с указанным product_id. 
    # Если нет, возвращает ошибку HTTP 404 ("Product not found").
    stmt = select(Product).where(Product.is_active == True,
                                 Product.id == product_id)
    product = db.scalars(stmt).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    #Проверяет, существует ли категория с полученным category_id из объекта товара. 
    # Если нет, возвращает ошибку HTTP 400 ("Category not found").

    category_stmt = select(Category).where(
        Category.id == product.category_id,
        Category.is_active == True
    )
    category = db.scalars(category_stmt).first()
    
    if category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")
    
    return product

@router.put("/{product_id}", response_model=ProductResponce, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """
    ОБновляем продукт 
    Принимает product_id (параметр пути) и данные в формате ProductCreate.

    Проверяет, существует ли товар с указанным product_id. Если нет, возвращает ошибку HTTP 404 ("Product not found").

    Проверяет, существует ли категория с указанным category_id. Если нет, возвращает ошибку HTTP 400 ("Category not found").

    Обновляет поля товара (name, description, price, image_url, stock, category_id), сохраняя is_active без изменений.

    Возвращает обновлённый товар в формате Product.

    Код ответа: HTTP 200 OK.

    """
    stmt = select(Product).where(Product.id == product_id, Product.is_active == True)
    db_product = db.scalars(stmt).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    stmt_category = select(Category).where(Category.id == product.category_id, Category.is_active == True)
    db_category = db.scalars(stmt_category).first()
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")
    
    #Обновляем
    db.execute(
         update(Product)
         .where(Product.id == product_id)
         .values(**product.model_dump())
    )
    db.commit()
    db.refresh(db_product)
    return db_product



@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Удаляем продукт
    """
    stmt = select(Product).where(Product.id == product_id, Product.is_active == True)
    product = db.scalars(stmt).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.execute(update(Product).where(Product.id == product_id).values(is_active=False))
    db.commit()

    return {"status": "success", "message": "Product marked as inactive"}













