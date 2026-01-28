from typing import List

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from carrot.app.product.models import Product
from carrot.app.auction.models import Auction


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_post(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def create_auction(self, product: Product, auction: Auction) -> Product:
        auction.product_id = product.id
        self.session.add(auction)
        await self.session.commit()
        await self.session.refresh(auction)
        return product

    async def update_post(self, product: Product) -> Product:
        merged = await self.session.merge(product)
        await self.session.commit()
        await self.session.refresh(merged)
        return merged

    async def get_post_by_product_id(self, product_id: str) -> Product:
        query = select(Product).where(Product.id == product_id)
        posts = await self.session.execute(query)
        return posts.scalars().one_or_none()

    async def get_posts_by_query(self, user_id: str, keyword: str, region_id: str) -> List[Product]:
        query = select(Product)

        if user_id:
            query = query.where(Product.owner_id == user_id)

        if keyword:
            search_pattern = f"%{keyword}%"
            query = query.where(
                or_(
                    Product.title.ilike(search_pattern),
                    Product.content.ilike(search_pattern)
                )
            )

        if region_id:
            query = query.where(Product.region_id == region_id)

        posts = await self.session.execute(query)
        return posts.scalars().all()

    async def get_posts_all(self) -> List[Product]:
        query = select(Product)
        posts = await self.session.execute(query)
        return posts.scalars().all()

    async def remove_post(self, product: Product):
        await self.session.delete(product)
        await self.session.commit()
