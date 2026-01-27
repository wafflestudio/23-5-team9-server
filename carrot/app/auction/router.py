from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated

from carrot.db.connection import get_db_session
from carrot.app.auth.utils import login_with_header

from carrot.app.auction.services import AuctionService
from carrot.app.auction.schemas import AuctionCreate, AuctionResponse # Pydantic 모델 가정

from carrot.app.user.models import User

from carrot.app.product.schemas import ProductPostRequest

auction_router = APIRouter()

# 1. 경매 등록
@auction_router.post("/", response_model=AuctionResponse)
async def create_new_auction(
    owner: Annotated[User, Depends(login_with_header)],
    product_data: ProductPostRequest,
    auction_data: AuctionCreate,
    service: Annotated[AuctionService, Depends()],
) -> AuctionResponse:
    auction = await service.create_auction_with_product(
        owner_id=owner.id,
        region_id=owner.region_id,
        product_data=product_data,
        auction_data=auction_data
    )
    return AuctionResponse.model_validate(auction)