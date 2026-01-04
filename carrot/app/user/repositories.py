from typing import Annotated
import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from carrot.app.user.models import LocalAccount, SocialAccount, User
from carrot.db.connection import get_db_session


class UserRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def create_user(self, email: str) -> User:
        user = User(email=email)
        self.session.add(user)

        self.session.flush()

        return user

    def update_user(self, user: User) -> User:
        self.session.merge(user)
        self.session.flush()
        return user

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.session.scalar(select(User).where(User.id == user_id))

    def get_user_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))

    def get_user_by_nickname(self, nickname: str) -> User | None:
        return self.session.scalar(select(User).where(User.nickname == nickname))

    def get_social_account_by_provider(
        self, provider: str, sub: str
    ) -> SocialAccount | None:
        return self.session.scalar(
            select(SocialAccount).where(
                SocialAccount.provider == provider and SocialAccount.provider_sub == sub
            )
        )

    def create_social_account(self, user_id: str, provider: str, provider_sub: str):
        social_account = SocialAccount(
            user_id=user_id, provider=provider, provider_sub=provider_sub
        )
        self.session.add(social_account)
        self.session.flush()
        return social_account

    def get_local_account_by_id(self, user_id: str):
        return self.session.scalar(
            select(LocalAccount).where(LocalAccount.user_id == user_id)
        )

    def create_local_account(self, user_id: str, hashed_password: str):
        local_acount = LocalAccount(user_id=user_id, hashed_password=hashed_password)
        self.session.add(local_acount)
        self.session.flush()
        return local_acount
