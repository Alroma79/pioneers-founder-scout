import os
import logging
from typing import List, Dict, Any
import httpx
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

HARVEST_API_KEY = os.getenv("HARVEST_API_KEY")
HARVEST_BASE_URL = os.getenv("HARVEST_BASE_URL", "https://api.harvest-api.com")


class HarvestClient:
    def __init__(self) -> None:
        if HARVEST_API_KEY:
            # HarvestAPI uses X-API-Key header
            self.headers = {
                "X-API-Key": HARVEST_API_KEY,
                "Content-Type": "application/json"
            }
        else:
            self.headers = {}

    async def search_people(
        self,
        search: str = "",
        title: str = "",
        location: str = "",
        geo_id: str = "",
        page: int = 1,
        limit: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Calls HarvestAPI /linkedin/profile-search
        - search: free-text keyword(s)
        - title: job title filter
        - location: text-based location (fallback if geo_id is empty)
        - geo_id: preferred Harvest geoId for precise location
        """
        if not HARVEST_API_KEY:
            logger.error("HARVEST_API_KEY missing")
            return []

        url = f"{HARVEST_BASE_URL}/linkedin/profile-search"
        params: Dict[str, Any] = {"page": str(page)}
        if search:
            params["search"] = search
        if title:
            params["title"] = title
        if geo_id:
            params["geoId"] = geo_id
        elif location:
            params["location"] = location

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.get(url, params=params, headers=self.headers)
                logger.debug(f"Harvest API response: {r.status_code}")
                r.raise_for_status()
                data = r.json()
                results = data.get("elements", [])[:limit]
                logger.info(f"Harvest returned {len(results)} results", extra={
                    'url': url, 'params': params, 'status': r.status_code
                })
                return results
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.error(f"Harvest API error", extra={
                'url': url, 'params': params, 'error': str(e)
            })
            return []

    async def lookup_geo_id(self, search: str) -> str:
        """
        Resolve a text location into a geoId using /linkedin/geo-id-search.
        Example: "Lisbon" -> geoId "100509491"
        """
        if not HARVEST_API_KEY:
            return ""

        url = f"{HARVEST_BASE_URL}/linkedin/geo-id-search"
        params = {"search": search}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.get(url, params=params, headers=self.headers)
                logger.debug(f"GeoID lookup response: {r.status_code} for {search}")
                r.raise_for_status()
                data = r.json()
                els = data.get("elements", [])
                geo_id = els[0].get("geoId", "") if els else ""
                logger.info(f"GeoID lookup: '{search}' -> '{geo_id}'")
                return geo_id
        except Exception as e:
            logger.error(f"GeoID lookup failed for '{search}'", extra={'error': str(e)})
            return ""
