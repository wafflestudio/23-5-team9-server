from typing import Annotated, List

from fastapi import Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from carrot.app.user.models import LocalAccount, SocialAccount, User
from carrot.app.product.models import Product
from carrot.db.connection import get_db_session


class ProductRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
        self.session = session

    async def create_post(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update_post(self, product: Product) -> Product:
        merged = self.session.merge(product)
        await self.session.commit()
        await self.session.refresh(merged)
        return merged
    
    async def remove_post(self, product: Product):
        await self.session.delete(product)
        await self.session.commit()
    
    async def get_post_by_id(self, id: str) -> Product:
        post = await self.session.get(Product, id)
        return post
    
    async def get_post_all(self) -> List[Product]:
        query = select(Product)
        posts = await self.session.execute(query)
        
        return posts.scalars().all()