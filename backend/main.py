import os
from dataclasses import dataclass
from enum import Enum
from webbrowser import get

from cachetools import TTLCache
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from helpers.average_delay import average_delay
from helpers.calculate_ontime import amount, percentage
from helpers.get_time import get_time_by_country
from helpers.search_web import search_web
from openrouter import OpenRouter
from wrappers.fetch_trip_updates import realtime
from wrappers.search_completion import find_feeds

client = OpenRouter(
    api_key=os.getenv("AI_API_KEY"),
    server_url="https://ai.hackclub.com/proxy/v1",
)


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


class Mode(str, Enum):
    DELAY_SECONDS = "delay_seconds"
    ON_TIME = "on_time"
    ON_TIME_PERCENTAGE = "on_time_percentage"


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
    location: str,
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


@app.get("/analysis/{mode}")
async def analysis(mode: Mode, country: str, data: str):
    print("request with mode=", mode, "country=", country, "data=", data)
    BASE = f"""You are a public transit analyst who specializes in delivering a verdict about public transit accuracy. Your data you get from a GTFS-RT feed for a specific agency. I will specify the mode, you will just see a float or int as data. This data represents the delay in seconds, on-time percentage, or on-time count, depending on the mode.\n
    You will also get the country, and you will use this to provide a verdict about the public transit accuracy in that country.
    You will respond with a verdict about the public transit accuracy in the specified country.
    Please keep your response concise and use no more than 175 characters or 30 words. However, do not mention this in your answer.
    The answer is intended for on a website, so do not use anything like "" or the amount of characters used, nor should you use smileys in your response.
    Do not hallucinate data.

    Here is the data you need to analyze:
    country: {country}
    data: {data}

    The current time in {country} is {get_time_by_country(country)}. Use this to provide a more accurate verdict.
    """
    cache_key = f"{mode}_{country}_{data}"
    if cache_key in cache:
        return cache[cache_key]

    match mode:
        case Mode.DELAY_SECONDS:
            prompt = (
                BASE
                + """\nMode: DELAY_SECONDS\nYou are analyzing delay in seconds. If the delay is less than 60 seconds, most of the transit will likely be on time.
            Here is an example of an analysis for when the average delay was 40.7 seconds at 5:34 pm:

            ---
            Not a bad score for 5:34PM, rush hour! That's less than a minute for the most crowded part of the day!
            ---

            If you get an unlikely number like 0 or -1, respond with "No data available". If you get a natural negative number, however unlikely, it could be that most trains were early. In that case, still provide an analysis.
            """
            )
        case Mode.ON_TIME:
            results = search_web(f"how many passengers on train {country} average")

            prompt = (
                BASE
                + f"""\nMode: ON_TIME\nYou are analyzing the amount of trains that are on time (less than 60 seconds delay on any of the stops in the entire trip.)
            Here is an example of an analysis for when there were 5421 trains on time in a made-up country (this means, please don't rely on these numbers as your source of truth):

            ---
            In your country, there's an average of 324 people on a train. This means 1.8 million people are transported to their destination without friction right now!
            ---
            If you get an unlikely number like 0 or -1, respond with "No data available".

            If you want, here are some sources you can look at to find average passenger count on a train:\n\n{context}

            If this data didn't produce anything useful, please don't hallucinate numbers but instead just make do with the data you have.
            """
            )
        case Mode.ON_TIME_PERCENTAGE:
            prompt = (
                BASE
                + """\nMode: ON_TIME_PERCENTAGE\nYou are analyzing the percentage of trains that are on time (less than 60 seconds delay on any of the stops in the entire trip.)
            Here is an example of an analysis for when the on-time percentage was 33.1% at 5:34 pm:

            ---
            Even for rush hour, this is not the best ever, but keep in mind most of these are small <5 minute delays.
            ---
            If you get something like 100% or 0% or anything you deem unlikely to be real, respond with "No data available".
            """
            )

    response = client.chat.send(
        model="qwen3/32b",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )

    cache[cache_key] = response.choices[0].message.content
    return response.choices[0].message.content
