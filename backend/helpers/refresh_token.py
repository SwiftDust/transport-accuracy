import os

import requests
from dotenv import load_dotenv

load_dotenv()


def refresh_token():
    url = "https://api.mobilitydatabase.org/v1/tokens"
    headers = {"Content-Type": "application/json"}
    data = {"refresh_token": os.getenv("REFRESH_TOKEN")}

    response = requests.post(url, headers=headers, json=data)

    return response.json()
