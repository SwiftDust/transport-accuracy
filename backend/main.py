import json
import os
from dataclasses import dataclass
from enum import Enum

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


@app.get("/analysis")
async def analysis(
    country: str,
    provider_name: str,
    avg_delay: float,
    on_time: int,
    on_time_percentage: float,
):
    results = search_web(f"how many passengers on train {country} average")
    context = "\n\n".join(
        [
            f"[{r['title']}]({r['url']})\n{r['description']}"
            for r in results.get("web", {}).get("results", [])
        ]
    )

    prompt = f"""You are a public transit analyst delivering verdicts about public transit accuracy from GTFS-RT data.

    Here is the data for a feed called {provider_name} (most likely from {country} but this may be inaccurate):
    Please be aware the feed name may not reflect the actual service name or country. In that case, fall back to the country name; {country}.
        - Average delay: {avg_delay:.1f} seconds
        - Trains on time: {on_time}
        - On-time percentage: {on_time_percentage:.1f}%

        Return ONLY a raw JSON object with no markdown, no code fences, no explanation:
        {{
            "delay_analysis": "...",
            "on_time_analysis": "...",
            "percentage_analysis": "..."
        }}

        Rules for all three fields:
        - Max 175 characters / 30 words each
        - No emojis, no quotation marks, no character counts
        - Do not hallucinate data
        - If a value is 0, -1, 100%, or otherwise implausible, write "No data available" for that field
        - This is realtime data, so use the present tense when possible.

        Guidance per field:
        - delay_analysis: Analyze the {avg_delay:.1f}s average delay. Under 60s is generally on time. Consider the time of day ({get_time_by_country(country)}) for context. Negative values may mean trains ran early.
        - on_time_analysis: Analyze {on_time} on-time trains. Try to estimate people transported using average passenger counts (seeing the source below). If sources are unhelpful, don't hallucinate numbers.
        - percentage_analysis: Analyze the {on_time_percentage:.1f}% on-time rate. Consider the time of day for context. Note if small delays are likely the cause of a low score.

        Use the provider name ({provider_name}) to guide your analysis. For example, Deutsche Bahn (DELFI Realtime Data) is less likely to be on time than NS (OVApi).
        Passenger data sources: {context}.
    """

    print(prompt)
    cache_key = f"analysis_{country}"
    if cache_key in cache:
        return cache[cache_key]

    response = client.chat.send(
        model="google/gemini-2.5-flash-lite-preview-09-2025",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )

    try:
        result = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        result = {
            "delay_analysis": "No data available",
            "on_time_analysis": "No data available",
            "percentage_analysis": "No data available",
        }

    cache[cache_key] = result
    return result
