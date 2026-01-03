import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from carrot.db.common import Base

from carrot.app.region import Region

class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    nickname: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(20))
    profile_image: Mapped[str | None] = mapped_column(String(150))
    coin: Mapped[int] = mapped_column(Integer, nullable=False)
    region_id: Mapped[str] = mapped_column(String(36), ForeignKey("region.id", ondelete="CASCADE"), primary_key=True, index=True)
    
    region_id: Mapped[Region] = relationship("Region")