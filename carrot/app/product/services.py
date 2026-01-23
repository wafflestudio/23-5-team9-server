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
        product = await self.repository.get_post_by_product_id(id)

        if product is None:
            raise InvalidProductIDException
        
        if user_id != product.owner_id:
            raise NotYourProductException
        
        product.title = title
        # image_objects = [ProductImage(image_url=img_url) for img_url in images]
        # product.images = image_objects
        product.content = content
        product.price = price
        product.category_id = category_id
        
        updated = await self.repository.update_post(product)
        return updated
    
    async def view_post_by_product_id(self, product_id: str):
        product = await self.repository.get_post_by_product_id(product_id)
        
        if product is None:
            raise InvalidProductIDException
        
        return product
    
    async def view_posts_by_query(self, user_id: str | None, keyword: str | None, region_id: str | None):
        products = await self.repository.get_posts_by_query(keyword)
        
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
        
        await self.repository.remove_post(product)