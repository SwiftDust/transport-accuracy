import asyncio
import json
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

from cachetools import TTLCache
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from helpers.average_delay import average_delay
from helpers.calculate_ontime import amount, percentage
from httpx import URL
from wrappers.fetch_trip_updates import realtime
from wrappers.search_completion import find_feeds


@dataclass
class DelayData:
    """Represents realtime delay statistics for a time period"""

    avg_delay: float
    on_time: int
    on_time_percentage: float


@dataclass
class Feed:
    id: str
    location: str
    rt_url: str


app = FastAPI()

cache = TTLCache(maxsize=10, ttl=60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Svelte dev server
        "https://transit.m4rt.nl",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/delays")
async def get_country_delays(
    id: str,
    rt_url: str,
    location: str | None = None,
    provider_name: str | None = None,
    feed_name: str | None = None,
):
    feed = Feed(id=id, location=location, rt_url=rt_url)
    cache_key = f"feed_{feed.id}"

    if cache_key in cache:
        cached = cache[cache_key]
        return cached
    try:
        realtime_delay = realtime(feed.rt_url)
        if not realtime_delay:
            return {
                "error": f"no delay data available for {feed.location if feed.location else feed.id}"
            }

        realtime_data = DelayData(
            avg_delay=average_delay(realtime_delay),
            on_time=amount(realtime_delay),
            on_time_percentage=percentage(realtime_delay),
        )

        response = {
            "realtime": realtime_data,
        }

        cache[cache_key] = response

        return response
    except Exception as e:
        return {"error": f"failed to fetch data for {feed.id}: {str(e)}"}


@app.get("/search/{query}")
async def search_feeds(query: str):
    return await find_feeds(query, "gtfs_rt")
