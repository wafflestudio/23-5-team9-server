import asyncio
import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from carrot.db.connection import get_db_session
from sqlalchemy import text

async def check_regions():
    async for session in get_db_session():
        result = await session.execute(text("SELECT id, name FROM region"))
        regions = result.fetchall()
        print("Existing regions:")
        for r in regions:
            print(f"ID: {r.id}, Name: {r.name}")
        
        if not regions:
            print("No regions found.")

if __name__ == "__main__":
    asyncio.run(check_regions())
