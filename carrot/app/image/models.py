import uuid
from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from carrot.db.common import Base
from carrot.app.user.models import User

if TYPE_CHECKING:
    from carrot.app.product.models import Product

class ProductImage(Base):
    __tablename__ = "product_image"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    
    product: Mapped["Product"] = relationship("Product", back_populates="images")
    
# class UserImage(Base):
#     __tablename__ = "user_image"

#     id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
#     image_url: Mapped[str] = mapped_column(String(255), nullable=False)
#     user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
#     user: Mapped[User] = relationship("User", back_populates="images")