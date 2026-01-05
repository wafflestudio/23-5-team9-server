from typing import Annotated

from fastapi import Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from carrot.app.user.models import LocalAccount, SocialAccount, User
from carrot.db.connection import get_db_session


class UserRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
        self.session = session

    async def create_user(self, email: str) -> User:
        user = User(email=email)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_user(self, user: User) -> User:
        merged = await self.session.merge(user)
        await self.session.flush()
        return merged

    async def get_user_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_nickname(self, nickname: str) -> User | None:
        result = await self.session.execute(select(User).where(User.nickname == nickname))
        return result.scalar_one_or_none()

    async def get_social_account_by_provider(
        self, provider: str, sub: str
    ) -> SocialAccount | None:
        stmt = select(SocialAccount).where(
            and_(
                SocialAccount.provider == provider,
                SocialAccount.provider_sub == sub,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_social_account(
        self, user_id: str, provider: str, provider_sub: str
    ) -> SocialAccount:
        social_account = SocialAccount(
            user_id=user_id, provider=provider, provider_sub=provider_sub
        )
        self.session.add(social_account)
        await self.session.flush()
        return social_account

    async def get_local_account_by_id(self, user_id: str) -> LocalAccount | None:
        result = await self.session.execute(
            select(LocalAccount).where(LocalAccount.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_local_account(self, user_id: str, hashed_password: str) -> LocalAccount:
        local_account = LocalAccount(user_id=user_id, hashed_password=hashed_password)
        self.session.add(local_account)
        await self.session.flush()
        return local_account
