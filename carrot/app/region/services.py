from typing import Annotated

from fastapi import Depends

from carrot.app.region.exceptions import RegionAlreadyExistsException
from carrot.app.region.models import Region
from carrot.app.region.repositories import RegionRepository
from carrot.app.region.schemas import RegionResponse


class RegionService:
    def __init__(
        self, region_repository: Annotated[RegionRepository, Depends()]
    ) -> None:
        self.region_repository = region_repository

    async def create_region(self, name: str) -> Region:
        if await self.region_repository.get_region_by_name(name):
            raise RegionAlreadyExistsException()

        region = await self.region_repository.create_region(name)
        return region

    async def get_all_regions(self) -> list[Region]:
        return await self.region_repository.get_all_regions()
