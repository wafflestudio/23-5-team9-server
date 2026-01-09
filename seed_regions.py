import asyncio
import sys
import os
import uuid

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from carrot.db.connection import get_db_session, db
from carrot.app.region.models import Region
from sqlalchemy import select

REGIONS = [
    {"name": "강남구"},
    {"name": "서초구"},
    {"name": "송파구"},
]

async def seed_regions():
    try:
        async for session in get_db_session():
            print("Checking existing regions...")
            result = await session.execute(select(Region))
            existing = result.scalars().all()
            existing_names = {r.name for r in existing}
            
            for region_data in REGIONS:
                if region_data["name"] not in existing_names:
                    new_region = Region(name=region_data["name"])
                    session.add(new_region)
                    print(f"Adding region: {region_data['name']}")
                else:
                    print(f"Region already exists: {region_data['name']}")
            
            await session.commit()
            
            # Print all regions
            result = await session.execute(select(Region))
            all_regions = result.scalars().all()
            print("\nAll Regions in DB:")
            for r in all_regions:
                print(f"ID: {r.id}, Name: {r.name}")
    finally:
        # Close the DB connection pool to prevent "Event loop is closed" error
        await db.engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_regions())
