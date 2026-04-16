# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

GetFinance is a Python ETL pipeline that fetches financial data from the [Pluggy.ai](https://pluggy.ai) API (Brazilian open banking aggregator) and processes it with PySpark.

## Running the Pipeline

```bash
# Activate virtual environment first
source venv/bin/activate

# Run the full pipeline
python main.py

# Run a single ETL step directly (for development)
python -c "$(cat functions.py dataBase.py etl/raw2cleansed.py)"
```

## Environment Variables

A `.env` file is required (gitignored). Required variables:

```
CLIENT_ID=<pluggy client id>
CLIENT_SECRET=<pluggy client secret>
ITEM_IDS=<comma-separated pluggy item ids>
```

## Architecture

### Code-injection pipeline pattern

`main.py` orchestrates the pipeline with an unusual pattern: rather than using imports, it **concatenates** `functions.py` and `dataBase.py` as raw text before each ETL script, then executes the combined string via `subprocess.run([sys.executable, "-c", combined_code])`.

This means ETL scripts in `etl/` can freely use anything defined in `functions.py` or `dataBase.py` without importing them — those names are already in scope at runtime. The tradeoff is that **import order within `functions.py` matters**: anything used before its import statement will fail when the file runs standalone but work when injected (since other files may have imported it already). Currently `SparkSession` is used on line 12 of `functions.py` but imported on line 18 — this works only because of the injection order.

### Layers

| File | Role |
|---|---|
| `main.py` | Pipeline runner — validates files, injects base scripts, executes each ETL step |
| `functions.py` | Pluggy API client — token caching (2-hour TTL), account listing, SparkSession init |
| `dataBase.py` | SQLAlchemy ORM models (`Accounts` table) |
| `etl/raw2cleansed.py` | ETL step 1 — calls `list_accounts()`, reads `dados.json` with Spark |

### Adding a new ETL step

1. Create `etl/your_step.py` — use `functions.py` and `dataBase.py` names freely (no imports needed)
2. Add the path to the `PIPELINE` list in `main.py`

## Dependencies

Install with:
```bash
pip install -r requirements.txt
```

Key packages: `requests`, `python-dotenv`, `pyspark`, `sqlalchemy`
