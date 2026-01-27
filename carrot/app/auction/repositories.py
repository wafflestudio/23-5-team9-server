from typing import Annotated, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from datetime import datetime
from fastapi import Depends

from carrot.app.auction.models import Auction, Bid, AuctionStatus
from carrot.app.product.models import Product
from carrot.db.connection import get_db_session

from carrot.app.auction.exceptions import (
    AuctionAlreadyExistsError,
    AuctionNotFoundError,
    NotAllowedActionError
)

class AuctionRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
        self.session = session

    async def create_auction(self, product: Product, auction: Auction) -> Auction:
        self.session.add(product)
        await self.session.flush()  # Ensure product ID is generated

        auction.product_id = product.id
        self.session.add(auction)
        
        await self.session.commit()
        await self.session.refresh(auction)
        return auction
    
    async def get_auction_by_id(self, auction_id: str) -> Optional[Auction]:
        stmt = (
            select(Auction)
            .where(Auction.id == auction_id)
            .options(joinedload(Auction.bids))
        )
        result = await self.session.execute(stmt)

        if not result:
            raise AuctionNotFoundError
        
        return result.scalar_one_or_none()
    
    async def get_active_auctions(
            self,
            category_id: Optional[str] = None,
            region_id: Optional[str] = None
    )-> List[Auction]:
        stmt = (
            select(Auction)
            .where(Auction.status == AuctionStatus.ACTIVE)
            .options(selectinload(Auction.product))
        )

        if category_id:
            stmt = stmt.join(Auction.product).where(Product.category_id == category_id)
        
        if region_id:
            stmt = stmt.join(Auction.product).where(Product.region_id == region_id)
        
        stmt = stmt.options(contains_eager(Auction.product))

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_auction(self, auction: Auction) -> None:
        await self.session.delete(auction)
        await self.session.commit()

    async def update_auction_status(self, auction: Auction) -> Auction:
        merged = await self.session.merge(auction)
        await self.session.commit()
        await self.session.refresh(merged)
        return merged

class BidRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
        self.session = session

    async def place_bid(self, bid: Bid) -> Bid:
        self.session.add(bid)
        await self.session.commit()
        await self.session.refresh(bid)
        return bid

    async def update_bid(self, bid: Bid) -> Bid:
        merged = await self.session.merge(bid)
        await self.session.commit()
        await self.session.refresh(merged)
        return merged

    async def gets_user_bids(self, user_id: str) -> List[Bid]:
        stmt = (
            select(Bid)
            .where(Bid.bidder_id == user_id)
            .options(joinedload(Bid.auction).joinedload(Auction.product))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()