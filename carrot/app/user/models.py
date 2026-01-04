import uuid
import enum

from sqlalchemy import String, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from carrot.db.common import Base

from carrot.app.region.models import Region


class UserStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(100))

    nickname: Mapped[str | None] = mapped_column(String(20))
    profile_image: Mapped[str | None] = mapped_column(String(150))
    coin: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    region_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("region.id", ondelete="CASCADE"), index=True
    )
    region: Mapped[Region | None] = relationship("Region")

    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.PENDING, nullable=False
    )


class SocialAccount(Base):
    __tablename__ = "social_account"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped[User] = relationship("User")

    provider: Mapped[str] = mapped_column(String(20))
    provider_sub: Mapped[str] = mapped_column(String(256))
