from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from carrot.db.connection import get_db_session
from carrot.app.region.models import Region
from carrot.app.region.schemas import RegionResponse

region_router = APIRouter()


@region_router.get("/", status_code=200, response_model=List[RegionResponse])
async def get_regions(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[RegionResponse]:
    result = await session.execute(select(Region))
    regions = result.scalars().all()
    return [RegionResponse.model_validate(region) for region in regions]
