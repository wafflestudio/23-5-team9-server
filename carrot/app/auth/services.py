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


class AuthService:
    def __init__(
        self,
        auth_repository: Annotated[AuthRepository, Depends()],
        user_repository: Annotated[UserRepository, Depends()],
    ) -> None:
        self.auth_repository = auth_repository
        self.user_repository = user_repository

    def _issue_token(self, user: User) -> tuple[str, str]:
        access_token = issue_token(user.id, SHORT_SESSION_LIFESPAN, ACCESS_TOKEN_SECRET)
        refresh_token = issue_token(
            user.id, LONG_SESSION_LIFESPAN, REFRESH_TOKEN_SECRET
        )

        return access_token, refresh_token

    def signin(self, email: str, password: str) -> tuple[str, str]:
        user = self.user_repository.get_user_by_email(email)
        if user is None:
            raise InvalidAccountException()

        verify_password(password, user.local_account.hashed_password)

        return self._issue_token(user)

    def block_refresh_token(self, token: str, exp: datetime) -> None:
        self.auth_repository.block_refresh_token(token, exp)

    def refresh_tokens(self, authorization: str | None) -> tuple[str, str]:
        if authorization is None:
            raise UnauthenticatedException()
        token = get_token_from_authorization_header(authorization)

        # check if refresh token is already blocked
        blocked_token = self.auth_repository.get_blocked_token(token)
        if blocked_token != None:
            raise RevokedTokenException()

        claims = verify_and_decode_token(token, REFRESH_TOKEN_SECRET)

        exp = claims.get("exp", None)
        if exp is None:
            raise InvalidTokenException()
        exp_datetime = datetime.fromtimestamp(exp)

        self.block_refresh_token(token, exp_datetime)

        user_id = claims.get("sub", None)
        if user_id is None:
            raise InvalidTokenException()
        access_token = issue_token(user_id, SHORT_SESSION_LIFESPAN, ACCESS_TOKEN_SECRET)
        refresh_token = issue_token(
            user_id, LONG_SESSION_LIFESPAN, REFRESH_TOKEN_SECRET
        )
        return access_token, refresh_token

    def delete_token(self, authorization: str | None) -> None:
        if authorization is None:
            raise UnauthenticatedException()
        token = get_token_from_authorization_header(authorization)

        # check if refresh token is already blocked
        blocked_token = self.auth_repository.get_blocked_token(token)
        if blocked_token != None:
            raise RevokedTokenException()

        claims = verify_and_decode_token(token, REFRESH_TOKEN_SECRET)

        exp = claims.get("exp", None)
        if exp is None:
            raise InvalidTokenException()
        exp_datetime = datetime.fromtimestamp(exp)
        self.block_refresh_token(token, exp_datetime)

    def handle_google_oauth2(self, token: dict) -> tuple[str, str]:
        user_info: dict = token.get("userinfo")  # type: ignore
        google_sub = user_info["sub"]
        email = user_info["email"]

        # sub에 대응하는 social account 혹은 email에 대응하는 user가 있는 경우 로그인
        social_account = self.user_repository.get_social_account_by_provider(
            "google", google_sub
        )
        if social_account != None:
            return self._issue_token(social_account.user)

        email_user = self.user_repository.get_user_by_email(email)
        if email_user != None:
            self.user_repository.create_social_account(
                email_user.id, "google", google_sub
            )
            return self._issue_token(email_user)

        # 아닌 경우 계정 생성
        new_user = self.user_repository.create_user(email)
        new_social = self.user_repository.create_social_account(
            new_user.id, "google", google_sub
        )
        return self._issue_token(new_user)
