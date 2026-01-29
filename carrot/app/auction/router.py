from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from carrot.db.connection import get_db_session
from carrot.app.auth.utils import login_with_header

from carrot.app.auction.services import AuctionService
from carrot.app.auction.schemas import AuctionListResponse, AuctionResponse, BidCreate, BidResponse # Pydantic 모델 가정

from carrot.app.user.models import User

auction_router = APIRouter()

@auction_router.post("/{auction_id}/bids", response_model=BidResponse)
async def place_bid(
    auction_id: str,
    bid_data: BidCreate,
    bidder: Annotated[User, Depends(login_with_header)],
    service: Annotated[AuctionService, Depends()],
) -> BidResponse:

    bid = await service.place_bid(
        auction_id=auction_id,
        bidder_id=bidder.id,
        bid_price=bid_data.bid_price
    )

    return BidResponse.model_validate(bid)