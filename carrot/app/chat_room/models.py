import uuid
from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from carrot.db.common import Base

from carrot.app.user import User
from carrot.app.product import Product

class ChatRoom(Base):
    __tablename__ = "chat_room"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("product.id", ondelete="CASCADE"), primary_key=True, index=True)

    product_id: Mapped[Product] = relationship("Product")
    
class UserChatRoom(Base):
    __tablename__ = "user_chat_room"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id", ondelete="CASCADE"), primary_key=True, index=True)
    chat_room_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_room.id", ondelete="CASCADE"), primary_key=True, index=True)
    has_unread: Mapped[bool] = mapped_column(Boolean, nullable=False)

    
    user_id: Mapped[User] = relationship("User")
    chat_room_id: Mapped[ChatRoom] = relationship("Chatroom")