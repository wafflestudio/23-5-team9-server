from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlalchemy import func

# 경매 상태 Enum (모델과 맞춤)
class AuctionStatus(str, Enum):
    ACTIVE = "active"
    FINISHED = "finished"
    FAILED = "failed"
    CANCELED = "canceled"

# --- 입찰 (Bid) 스키마 ---
class BidBase(BaseModel):
    amount: int = Field(..., gt=0, description="입찰 금액은 0보다 커야 합니다.")

class BidCreate(BidBase):
    pass

class BidResponse(BidBase):
    id: str
    auction_id: str
    bidder_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- 경매 (Auction) 스키마 ---
class AuctionBase(BaseModel):
    start_price: int = Field(..., ge=0)
    end_at: datetime

    @field_validator("end_at")
    @classmethod
    def check_future_date(cls, v: datetime):
        if v <= func.now():
            raise ValueError("마감 시간은 현재 시간보다 미래여야 합니다.")
        return v

class AuctionCreate(AuctionBase):
    product_id: str

class AuctionResponse(AuctionBase):
    id: str
    product_id: str
    current_bid: int
    bid_count: int
    status: AuctionStatus
    
    # 관계된 데이터 (필요 시 포함)
    # product: Optional[ProductResponse] 
    
    class Config:
        from_attributes = True

# --- 상품 상세 조회 시 경매 정보를 포함하기 위한 스키마 ---
class AuctionInProduct(BaseModel):
    id: str
    current_bid: int
    end_at: datetime
    status: AuctionStatus

    class Config:
        from_attributes = True