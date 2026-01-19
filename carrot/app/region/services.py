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

    async def get_region_by_id(self, id: str) -> Region | None:
        return await self.region_repository.get_region_by_id(id=id)

    async def get_all_sido(self) -> list[str]:
        return await self.region_repository.get_all_sido()

    async def get_all_sigugun(self, sido_nm: str) -> list[str]:
        return await self.region_repository.get_all_sigugun(sido=sido_nm)

    async def get_all_dong(self, sido_nm: str, sigugun_nm: str) -> list[dict[str, str]]:
        return await self.region_repository.get_all_dong(
            sido=sido_nm, sigugun=sigugun_nm
        )
