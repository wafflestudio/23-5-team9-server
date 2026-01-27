from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from carrot.db.connection import get_db_session
from carrot.app.auth.utils import login_with_header

from repositories import AuctionRepository, BidRepository
from schemas import AuctionCreate, BidCreate, AuctionResponse # Pydantic 모델 가정

auction_router = APIRouter()

# 1. 경매 등록
@auction_router.post("", response_model=AuctionResponse)
async def create_new_auction(
    data: AuctionCreate, 
    db: AsyncSession = Depends(get_db_session)
):
    repo = AuctionRepository(db)
    try:
        auction = await repo.create_auction(
            product_id=data.product_id,
            start_price=data.start_price,
            end_at=data.end_at
        )
        return auction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 2. 경매 목록 조회 (필터링 포함)
@auction_router.get("")
async def list_active_auctions(
    category_id: Optional[str] = None,
    region_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    repo = AuctionRepository(db)
    return await repo.get_active_auctions(category_id, region_id)

# 3. 입찰하기
@auction_router.post("/{auction_id}/bids")
async def place_a_bid(
    auction_id: str,
    data: BidCreate,
    current_user_id: str = Depends(login_with_header), # 인증 로직 가정
    db: AsyncSession = Depends(get_db_session)
):
    repo = BidRepository(db)
    try:
        bid = await repo.place_bid(
            auction_id=auction_id,
            bidder_id=current_user_id,
            amount=data.amount
        )
        return {"status": "success", "current_bid": bid.bid_amount}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))