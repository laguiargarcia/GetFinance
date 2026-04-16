import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

_api_token = None
_api_token_created_at = 0


spark = SparkSession.builder.appName("meuApp").getOrCreate()


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ITEMS_ID = [item.strip() for item in os.getenv("ITEM_IDS", "").split(",") if item.strip()]
from pyspark.sql import SparkSession


def get_api_token():
    global _api_token, _api_token_created_at
    now = time.time()

    if _api_token is not None and (now - _api_token_created_at) < 7200:
        return _api_token

    url = "https://api.pluggy.ai/auth"

    body = {
        "clientId": CLIENT_ID,
        "clientSecret": CLIENT_SECRET
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=body, headers=headers)

    if response.status_code == 200:
        _api_token = response.json().get("apiKey")
        _api_token_created_at = now
        return _api_token
    else:
        print(f"Failed to get token: {response.status_code} - {response.text}")
        return None


def list_accounts(item_id):
    token = get_api_token()

    url = f"https://api.pluggy.ai/accounts?itemId={item_id}"
    headers = {
        "accept": "application/json",
        "X-API-KEY": f"{token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get account: {response.status_code} - {response.text}")
        return None