import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

from cachetools import TTLCache
from fastapi import FastAPI
from helpers.average_delay import average_delay
from helpers.calculate_ontime import amount, percentage
from helpers.database import get_delay_snapshots, init_database, store_delay_snapshot
from wrappers.fetch_trip_updates import realtime
from wrappers.search_completion import find_feeds


@dataclass
class DelayData:
    """Represents realtime delay statistics for a time period"""

    avg_delay: float
    on_time: int
    on_time_percentage: float


@dataclass
class HistoricalDelayData:
    """Represents historical delay statistics (aggregate, no on_time count)"""

    avg_delay: float
    on_time_percentage: float


async def poll_all_countries():
    while True:
        for country, config in COUNTRY_CONFIG.items():
            try:
                delays = realtime(config["feed_url"])
                if delays:
                    avg_delay = average_delay(delays)
                    on_time = amount(delays)
                    on_time_percentage = percentage(delays)
                    store_delay_snapshot(
                        country, avg_delay, on_time, on_time_percentage
                    )
                    print(
                        f"polling succeeded for {country}: avg_delay={avg_delay}, on_time={on_time}, on_time_percentage={on_time_percentage}"
                    )
            except Exception as e:
                print(f"polling failed for {country}: {e}")
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    asyncio.create_task(poll_all_countries())
    yield


app = FastAPI(lifespan=lifespan)

cache = TTLCache(maxsize=10, ttl=60)


# TODO: add function to discover all countries via Mobility Database
class Country(str, Enum):
    netherlands = "netherlands"
    belgium = "belgium"
    germany = "germany"


COUNTRY_CONFIG = {
    Country.netherlands: {"feed_url": "http://gtfs.ovapi.nl/nl/tripUpdates.pb"},
    Country.belgium: {"feed_url": "https://data.gtfs.be/sncb/gtfs/tripUpdates.pb"},
    Country.germany: {"feed_url": " https://realtime.gtfs.de/realtime-free.pb"},
}


@app.get("/delays/world")
async def get_world_delays():
    return {"message": f"Hello World"}


@app.get("/delays/country/{country}")
async def get_country_delays(country: Country):
    cache_key = f"country_{country}"

    if cache_key in cache:
        cached = cache[cache_key]
        return cached

    config = COUNTRY_CONFIG.get(country)
    if not config:
        return {"error": f"{country} is not supported yet!"}

    try:
        realtime_delay = realtime(config["feed_url"])
        if not realtime_delay:
            return {"error": f"no delay data available for {country}"}

        realtime_data = DelayData(
            avg_delay=average_delay(realtime_delay),
            on_time=amount(realtime_delay),
            on_time_percentage=percentage(realtime_delay),
        )

        historical_stats = get_delay_snapshots(country)

        historical_data = HistoricalDelayData(
            avg_delay=historical_stats["avg_delay"],
            on_time_percentage=historical_stats["on_time_percentage"],
        )

        response = {
            "realtime": realtime_data,
            "historical": historical_data,
        }

        cache[cache_key] = response

        return response
    except Exception as e:
        return {"error": f"failed to fetch data for {country}: {str(e)}"}


@app.get("/delays/location/{location}")
async def get_delays(location: str):
    return {"error": f"locations are not supported yet"}


@app.get("/search/{query}")
async def search_feeds(query: str):
    return await find_feeds(query, "gtfs_rt")
