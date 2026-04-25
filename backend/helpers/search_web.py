import os

import requests


def search_web(query: str) -> dict:
    response = requests.get(
        "https://search.hackclub.com/res/v1/web/search",
        params={"q": query, "count": 5},
        headers={"Authorization": f"Bearer {os.environ['SEARCH_API_KEY']}"},
    )
    return response.json()
