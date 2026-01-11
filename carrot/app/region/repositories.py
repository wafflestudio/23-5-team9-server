from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from carrot.app.region.models import Region
from carrot.db.connection import get_db_session


class RegionRepository:
    def __init__(
        self, session: Annotated[AsyncSession, Depends(get_db_session)]
    ) -> None:
        self.session = session

    async def create_region(self, name: str) -> Region:
        region = Region(name=name)
        self.session.add(region)
        await self.session.flush()
        return region

    async def get_region_by_name(self, name: str) -> Region | None:
        return await self.session.scalar(select(Region).where(Region.name == name))

    async def get_all_regions(self) -> list[Region]:
        result = await self.session.scalars(select(Region))
        return list(result.all())
