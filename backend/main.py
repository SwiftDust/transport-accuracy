from enum import Enum

from cachetools import TTLCache
from fastapi import FastAPI
from helpers.average_delay import average_delay
from helpers.calculate_ontime import amount, percentage
from wrappers.fetch_trip_updates import realtime

app = FastAPI()

cache = TTLCache(maxsize=10, ttl=60)


# TODO: Add function to discover all countries via Mobility Database
class Country(str, Enum):
    netherlands = "netherlands"
    belgium = "belgium"
    germany = "germany"


COUNTRY_CONFIG = {
    Country.netherlands: {"feed_url": "http://gtfs.ovapi.nl/nl/tripUpdates.pb"},
    Country.belgium: {"feed_url": "PLACEHOLDER_BELGIUM_FEED_URL"},
    Country.germany: {"feed_url": "PLACEHOLDER_GERMANY_FEED_URL"},
}


@app.get("/delays/world")
async def get_world_delays():
    return {"message": f"Hello World"}


@app.get("/delays/country/{country}")
async def get_country_delays(country: Country):
    cache_key = f"country_{country}"

    if cache_key in cache:
        cached = cache[cache_key]
        return {
            "realtime_avg_delay": cached["realtime_avg_delay"],
            "on_time": cached["on_time"],
            "on_time_percentage": cached["on_time_percentage"],
        }

    config = COUNTRY_CONFIG.get(country)
    if not config:
        return {"error": f"{country} is not supported yet!"}

    try:
        realtime_delay = realtime(config["feed_url"])
        if not realtime_delay:
            return {"error": f"no delay data available for {country}"}

        avg_delay = average_delay(realtime_delay)
        on_time = amount(realtime_delay)
        on_time_percentage = percentage(realtime_delay)

        cache[cache_key] = {
            "realtime_avg_delay": avg_delay,
            "on_time": on_time,
            "on_time_percentage": on_time_percentage,
        }

        return {
            "realtime_avg_delay": avg_delay,
            "on_time": on_time,
            "on_time_percentage": on_time_percentage,
        }
    except Exception as e:
        return {"error": f"failed to fetch data for {country}: {str(e)}"}


@app.get("/delays/location/{location}")
async def get_delays(location: str):
    return {"message": f"Hello {location}"}
