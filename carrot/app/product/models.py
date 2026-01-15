import uuid
from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from carrot.db.common import Base

from carrot.app.user.models import User
from carrot.app.category.models import Category
from carrot.app.image.models import ProductImage

class Product(Base):
    __tablename__ = "product"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id:  Mapped[str] = mapped_column(String(36), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(50))
    images: Mapped[list["ProductImage"]] = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    content: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[Category] = relationship("User")
    category: Mapped[Category] = relationship("Category")
    
class UserProduct(Base):
    __tablename__ = "user_product"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    like: Mapped[bool] = mapped_column(Boolean, default=False)

    
    user: Mapped[User] = relationship("User")
    product: Mapped[Product] = relationship("Product")