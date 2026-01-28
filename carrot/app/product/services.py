from typing import Annotated

from fastapi import Depends

from carrot.app.user.schemas import UserOnboardingRequest, UserUpdateRequest
from carrot.app.product.models import Product, UserProduct
from carrot.app.product.repositories import ProductRepository
from carrot.app.product.exceptions import NotYourProductException, InvalidProductIDException
from carrot.app.image.services import ImageService
from carrot.common.exceptions import InvalidFormatException

class ProductService:
    def __init__(self, product_repository: Annotated[ProductRepository, Depends()], image_service: Annotated[ImageService, Depends()]) -> None:
        self.repository = product_repository
        self.image_service = image_service

    async def create_post(self, user_id: str, title: str, image_ids: list, content: str, price: int, category_id: str, region_id: str) -> Product:
        product = Product(
            owner_id = user_id,
            title = title,
            image_ids = image_ids,
            content = content,
            price = price,
            category_id = category_id,
            region_id = region_id,
        )
        
        new = await self.repository.create_post(product)
        return new

    async def update_post(self, user_id: str, id: str, title: str, image_ids: list, content: str, price: int, category_id: str, region_id: str) -> Product:
        product = await self.repository.get_post_by_product_id(id)

        if product is None:
            raise InvalidProductIDException
        
        if user_id != product.owner_id:
            raise NotYourProductException
        
        product.title = title
        product.image_ids = image_ids
        product.content = content
        product.price = price
        product.category_id = category_id
        product.region_id = region_id
        
        updated = await self.repository.update_post(product)
        return updated
    
    async def view_post_by_product_id(self, product_id: str):
        product = await self.repository.get_post_by_product_id(product_id)
        
        if product is None:
            raise InvalidProductIDException
        
        return product
    
    async def view_posts_by_query(self, user_id: str | None, keyword: str | None, region_id: str | None):
        products = await self.repository.get_posts_by_query(user_id, keyword, region_id)
        
        return products
    
    async def view_posts_all(self):
        products = await self.repository.get_posts_all()
        
        return products
    
    async def remove_post(self, user_id: str, product_id: str):
        product = await self.repository.get_post_by_product_id(product_id)
        
        if product is None:
            raise InvalidProductIDException
        
        if user_id != product.owner_id:
            raise NotYourProductException
        
        image_ids = product.image_ids
        for id in image_ids:
            await self.image_service.remove_product_image(id)
            
        await self.repository.remove_post(product)