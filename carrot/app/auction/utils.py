import asyncio
from datetime import datetime

from carrot.app.auction.models import Auction, AuctionStatus, Bid

from carrot.app.auction.exceptions import (
    NotAllowedActionError,
    BidTooLowError,
    AuctionAlreadyFinishedError
)

async def check_auction_active(auction: Auction) -> None:
    if auction.status != AuctionStatus.ACTIVE:
        raise NotAllowedActionError()
    if auction.end_at <= datetime.now():
        raise AuctionAlreadyFinishedError()
    
async def check_bid_request(auction: Auction, bidder_id: str, bid_price: int) -> None:
    if auction.product.owner_id == bidder_id:
        raise NotAllowedActionError()
    if bid_price <= auction.current_price:
        raise BidTooLowError()