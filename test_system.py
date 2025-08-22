#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('backend')
from backend.app.clients.harvest_client import HarvestClient

async def test():
    client = HarvestClient()
    geo_id = await client.lookup_geo_id('Portugal')
    print(f'Portugal geo_id: {geo_id}')
    
    results = await client.search_people(search='founder', limit=5)
    print(f'Search results: {len(results)}')
    if results:
        print(f'First result: {results[0].get("name", "N/A")}')

if __name__ == "__main__":
    asyncio.run(test())
