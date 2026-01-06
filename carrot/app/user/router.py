from typing import Annotated

from fastapi import APIRouter, Depends

from carrot.app.auth.utils import login_with_header, partial_login_with_header
from carrot.app.user.models import User
from carrot.app.user.schemas import (
    UserOnboardingRequest,
    UserSignupRequest,
    UserUpdateRequest,
    UserResponse,
)
from carrot.app.user.services import UserService

user_router = APIRouter()


@user_router.post("/", status_code=201, response_model=UserResponse)
async def signup(
    signup_request: UserSignupRequest,
    user_service: Annotated[UserService, Depends()],
) -> UserResponse:
    user = await user_service.create_user(
        signup_request.email,
        signup_request.password,
    )
    return UserResponse.model_validate(user)


@user_router.get("/me", status_code=200, response_model=UserResponse)
async def get_me(
    user: Annotated[User, Depends(partial_login_with_header)],
) -> UserResponse:
    return UserResponse.model_validate(user)


@user_router.post("/me/onboard", status_code=200, response_model=UserResponse)
async def onboard_me(
    user: Annotated[User, Depends(partial_login_with_header)],
    request: UserOnboardingRequest,
    user_service: Annotated[UserService, Depends()],
) -> UserResponse:
    updated_user = await user_service.onboard_user(request=request, user=user)
    return UserResponse.model_validate(updated_user)


@user_router.patch("/me", status_code=200, response_model=UserResponse)
async def update_me(
    user: Annotated[User, Depends(login_with_header)],
    request: UserUpdateRequest,
    user_service: Annotated[UserService, Depends()],
) -> UserResponse:
    updated_user = await user_service.update_user(request=request, user=user)
    return UserResponse.model_validate(updated_user)
