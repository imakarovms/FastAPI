from sqlalchemy import String, Boolean, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship  
from decimal import Decimal

from app.database import Base

class Product(Base):
    """
    таблица продуктов
    """
    __tablename__="products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)    
    image_url: Mapped[str | None] = mapped_column(String(100), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)

    category: Mapped["Category"] = relationship(
        back_populates= 'products'
    )
    seller = relationship("User", back_populates="products")  
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)












