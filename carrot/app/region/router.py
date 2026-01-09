from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from carrot.db.connection import get_db_session
from carrot.app.region.models import Region
from carrot.app.region.schemas import RegionResponse

region_router = APIRouter()

class GeoLocation(BaseModel):
    latitude: float
    longitude: float

@region_router.get("/", status_code=200, response_model=List[RegionResponse])
async def get_regions(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[RegionResponse]:
    result = await session.execute(select(Region))
    regions = result.scalars().all()
    return [RegionResponse.model_validate(region) for region in regions]

@region_router.post("/detect", status_code=200, response_model=RegionResponse)
async def detect_region(
    location: GeoLocation,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RegionResponse:
    """
    Detect user's region based on latitude and longitude.
    Currently implements a stub that returns a seeded region.
    """
    # TODO: Implement real reverse geocoding using external API (e.g. Kakao, Naver Map)
    # response = kakao_api.coord2address(location.longitude, location.latitude)
    # address = response['documents'][0]['address'] # Parsing logic needed
    
    # For now, return a default region (e.g., 역북동) to simulate detection
    stmt = select(Region).where(Region.dong == '역북동')
    result = await session.execute(stmt)
    region = result.scalars().first()
    
    if not region:
        # Fallback to any region if '역북동' is not seeded yet
        stmt = select(Region).limit(1)
        result = await session.execute(stmt)
        region = result.scalars().first()
    
    if not region:
        raise HTTPException(status_code=404, detail="No service regions found.")
        
    return RegionResponse.model_validate(region)

