from typing import Annotated

from fastapi import Depends
from sqlalchemy import and_, select
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

    async def get_region_by_id(self, id: str) -> Region | None:
        return await self.session.scalar(select(Region).where(Region.id == id))

    async def get_all_sido(self) -> list[str]:
        result = await self.session.scalars(
            select(Region.sido).distinct().order_by(Region.sido)
        )
        return list(result.all())

    async def get_all_sigugun(self, sido: str) -> list[str]:
        result = await self.session.scalars(
            select(Region.sigugun)
            .where(Region.sido == sido)
            .distinct()
            .order_by(Region.sigugun)
        )
        return list(result.all())

    async def get_all_dong(self, sido: str, sigugun: str) -> list[dict[str, str]]:
        result = await self.session.execute(
            select(Region.id, Region.dong)
            .where(and_(Region.sido == sido, Region.sigugun == sigugun))
            .distinct()
            .order_by(Region.dong)
        )

        return [dict(row) for row in result.mappings()]
