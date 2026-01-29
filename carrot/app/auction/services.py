from datetime import datetime, timezone
from typing import List, Annotated

from fastapi import Depends
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from carrot.app.auction.models import Auction, AuctionStatus, Bid
from carrot.app.auction.schemas import AuctionCreate
from carrot.app.auction.repositories import AuctionRepository
from carrot.db.connection import get_session_factory

from carrot.app.auction.exceptions import (
    AuctionAlreadyExistsError, 
    AuctionNotFoundError, 
    NotAllowedActionError,
    AuctionAlreadyFinishedError
)

from carrot.app.auction.utils import (
    check_auction_active,
    check_bid_request
)

class AuctionService:
    def __init__(self, session : AsyncSession = Depends(get_session_factory)):
        self.repository = AuctionRepository(session)
        self.session = session

    async def place_bid(self, auction_id: str, bidder_id: str, bid_price: int) -> Bid:
        auction = await self.repository.get_auction_by_id(auction_id)

        if auction is None:
            raise AuctionNotFoundError()
        
        await check_auction_active(auction)
        await check_bid_request(auction, bidder_id, bid_price)

        new_bid = Bid(
            auction_id=auction_id,
            bidder_id=bidder_id,
            bid_price=bid_price
        )
        await self.repository.add_bid_without_commit(new_bid)

        auction.current_price = bid_price
        auction.bid_count += 1
        await self.repository.update_auction_without_commit(auction)

        await self.db_session.commit()
        await self.db_session.refresh(new_bid)
        await self.db_session.refresh(auction)
        return new_bid