import asyncio
import sys
import os
import httpx
import json
from sqlalchemy import select

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from carrot.db.connection import get_db_session, db
from carrot.app.region.models import Region

# URL for South Korea Administrative Divisions (Hangjeong-dong)
# Using vuski's repository which is a standard source for this data.
GEOJSON_URL = "https://raw.githubusercontent.com/vuski/admdongkor/master/ver20250101/HangJeongDong_ver20250101.geojson"

async def fetch_regions():
    print(f"Fetching region data from {GEOJSON_URL}...")
    async with httpx.AsyncClient() as client:
        response = await client.get(GEOJSON_URL)
        response.raise_for_status()
        return response.json()

def parse_regions(geojson_data):
    regions = []
    features = geojson_data.get('features', [])
    
    print(f"Parsing {len(features)} regions...")
    
    for feature in features:
        props = feature.get('properties', {})
        
        sido = props.get('sidonm')
        sigugun = props.get('sggnm')
        full_name = props.get('adm_nm', '')
        
        if not sido or not full_name:
            continue
            
        # Extract Dong from full_name
        # format: "Sido Sigugun Dong" or "Sido Dong" (for Sejong sometimes)
        parts = full_name.split()
        dong = parts[-1] 
        
        # Handle cases where sigugun might be empty (e.g., Sejong)
        if not sigugun:
            if "세종" in sido:
                sigugun = "세종시" 
            else:
                # Fallback: try to guess or skip if invalid
                # If full_name has 2 parts "Sido Dong", sigugun is empty.
                # Use Sido as Sigugun or "" if allowed? DB says Not Null.
                sigugun = sido # Best effort fallback
        
        # Ensure we have valid strings
        regions.append({
            "sido": sido,
            "sigugun": sigugun,
            "dong": dong
        })
        
    return regions

async def seed_regions():
    try:
        # 1. Fetch and Parse
        data = await fetch_regions()
        new_regions_data = parse_regions(data)
        
        # 2. Seed to DB
        async for session in get_db_session():
            print("Checking existing regions in DB...")
            # Fetch all existing keys (sido, sigugun, dong) to minimize queries
            # Warning: Loading all might be heavy if DB is huge, but for ~3500 it's fine.
            result = await session.execute(select(Region))
            existing = result.scalars().all()
            existing_keys = {(r.sido, r.sigugun, r.dong) for r in existing}
            
            print(f"Found {len(existing_keys)} existing regions.")
            
            added_count = 0
            for r_data in new_regions_data:
                key = (r_data["sido"], r_data["sigugun"], r_data["dong"])
                if key not in existing_keys:
                    session.add(Region(
                        sido=r_data["sido"],
                        sigugun=r_data["sigugun"],
                        dong=r_data["dong"]
                    ))
                    existing_keys.add(key) # Add to set to prevent duplicates within this batch
                    added_count += 1
            
            if added_count > 0:
                print(f"Committing {added_count} new regions...")
                await session.commit()
                print("Commit complete.")
            else:
                print("No new regions to add.")
            
    except Exception as e:
        print(f"Error seeding regions: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the DB connection pool to prevent "Event loop is closed" error
        await db.engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_regions())
