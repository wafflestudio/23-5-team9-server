from typing import Annotated
from datetime import datetime

from fastapi import Depends

from carrot.app.auth.utils import (
    verify_password,
    issue_token,
    get_token_from_authorization_header,
    verify_and_decode_token,
)
from carrot.app.auth.exceptions import (
    InvalidAccountException,
    RevokedTokenException,
    UnauthenticatedException,
    InvalidTokenException,
)
from carrot.app.auth.repositories import AuthRepository
from carrot.app.auth.settings import AUTH_SETTINGS
from carrot.app.user.models import User
from carrot.app.user.repositories import UserRepository

ACCESS_TOKEN_SECRET = AUTH_SETTINGS.ACCESS_TOKEN_SECRET
REFRESH_TOKEN_SECRET = AUTH_SETTINGS.REFRESH_TOKEN_SECRET
SHORT_SESSION_LIFESPAN = AUTH_SETTINGS.SHORT_SESSION_LIFESPAN
LONG_SESSION_LIFESPAN = AUTH_SETTINGS.LONG_SESSION_LIFESPAN


# ... (상단 import 생략)

class AuthService:
    def __init__(
        self,
        auth_repository: Annotated[AuthRepository, Depends()],
        user_repository: Annotated[UserRepository, Depends()],
    ) -> None:
        self.auth_repository = auth_repository
        self.user_repository = user_repository

    # ✅ 변경: User 객체 전체가 아닌 user_id만 받도록 하여 객체 참조로 인한 Lazy Load 에러 방지
    def _issue_token_by_id(self, user_id: int) -> tuple[str, str]:
        access_token = issue_token(user_id, SHORT_SESSION_LIFESPAN, ACCESS_TOKEN_SECRET)
        refresh_token = issue_token(user_id, LONG_SESSION_LIFESPAN, REFRESH_TOKEN_SECRET)
        return access_token, refresh_token

    async def signin(self, email: str, password: str) -> tuple[str, str]:
        user = await self.user_repository.get_user_by_email(email)
        if user is None:
            raise InvalidAccountException()

        # user.local_account가 Lazy Loading이면 여기서 에러 발생 가능
        # Repository에서 selectinload/joinedload로 미리 가져오거나 ID를 사용해야 함
        verify_password(password, user.local_account.hashed_password)

        return self._issue_token_by_id(user.id)

    # ... (refresh_tokens, delete_token은 로직상 큰 문제 없음)

    async def handle_google_oauth2(self, token: dict) -> tuple[str, str]:
        user_info: dict = token.get("userinfo")  # type: ignore
        google_sub = user_info["sub"]
        email = user_info["email"]

        social_account = await self.user_repository.get_social_account_by_provider(
            "google", google_sub
        )
        
        if social_account is not None:
            return self._issue_token_by_id(social_account.user_id)

        email_user = await self.user_repository.get_user_by_email(email)
        if email_user is not None:
            await self.user_repository.create_social_account(
                email_user.id, "google", google_sub
            )
            return self._issue_token_by_id(email_user.id)

        new_user = await self.user_repository.create_user(email)
        await self.user_repository.create_social_account(
            new_user.id, "google", google_sub
        )
        return self._issue_token_by_id(new_user.id)