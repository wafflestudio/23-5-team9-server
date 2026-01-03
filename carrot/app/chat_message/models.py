import uuid
from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from carrot.db.common import Base

from carrot.app.chat_room import Chatroom

class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    time: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(500))
    sender: Mapped[int] = mapped_column(String(36))
    read_count: Mapped[int] = mapped_column(Integer, nullable=False)
    chatroom_id: Mapped[str] = mapped_column(String(36), ForeignKey("category.id", ondelete="CASCADE"), primary_key=True, index=True)

    chatroom_id: Mapped[Chatroom] = relationship("Chatroom")