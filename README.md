# GetFinance

Personal finance pipeline that fetches data from Brazilian open banking (via [Pluggy](https://pluggy.ai)) and exposes it through a web interface.

## Stack

| Layer | Technology |
|---|---|
| Ingestion | Pluggy API + PySpark |
| Storage | Delta Lake |
| API | FastAPI + DuckDB |
| Frontend | Next.js + Tailwind CSS |

## Setup

### 1. Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
CLIENT_ID=<pluggy client id>
CLIENT_SECRET=<pluggy client secret>
ITEM_IDS=<comma-separated pluggy item ids>
```

### 2. Run the pipeline

```bash
cd ingestion
jupyter nbconvert --to notebook --execute --inplace main.ipynb
```

This fetches accounts and transactions from Pluggy and writes Delta Lake files to `etl/data/`.

### 3. Start the API

```bash
uvicorn api.api:app --reload
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Features

### Transactions (`/transactions`)
- Filter by date range, category, and type (credit/debit)
- Export to CSV, JSON, or Excel

### SQL Query (`/query`)
- Run arbitrary SQL against the Delta Lake data
- Use `{transactions}` and `{accounts}` as table references
- Export results to CSV

**Example queries:**

```sql
-- spending by category
SELECT category, SUM(amount) as total
FROM delta_scan('{transactions}')
GROUP BY category
ORDER BY total ASC

-- recent transactions
SELECT date, description, amount, category
FROM delta_scan('{transactions}')
ORDER BY date DESC
LIMIT 50
```

### Refresh data
Click "Atualizar dados" in the navbar to re-run the full pipeline and fetch new transactions.

## Project structure

```
ingestion/
  functions.ipynb   # Pluggy API client
  main.ipynb        # Pipeline orchestrator
etl/
  landing2raw.ipynb   # Fetch → raw Delta
  raw2cleansed.ipynb  # Clean → cleansed Delta
api/
  api.py            # FastAPI endpoints
frontend/
  app/              # Next.js pages
  components/       # React components
  lib/              # API client and types
infra/
  docker-compose.yml  # FastAPI + Superset
```
