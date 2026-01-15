from typing import Annotated

from fastapi import Depends

from carrot.app.user.schemas import UserOnboardingRequest, UserUpdateRequest
from carrot.app.image.models import ProductImage
from carrot.app.image.repositories import ImageRepository
from carrot.common.exceptions import InvalidFormatException

class ImageService:
    def __init__(self, image_repository: Annotated[ImageRepository, Depends()]) -> None:
        self.repository = image_repository

    async def upload_product_image(self, url: str, product_id: str) -> ProductImage:
        image = ProductImage(
            image_url = url,
            product_id = product_id
        )
        
        new = await self.repository.upload_product_image(image)
        return new
    
    # async def upload_profile_image(self, user_id: str, url: str) -> UserImage:
    #     image = UserImage(
    #         image_url = url,
    #         user_id = user_id
    #     )
        
    #     new = await self.repository.upload_profile_image(image)
    #     return new