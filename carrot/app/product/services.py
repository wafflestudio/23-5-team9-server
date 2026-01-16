from typing import Annotated

from fastapi import Depends

from carrot.app.user.schemas import UserOnboardingRequest, UserUpdateRequest
from carrot.app.product.models import Product, UserProduct
from carrot.app.product.repositories import ProductRepository
from carrot.app.product.exceptions import NotYourProductException, InvalidProductIDException
from carrot.common.exceptions import InvalidFormatException
# from carrot.app.image.models import ProductImage

class ProductService:
    def __init__(self, product_repository: Annotated[ProductRepository, Depends()]) -> None:
        self.repository = product_repository

    async def create_post(self, user_id: str, title: str, content: str, price: int, category_id: str) -> Product:
        # image_objects = [ProductImage(image_url=img_url) for img_url in images]
        product = Product(
            owner_id = user_id,
            title = title,
            # images = image_objects,
            content = content,
            price = price,
            category_id = category_id,
        )
        
        new = await self.repository.create_post(product)
        return new

    async def update_post(self, user_id: str, id: str, title: str, content: str, price: int, category_id: str) -> Product:
        product = await self.repository.get_post_by_id(id)

        if product is None:
            raise InvalidProductIDException
        
        if user_id != product.owner_id:
            raise NotYourProductException
        if title is not None:
            product.title = title
        # if images is not None:
        #     image_objects = [ProductImage(image_url=img_url) for img_url in images]
        #     product.images = image_objects
        if content is not None:
            product.content = content
        if price is not None:
            product.price = price
        if category_id is not None:
            product.category_id = category_id
        
        updated = await self.repository.update_post(product)
        return updated
    
    async def view_post(self, id: str):
        product = await self.repository.get_post_by_id(id)
        if product is None:
            raise InvalidProductIDException
        
    async def view_post_all(self):
        products = await self.repository.get_post_all()
        if products is None:
            raise InvalidProductIDException
        
        return products
    
    async def remove_post(self, id: str):
        product = await self.repository.get_post_by_id(id)
        if product is None:
            raise InvalidProductIDException
        
        await self.repository.remove_post(product)
        return product