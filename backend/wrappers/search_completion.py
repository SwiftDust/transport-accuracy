from typing import Literal

import httpx
from google.transit import gtfs_realtime_pb2
from helpers.refresh_token import refresh_token

access_token = refresh_token().get("access_token")


async def resolve_url(client: httpx.AsyncClient, url: str) -> str:
    resp = await client.head(url, follow_redirects=True)
    return str(resp.url)


async def find_feeds(search_query: str, data_type: Literal["gtfs", "gtfs_rt"]):
    """data_type = 'gtfs' for static, 'gtfs_rt' for realtime"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.mobilitydatabase.org/v1/search",
            params={
                "limit": 20,
                "search_query": search_query,
                "data_type": data_type,
                "status": "active",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if resp.status_code != 200:
            print(f"error: status {resp.status_code}")
            print(f"{resp.text}")
            return []

        try:
            data = resp.json()
            feeds = data.get("results", [])
        except ValueError as e:
            print(f"failed to parse JSON response: {e}")
            print(f" {resp.text}")
            return []

        results = []
        for f in feeds:
            if "tu" not in f.get("entity_types", []):
                continue
            rt_url = f.get("source_info", {}).get("producer_url")
            if rt_url:
                rt_url = await resolve_url(client, rt_url)
            results.append(
                {
                    "id": f.get("id"),
                    "provider_name": f.get("provider"),
                    "feed_name": f.get("feed_name"),
                    "rt_url": rt_url,
                    "location": f.get("locations", [{}])[0].get("country"),
                    # "static_url": f.get("latest_dataset", {}).get("hosted_url"),
                }
            )
        return results
