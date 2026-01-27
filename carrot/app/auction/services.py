from typing import List, Annotated

from fastapi import Depends

from carrot.app.auction.models import Auction, AuctionStatus, Bid
from carrot.app.auction.schemas import AuctionCreate
from carrot.app.auction.repositories import AuctionRepository
from carrot.app.auction.exceptions import AuctionAlreadyExistsError

from carrot.app.product.models import Product
from carrot.app.product.schemas import ProductPostRequest

class AuctionService:
    def __init__(self, auction_repository: Annotated[AuctionRepository, Depends()]) -> None:
        self.repository = auction_repository

    async def create_auction_with_product(self, owner_id: str, region_id: str, product_data: ProductPostRequest, auction_data: AuctionCreate) -> Auction:
        product = Product(
            owner_id=owner_id,
            title=product_data.title,
            image_ids=product_data.image_ids,
            content=product_data.content,
            price=product_data.price,
            category_id=product_data.category_id,
            region_id=region_id,
        )
        
        auction = Auction(
            starting_price=auction_data.starting_price,
            current_price=auction_data.starting_price,
            end_at=auction_data.end_at,
            status=AuctionStatus.ACTIVE
        )

        return await self.repository.create_auction(product, auction)
    
    async def list_auctions(self, category_id: str | None = None, region_id: str | None = None) -> List[Auction]:
        return await self.repository.get_active_auctions(category_id, region_id)