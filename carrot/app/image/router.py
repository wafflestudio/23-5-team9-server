# from typing import Annotated

# from fastapi import APIRouter, Depends

# from carrot.app.auth.utils import login_with_header, partial_login_with_header
# from carrot.app.user.models import User
# from carrot.app.image.schemas import (
#     ProductImageRequest,
#     UserImageRequest,
#     ProductImageResponse,
#     UserImageResponse,
# )
# from carrot.app.image.services import ImageService

# image_router = APIRouter()


# @image_router.post("/me", status_code=201, response_model=ProductImageResponse)
# async def upload_product_image(
#     user: Annotated[User, Depends(login_with_header)],
#     request: ProductImageRequest,
#     service: Annotated[ImageService, Depends()],
# ) -> ProductImageResponse:
#     image = await service.upload_product_image(
#         request.image_url,
#     )
#     return ProductImageResponse.model_validate(image)

# @image_router.post("/me", status_code=201, response_model=UserImageResponse)
# async def upload_profile_image(
#     user: Annotated[User, Depends(login_with_header)],
#     request: UserImageRequest,
#     service: Annotated[ImageService, Depends()],
# ) -> UserImageResponse:
#     image = await service.upload_profile_image(
#         user.id,
#         request.image_url
#     )
#     return UserImageResponse.model_validate(image)