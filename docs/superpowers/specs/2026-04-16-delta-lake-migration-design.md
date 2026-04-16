# Delta Lake Migration Design

**Date:** 2026-04-16
**Status:** Approved

## Context

GetFinance currently uses SQLAlchemy ORM (`dataBase.py`) as its persistence layer, but the models are defined and never actually persisted — no connection string, no session management, no writes. The goal is to replace SQLAlchemy entirely with Delta Lake, giving the project a proper data lake architecture with three layers (raw, cleansed, curated) that stores both accounts and transactions from the Pluggy.ai API.

## Architecture

### Files Changed

| File | Action | What changes |
|---|---|---|
| `dataBase.py` | **Delete** | SQLAlchemy removed entirely |
| `functions.py` | **Modify** | Remove SQLAlchemy imports; add `list_transactions(item_id)` function |
| `storage.py` | **Create** | Delta Lake helpers: `write_delta(df, path, mode)` and `read_delta(path)` |
| `main.py` | **Modify** | Remove `dataBase.py` from `BASE_SCRIPTS`; add 3 ETL steps to `PIPELINE` |
| `etl/raw2raw.py` | **Create** | Fetches API data, writes raw Delta tables |
| `etl/raw2cleansed.py` | **Rewrite** | Reads raw Delta, casts types, writes cleansed Delta |
| `etl/cleansed2curated.py` | **Create** | Placeholder — reads cleansed, prints schema |
| `requirements.txt` | **Populate** | Add all required dependencies with versions |

### Data Lake Structure

```
data/
├── raw/
│   ├── accounts/        ← Delta Lake table (all fields as-is from API)
│   └── transactions/    ← Delta Lake table (all fields as-is from API)
├── cleansed/
│   ├── accounts/        ← Delta Lake table (typed, snake_case)
│   └── transactions/    ← Delta Lake table (typed, snake_case)
└── curated/
    ├── accounts/        ← placeholder
    └── transactions/    ← placeholder
```

### Pipeline Flow

```
main.py
  BASE_SCRIPTS: [functions.py, storage.py]
  PIPELINE:     [etl/raw2raw.py, etl/raw2cleansed.py, etl/cleansed2curated.py]
```

Each ETL script receives `functions.py` and `storage.py` injected via the existing code-injection pattern — no imports needed in ETL files.

## Data Models

### Raw Layer

All fields kept exactly as returned by the Pluggy API. A `_ingested_at` timestamp column is added at ingestion time.

**raw/accounts** — all fields from `GET /accounts?itemId={id}`

**raw/transactions** — all fields from `GET /transactions?accountId={id}`

### Cleansed Layer

All fields preserved but with:
- Types cast to proper Spark types (Double for amounts, Date for dates, etc.)
- Column names converted to snake_case
- A `processed_at` timestamp column added

### Curated Layer

Placeholder only. Reads cleansed tables and prints schema + sample rows. No transformations defined yet.

## Implementation Details

### `functions.py` additions

```python
def list_transactions(account_id):
    """Fetch all transactions for a given account_id from Pluggy API."""
    # GET /transactions?accountId={account_id}
    # Returns JSON or None on failure
```

### `etl/raw2raw.py` flow

Transactions depend on account IDs, so the step runs sequentially:

1. For each `item_id` in `ITEM_IDS`: call `list_accounts(item_id)` → collect all accounts
2. Write all accounts to `data/raw/accounts/` (Delta)
3. For each account collected: call `list_transactions(account_id)` → collect all transactions
4. Write all transactions to `data/raw/transactions/` (Delta)

### `storage.py`

```python
def write_delta(df, path, mode="overwrite"):
    df.write.format("delta").mode(mode).save(path)

def read_delta(path):
    return spark.read.format("delta").load(path)
```

### Write mode

`overwrite` for both raw and cleansed layers for now. Incremental/merge strategy is out of scope for this iteration.

## Dependencies

```
requests
python-dotenv
pyspark
delta-spark
```

`delta-spark` version must match the PySpark version installed.

## Verification

1. Run `python main.py` — all 3 pipeline steps should complete without error
2. Confirm `data/raw/accounts/` and `data/raw/transactions/` are created as Delta tables
3. Confirm `data/cleansed/accounts/` and `data/cleansed/transactions/` have correct types
4. Confirm `etl/cleansed2curated.py` prints schema for both tables
5. Confirm `dataBase.py` is deleted and no SQLAlchemy references remain in the codebase
