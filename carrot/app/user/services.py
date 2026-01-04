from typing import Annotated
from argon2 import PasswordHasher

from fastapi import Depends
from carrot.app.user.models import User, UserStatus
from carrot.app.user.repositories import UserRepository
from carrot.app.user.exceptions import EmailAlreadyExistsException
from carrot.app.user.schemas import UserOnboardingRequest, UserUpdateRequest
from carrot.common.exceptions import InvalidFormatException


class UserService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends()]) -> None:
        self.user_repository = user_repository

    def create_user(self, email: str, password: str) -> User:
        if self.user_repository.get_user_by_email(email):
            raise EmailAlreadyExistsException()

        hashed_password = PasswordHasher().hash(password)

        return self.user_repository.create_user(email, hashed_password)

    def onboard_user(self, request: UserOnboardingRequest, user: User) -> User:
        for key, value in request.model_dump(exclude_none=True).items():
            setattr(user, key, value)
        user.status = UserStatus.ACTIVE
        self.user_repository.update_user(user)
        return user

    def update_user(self, request: UserUpdateRequest, user: User) -> User:
        if not any(
            [request.nickname, request.region_id, request.profile_image, request.coin]
        ):
            raise InvalidFormatException()
        for key, value in request.model_dump(exclude_none=True).items():
            setattr(user, key, value)
        self.user_repository.update_user(user)
        return user

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.user_repository.get_user_by_id(user_id)
