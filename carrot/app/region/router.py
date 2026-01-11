from typing import Annotated

from fastapi import APIRouter, Depends, status

from carrot.app.region.schemas import RegionResponse
from carrot.app.region.services import RegionService

region_router = APIRouter()


@region_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_regions(
    region_service: Annotated[RegionService, Depends()],
) -> list[RegionResponse]:
    all_regions = await region_service.get_all_regions()
    return [RegionResponse.model_validate(region) for region in all_regions]
