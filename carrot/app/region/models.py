import uuid
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from carrot.db.common import Base

class Region(Base):
    __tablename__ = "region"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    sido: Mapped[str] = mapped_column(String(20), nullable=False)
    sigugun: Mapped[str] = mapped_column(String(20), nullable=False)
    dong: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint('sido', 'sigugun', 'dong', name='uix_region_sido_sigugun_dong'),
    )

    @property
    def name(self):
        return f"{self.sido} {self.sigugun} {self.dong}"