from typing import Literal

import httpx
from google.transit import gtfs_realtime_pb2


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
            headers={
                "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjNiMDk1NzQ3YmY4MzMxZWE0YWQ1M2YzNzBjNjMyNjAxNzliMGQyM2EiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiTWFydCIsInBpY3R1cmUiOiJodHRwczovL2F2YXRhcnMuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3UvOTM0MjM3ODk_dj00IiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL21vYmlsaXR5LWZlZWRzLXByb2QiLCJhdWQiOiJtb2JpbGl0eS1mZWVkcy1wcm9kIiwiYXV0aF90aW1lIjoxNzc2Nzc5MjMyLCJ1c2VyX2lkIjoiOXY0bkFjNHlNMmFGUGZ6Qk5ndUdkNGhsUUtIMiIsInN1YiI6Ijl2NG5BYzR5TTJhRlBmekJOZ3VHZDRobFFLSDIiLCJpYXQiOjE3NzY3ODEyMzksImV4cCI6MTc3Njc4NDgzOSwiZW1haWwiOiJtZUBtNHJ0Lm5sIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZ2l0aHViLmNvbSI6WyI5MzQyMzc4OSJdLCJlbWFpbCI6WyJtZUBtNHJ0Lm5sIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ2l0aHViLmNvbSJ9fQ.XN-5IL4r9-P5eyNDE72nYJTmQUGBI6Ro4DgVJrZtkO3wGhUiWSPqMX8CC7b0-0xFJLza6XFscSZvtNsOgNe0jJ3a8mPkE7nrbDgNEYOzMmB0AeKhj92SZOXdzzh80NaZqWPErmeZO_KvICNf4J60P1k66nOqmCUPQ3BdrNA671KtPrbw9DOFnNRTIwNj1hhoDqyG3sT58mL532EIUxDrsv_NPRgvyPM76-MFsAtB4PggNmYlKsVBXHD_pgRpttUEEYu2IsTl6-msQM2eohW1PaUqGCfyzAw-eJKaSk7EhgyjGY7R8eA0wNJaSE6KJqOVLB2lnWhy_Lca28xtxELv1w"
            },
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
