import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from carrot.db.common import Base

from carrot.app.user.models import User
from carrot.app.product.models import Product

class ChatRoom(Base):
    __tablename__ = "chat_room"

    # id는 String(36)으로 유지하되, product_id와 함께 복합 PK로 설정하신 의도를 살렸습니다.
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("product.id", ondelete="CASCADE"), primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship("Product")
    # 방에 속한 메시지들을 역참조할 수 있게 추가
    messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="chatroom", cascade="all, delete-orphan")

class UserChatRoom(Base):
    """유저와 채팅방의 다대다 관계를 관리하는 중간 테이블"""
    __tablename__ = "user_chat_room"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id", ondelete="CASCADE"), index=True)
    chat_room_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_room.id", ondelete="CASCADE"), index=True)
    
    # 단순히 '읽지 않음' 여부보다, 마지막으로 읽은 시간을 기록하는 것이 나중에 '안 읽은 개수' 계산에 더 유리합니다.
    # 하지만 일단 기존 구조를 살려 유지합니다.
    has_unread: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User")
    chat_room: Mapped["ChatRoom"] = relationship("ChatRoom")

class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    # String(20)보다는 실제 DateTime 타입을 쓰는 것이 정렬(Sorting)할 때 훨씬 빠르고 정확합니다.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    message: Mapped[str] = mapped_column(Text) # 긴 메시지를 위해 Text 타입 추천
    
    # sender는 User.id와 동일한 String(36)이어야 합니다.
    sender_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"), nullable=False)
    
    # 1:1 채팅이나 그룹채팅에서 '남은 인원 수'를 표현하기 위한 필드
    read_count: Mapped[int] = mapped_column(Integer, default=1) 
    
    # 🔥 수정: ForeignKey가 category.id로 되어있던 것을 chat_room.id로 변경
    chatroom_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_room.id", ondelete="CASCADE"), index=True)

    chatroom: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="messages")
    sender: Mapped["User"] = relationship("User")