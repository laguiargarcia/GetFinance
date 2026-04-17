import requests
import time
import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

load_dotenv()

_api_token = None
_api_token_created_at = 0

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ITEMS_ID = [item.strip() for item in os.getenv("ITEM_IDS", "").split(",") if item.strip()]

_builder = (
    SparkSession.builder.appName("meuApp")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog",
    )
)
spark = configure_spark_with_delta_pip(_builder).getOrCreate()


def get_api_token():
    global _api_token, _api_token_created_at
    now = time.time()

    if _api_token is not None and (now - _api_token_created_at) < 7200:
        return _api_token

    url = "https://api.pluggy.ai/auth"
    body = {"clientId": CLIENT_ID, "clientSecret": CLIENT_SECRET}
    headers = {"accept": "application/json", "content-type": "application/json"}

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
    if token is None:
        print("list_accounts: skipped — no valid API token")
        return None
    url = f"https://api.pluggy.ai/accounts?itemId={item_id}"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get accounts: {response.status_code} - {response.text}")
        return None


def list_transactions(account_id):
    token = get_api_token()
    if token is None:
        print("list_transactions: skipped — no valid API token")
        return None
    url = f"https://api.pluggy.ai/transactions?accountId={account_id}"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get transactions: {response.status_code} - {response.text}")
        return None


def delta_to_csv(delta_path, csv_path):
    import shutil
    df = spark.read.format("delta").load(delta_path)
    tmp_path = csv_path + "_tmp"
    df.coalesce(1).write.mode("overwrite").option("header", "true").csv(tmp_path)
    part_file = next(
        f for f in os.listdir(tmp_path) if f.startswith("part-") and f.endswith(".csv")
    )
    shutil.move(os.path.join(tmp_path, part_file), csv_path)
    shutil.rmtree(tmp_path)
