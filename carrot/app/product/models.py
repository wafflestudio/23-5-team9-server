import uuid
from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from carrot.db.common import Base

from carrot.app.user.models import User
from carrot.app.category.models import Category

class Product(Base):
    __tablename__ = "product"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id:  Mapped[str] = mapped_column(String(36), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(50))
    content: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("category.id", ondelete="CASCADE"), primary_key=True, index=True)

    category: Mapped[Category] = relationship("Category")
    
class UserProduct(Base):
    __tablename__ = "user_product"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("product.id", ondelete="CASCADE"), primary_key=True, index=True)
    like: Mapped[bool] = mapped_column(Boolean, nullable=False)

    
    user: Mapped[User] = relationship("User")
    product: Mapped[Product] = relationship("Product")