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

    async def create_auction(self, product_id: str, starting_price: int, end_at: datetime) -> Auction:
        stmt = select(Auction).where(
            Auction.product_id == product_id,
            Auction.status == AuctionStatus.ACTIVE
        )
        result = await self.session.execute(stmt)
        active_auction = result.scalar_one_or_none()

        if active_auction:
            raise AuctionAlreadyExistsError
        
        new_auction = Auction(
            product_id=product_id,
            starting_price=starting_price,
            current_price=starting_price,
            end_at=end_at,
            status=AuctionStatus.ACTIVE
        )
        self.session.add(new_auction)
        await self.session.commit()
        await self.session.refresh(new_auction)
        return new_auction
    
    async def get_auction_by_id(self, auction_id: str) -> Optional[Auction]:
        stmt = (
            select(Auction)
            .where(Auction.id == auction_id)
            .options(joinedload(Auction.bids))
        )
        result = await self.session.execute(stmt)
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
    
    async def delete_auction(self, auction_id:str) -> None:
        stmt = select(Auction).where(Auction.id == auction_id)
        result = await self.session.execute(stmt)
        auction = result.scalar_one_or_none()

        if not auction:
            raise AuctionNotFoundError
        
        if auction.status != AuctionStatus.ACTIVE:
            raise NotAllowedActionError
        
        await self.session.delete(auction)
        await self.session.commit()

    async def update_auction_status(self, auction_id: str, new_status: AuctionStatus) -> None:
        stmt = select(Auction).where(Auction.id == auction_id)
        result = await self.session.execute(stmt)
        auction = result.scalar_one_or_none()

        if not auction:
            raise AuctionNotFoundError
        
        auction.status = new_status
        await self.session.commit()

class BidRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
        self.session = session

    async def place_bid(self, auction_id: str, bidder_id: str, bid_price: int) -> Bid:
        new_bid = Bid(
            auction_id=auction_id,
            bidder_id=bidder_id,
            bid_price=bid_price
        )
        self.session.add(new_bid)
        
        # Update auction's current price and bid count
        stmt = (
            update(Auction)
            .where(Auction.id == auction_id)
            .values(
                current_price=bid_price,
                bid_count=Auction.bid_count + 1
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.refresh(new_bid)
        return new_bid
    
    async def gets_user_bids(self, user_id: str) -> List[Bid]:
        stmt = (
            select(Bid)
            .where(Bid.bidder_id == user_id)
            .options(joinedload(Bid.auction).joinedload(Auction.product))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()