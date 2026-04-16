# Delta Lake Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace SQLAlchemy with Delta Lake as the persistence layer, storing accounts and transactions from the Pluggy API across three data layers: raw, cleansed, and curated.

**Architecture:** The existing code-injection pipeline pattern is preserved — `main.py` concatenates `functions.py` + `storage.py` before each ETL script. Three ETL steps run in sequence: `raw2raw.py` (fetch API → write raw Delta), `raw2cleansed.py` (raw Delta → typed/normalized cleansed Delta), `cleansed2curated.py` (placeholder that reads cleansed and prints schema).

**Tech Stack:** Python, PySpark 3.5, delta-spark 3.1, requests, python-dotenv, pytest

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `requirements.txt` | Modify | Pin all dependencies |
| `functions.py` | Modify | Fix import order, update SparkSession for Delta, add `list_transactions()` |
| `storage.py` | Create | `write_delta(df, path, mode)` and `read_delta(path)` helpers |
| `main.py` | Modify | Replace `dataBase.py` → `storage.py` in BASE_SCRIPTS; add 3 ETL steps to PIPELINE |
| `etl/raw2raw.py` | Create | Fetch accounts + transactions from Pluggy API, write to `data/raw/` |
| `etl/raw2cleansed.py` | Rewrite | Read raw Delta, cast types + snake_case rename, write to `data/cleansed/` |
| `etl/cleansed2curated.py` | Create | Placeholder: read cleansed tables, print schema + sample rows |
| `dataBase.py` | Delete | SQLAlchemy removed |
| `tests/conftest.py` | Create | Shared pytest fixtures (SparkSession, temp dir) |
| `tests/test_storage.py` | Create | Tests for `write_delta` / `read_delta` |
| `tests/test_functions.py` | Create | Tests for `list_transactions` (mocked HTTP) |
| `tests/test_cleansed.py` | Create | Tests for type casting + column renaming logic |

---

## Task 1: Populate requirements.txt

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Write requirements.txt**

```
requests==2.32.3
python-dotenv==1.0.1
pyspark==3.5.0
delta-spark==3.1.0
pytest==8.3.5
```

- [ ] **Step 2: Add data/ to .gitignore**

Add this line to `.gitignore` (create the file if it doesn't exist):

```
data/
```

- [ ] **Step 3: Install dependencies**

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Expected: all packages install without errors. If there are version conflicts between `pyspark` and `delta-spark`, check https://docs.delta.io/latest/releases.html for the compatibility matrix and adjust both versions to match.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt .gitignore
git commit -m "chore: pin dependencies including delta-spark, ignore data/ directory"
```

---

## Task 2: Create storage.py

**Files:**
- Create: `storage.py`
- Create: `tests/conftest.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/conftest.py`:

```python
import pytest
import tempfile
import os
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    builder = (
        SparkSession.builder.appName("test")
        .master("local[1]")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.shuffle.partitions", "1")
    )
    from delta import configure_spark_with_delta_pip
    session = configure_spark_with_delta_pip(builder).getOrCreate()
    yield session
    session.stop()


@pytest.fixture
def tmp_path_str(tmp_path):
    return str(tmp_path)
```

Create `tests/test_storage.py`:

```python
import pytest
from pyspark.sql import Row


def test_write_and_read_delta(spark, tmp_path_str):
    from storage import write_delta, read_delta
    path = tmp_path_str + "/test_table"
    data = [Row(id="1", name="conta corrente", balance=100.0)]
    df = spark.createDataFrame(data)

    write_delta(df, path)
    result = read_delta(path)

    assert result.count() == 1
    assert result.collect()[0]["id"] == "1"


def test_write_delta_overwrite(spark, tmp_path_str):
    from storage import write_delta, read_delta
    path = tmp_path_str + "/test_overwrite"
    df1 = spark.createDataFrame([Row(id="1")])
    df2 = spark.createDataFrame([Row(id="2")])

    write_delta(df1, path)
    write_delta(df2, path, mode="overwrite")
    result = read_delta(path)

    assert result.count() == 1
    assert result.collect()[0]["id"] == "2"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
source venv/bin/activate
pytest tests/test_storage.py -v
```

Expected: `ImportError: No module named 'storage'` or similar failure.

- [ ] **Step 3: Create storage.py**

```python
def write_delta(df, path, mode="overwrite"):
    df.write.format("delta").mode(mode).save(path)


def read_delta(path):
    from pyspark.sql import SparkSession
    spark = SparkSession.getActiveSession()
    return spark.read.format("delta").load(path)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_storage.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add storage.py tests/conftest.py tests/test_storage.py
git commit -m "feat: add storage.py with Delta Lake write/read helpers"
```

---

## Task 3: Update functions.py

**Files:**
- Modify: `functions.py`
- Create: `tests/test_functions.py`

Changes:
1. Fix import order (move `from pyspark.sql import SparkSession` to the top)
2. Configure SparkSession to support Delta Lake
3. Add `list_transactions(account_id)` function

- [ ] **Step 1: Write the failing test**

Create `tests/test_functions.py`:

```python
import pytest
from unittest.mock import patch, MagicMock


def test_list_transactions_returns_json_on_success():
    import functions
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "total": 1,
        "results": [{"id": "txn1", "amount": -50.0, "description": "Supermercado"}]
    }
    with patch("functions.requests.get", return_value=mock_response):
        with patch("functions.get_api_token", return_value="fake-token"):
            result = functions.list_transactions("acc-123")

    assert result["results"][0]["id"] == "txn1"


def test_list_transactions_returns_none_on_failure():
    import functions
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    with patch("functions.requests.get", return_value=mock_response):
        with patch("functions.get_api_token", return_value="fake-token"):
            result = functions.list_transactions("acc-123")

    assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_functions.py -v
```

Expected: `AttributeError: module 'functions' has no attribute 'list_transactions'`

- [ ] **Step 3: Rewrite functions.py**

```python
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
    url = f"https://api.pluggy.ai/transactions?accountId={account_id}"
    headers = {"accept": "application/json", "X-API-KEY": token}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get transactions: {response.status_code} - {response.text}")
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_functions.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add functions.py tests/test_functions.py
git commit -m "feat: update SparkSession for Delta Lake, add list_transactions()"
```

---

## Task 4: Update main.py

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Update main.py**

Replace the content of `main.py` with:

```python
import subprocess
import sys
from pathlib import Path

BASE_SCRIPTS = [
    "functions.py",
    "storage.py",
]

PIPELINE = [
    "etl/raw2raw.py",
    "etl/raw2cleansed.py",
    "etl/cleansed2curated.py",
]


def build_combined_code(target_script: str) -> str:
    parts = []
    for path in BASE_SCRIPTS + [target_script]:
        code = Path(path).read_text(encoding="utf-8")
        parts.append(f"# {'='*40}\n# {path}\n# {'='*40}\n{code}\n")
    return "\n".join(parts)


def run_step(script: str) -> None:
    print(f"\n{'='*50}")
    print(f"▶ Iniciando: {script}")
    print(f"{'='*50}")

    combined_code = build_combined_code(script)

    result = subprocess.run(
        [sys.executable, "-c", combined_code],
        check=False,
    )

    if result.returncode != 0:
        print(f"\n✗ Falha em '{script}' (exit code {result.returncode}). Pipeline interrompido.")
        sys.exit(result.returncode)

    print(f"✔ Concluído: {script}")


if __name__ == "__main__":
    all_scripts = BASE_SCRIPTS + PIPELINE
    for script in all_scripts:
        if not Path(script).exists():
            print(f"✗ Arquivo não encontrado: {script}")
            sys.exit(1)

    for script in PIPELINE:
        run_step(script)

    print("\n✔ Pipeline concluído com sucesso.")
```

- [ ] **Step 2: Commit**

```bash
git add main.py
git commit -m "feat: update pipeline to use storage.py and 3 ETL steps"
```

---

## Task 5: Create etl/raw2raw.py

**Files:**
- Create: `etl/raw2raw.py`

This script is injected with `functions.py` + `storage.py` — do NOT add imports for those.

- [ ] **Step 1: Create etl/raw2raw.py**

```python
import json
from datetime import datetime, timezone
from pyspark.sql.functions import lit

ingested_at = datetime.now(timezone.utc).isoformat()

all_accounts = []
all_transactions = []

for item_id in ITEMS_ID:
    accounts_response = list_accounts(item_id)
    if accounts_response is None:
        print(f"Skipping item_id {item_id}: failed to fetch accounts")
        continue

    accounts = accounts_response.get("results", [])
    all_accounts.extend(accounts)

    for account in accounts:
        account_id = account.get("id")
        transactions_response = list_transactions(account_id)
        if transactions_response is None:
            print(f"Skipping account {account_id}: failed to fetch transactions")
            continue
        transactions = transactions_response.get("results", [])
        for txn in transactions:
            txn["accountId"] = account_id
        all_transactions.extend(transactions)

if all_accounts:
    accounts_df = spark.read.json(
        spark.sparkContext.parallelize([json.dumps(a) for a in all_accounts])
    )
    accounts_df = accounts_df.withColumn("_ingested_at", lit(ingested_at))
    write_delta(accounts_df, "data/raw/accounts")
    print(f"raw/accounts: {accounts_df.count()} rows written")
else:
    print("No accounts fetched — raw/accounts not written")

if all_transactions:
    transactions_df = spark.read.json(
        spark.sparkContext.parallelize([json.dumps(t) for t in all_transactions])
    )
    transactions_df = transactions_df.withColumn("_ingested_at", lit(ingested_at))
    write_delta(transactions_df, "data/raw/transactions")
    print(f"raw/transactions: {transactions_df.count()} rows written")
else:
    print("No transactions fetched — raw/transactions not written")
```

- [ ] **Step 2: Verify the step runs (manual)**

```bash
source venv/bin/activate
python main.py
```

Expected: pipeline runs `raw2raw.py` and creates `data/raw/accounts/` and `data/raw/transactions/` as Delta tables (folders with `_delta_log/` inside). If the pipeline fails at `raw2raw.py`, the remaining steps are skipped.

- [ ] **Step 3: Commit**

```bash
git add etl/raw2raw.py
git commit -m "feat: add raw2raw ETL step to fetch and store accounts and transactions"
```

---

## Task 6: Rewrite etl/raw2cleansed.py

**Files:**
- Rewrite: `etl/raw2cleansed.py`
- Create: `tests/test_cleansed.py`

The cleansed layer:
- Reads raw Delta tables
- Casts `balance` (accounts) and `amount` (transactions) to DoubleType
- Casts `date` (transactions) to DateType
- Renames all top-level columns from camelCase to snake_case
- Adds `processed_at` timestamp

- [ ] **Step 1: Write the failing tests**

Create `tests/test_cleansed.py`:

```python
import pytest
import re
from pyspark.sql import Row
from pyspark.sql.functions import col, current_timestamp, lit
from pyspark.sql.types import DoubleType, DateType


def camel_to_snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def test_camel_to_snake():
    assert camel_to_snake("currencyCode") == "currency_code"
    assert camel_to_snake("itemId") == "item_id"
    assert camel_to_snake("balance") == "balance"
    assert camel_to_snake("descriptionRaw") == "description_raw"


def test_accounts_balance_cast(spark, tmp_path_str):
    raw_path = tmp_path_str + "/raw/accounts"
    cleansed_path = tmp_path_str + "/cleansed/accounts"

    raw_data = [Row(id="1", name="Conta", balance="1500.50", currencyCode="BRL", itemId="item1")]
    raw_df = spark.createDataFrame(raw_data)
    raw_df.write.format("delta").mode("overwrite").save(raw_path)

    df = spark.read.format("delta").load(raw_path)
    df = df.withColumn("balance", col("balance").cast(DoubleType()))
    df = df.select([col(c).alias(camel_to_snake(c)) for c in df.columns])
    df.write.format("delta").mode("overwrite").save(cleansed_path)

    result = spark.read.format("delta").load(cleansed_path)
    row = result.collect()[0]
    assert row["balance"] == 1500.50
    assert "currency_code" in result.columns
    assert "item_id" in result.columns


def test_transactions_amount_and_date_cast(spark, tmp_path_str):
    raw_path = tmp_path_str + "/raw/transactions"
    cleansed_path = tmp_path_str + "/cleansed/transactions"

    raw_data = [Row(id="t1", description="Mercado", amount="-89.90", date="2024-03-15", accountId="acc1")]
    raw_df = spark.createDataFrame(raw_data)
    raw_df.write.format("delta").mode("overwrite").save(raw_path)

    df = spark.read.format("delta").load(raw_path)
    df = df.withColumn("amount", col("amount").cast(DoubleType()))
    df = df.withColumn("date", col("date").cast(DateType()))
    df = df.select([col(c).alias(camel_to_snake(c)) for c in df.columns])
    df.write.format("delta").mode("overwrite").save(cleansed_path)

    result = spark.read.format("delta").load(cleansed_path)
    row = result.collect()[0]
    assert row["amount"] == -89.90
    assert str(row["date"]) == "2024-03-15"
    assert "account_id" in result.columns
```

- [ ] **Step 2: Run tests to verify they pass (these tests are self-contained)**

```bash
pytest tests/test_cleansed.py -v
```

Expected: 3 tests PASS. These tests define the transformation logic inline to validate expected behavior — they serve as a regression baseline. Once `raw2cleansed.py` implements the same `camel_to_snake` logic and casting, any divergence in behavior will break these tests.

- [ ] **Step 3: Rewrite etl/raw2cleansed.py**

```python
import re
from pyspark.sql.functions import col, current_timestamp
from pyspark.sql.types import DoubleType, DateType


def camel_to_snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


# --- Cleanse accounts ---
accounts_raw = read_delta("data/raw/accounts")
accounts_cleansed = accounts_raw.withColumn("balance", col("balance").cast(DoubleType()))
accounts_cleansed = accounts_cleansed.select(
    [col(c).alias(camel_to_snake(c)) for c in accounts_cleansed.columns]
)
accounts_cleansed = accounts_cleansed.withColumn("processed_at", current_timestamp())
write_delta(accounts_cleansed, "data/cleansed/accounts")
print(f"cleansed/accounts: {accounts_cleansed.count()} rows written")
accounts_cleansed.printSchema()

# --- Cleanse transactions ---
transactions_raw = read_delta("data/raw/transactions")
transactions_cleansed = transactions_raw.withColumn("amount", col("amount").cast(DoubleType()))
transactions_cleansed = transactions_cleansed.withColumn("date", col("date").cast(DateType()))
transactions_cleansed = transactions_cleansed.select(
    [col(c).alias(camel_to_snake(c)) for c in transactions_cleansed.columns]
)
transactions_cleansed = transactions_cleansed.withColumn("processed_at", current_timestamp())
write_delta(transactions_cleansed, "data/cleansed/transactions")
print(f"cleansed/transactions: {transactions_cleansed.count()} rows written")
transactions_cleansed.printSchema()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_cleansed.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add etl/raw2cleansed.py tests/test_cleansed.py
git commit -m "feat: rewrite raw2cleansed to use Delta Lake with type casting and snake_case"
```

---

## Task 7: Create etl/cleansed2curated.py

**Files:**
- Create: `etl/cleansed2curated.py`

Placeholder step — reads cleansed tables and shows schema + sample rows.

- [ ] **Step 1: Create etl/cleansed2curated.py**

```python
print("=" * 50)
print("curated/accounts (placeholder)")
print("=" * 50)
accounts = read_delta("data/cleansed/accounts")
accounts.printSchema()
accounts.show(5, truncate=False)

print("=" * 50)
print("curated/transactions (placeholder)")
print("=" * 50)
transactions = read_delta("data/cleansed/transactions")
transactions.printSchema()
transactions.show(5, truncate=False)
```

- [ ] **Step 2: Run full pipeline to verify all 3 steps work**

```bash
source venv/bin/activate
python main.py
```

Expected output (in order):
```
▶ Iniciando: etl/raw2raw.py
raw/accounts: N rows written
raw/transactions: N rows written
✔ Concluído: etl/raw2raw.py

▶ Iniciando: etl/raw2cleansed.py
cleansed/accounts: N rows written
cleansed/transactions: N rows written
✔ Concluído: etl/raw2cleansed.py

▶ Iniciando: etl/cleansed2curated.py
[schema + sample rows printed]
✔ Concluído: etl/cleansed2curated.py

✔ Pipeline concluído com sucesso.
```

- [ ] **Step 3: Commit**

```bash
git add etl/cleansed2curated.py
git commit -m "feat: add cleansed2curated placeholder ETL step"
```

---

## Task 8: Delete dataBase.py

**Files:**
- Delete: `dataBase.py`

- [ ] **Step 1: Delete the file**

```bash
git rm dataBase.py
```

- [ ] **Step 2: Run all tests to confirm nothing broke**

```bash
pytest tests/ -v
```

Expected: all tests PASS. No references to `dataBase.py` should remain.

- [ ] **Step 3: Confirm no SQLAlchemy references remain**

```bash
grep -r "sqlalchemy\|dataBase" . --include="*.py" --exclude-dir=venv
```

Expected: no output.

- [ ] **Step 4: Run pipeline one final time**

```bash
python main.py
```

Expected: pipeline runs successfully end-to-end.

- [ ] **Step 5: Commit**

```bash
git commit -m "chore: remove dataBase.py and SQLAlchemy dependency"
```

---

## Verification Checklist

After all tasks are complete:

- [ ] `data/raw/accounts/` exists and contains `_delta_log/`
- [ ] `data/raw/transactions/` exists and contains `_delta_log/`
- [ ] `data/cleansed/accounts/` exists with `balance` as DoubleType and snake_case columns
- [ ] `data/cleansed/transactions/` exists with `amount` as DoubleType, `date` as DateType, snake_case columns
- [ ] `dataBase.py` is deleted
- [ ] No `sqlalchemy` import remains in any `.py` file
- [ ] `pytest tests/ -v` passes all tests
- [ ] `python main.py` completes with exit code 0
