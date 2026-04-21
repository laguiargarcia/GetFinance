# Frontend Design — GetFinance

**Date:** 2026-04-21  
**Stack:** Next.js + Tailwind CSS  
**Pattern:** Two-route SPA consuming existing FastAPI

---

## Architecture

```
frontend/ (Next.js + Tailwind)
├── app/
│   ├── layout.tsx              ← navbar with route links
│   ├── transactions/
│   │   └── page.tsx            ← filters + table + export
│   └── query/
│       └── page.tsx            ← free SQL editor + results
├── components/
│   ├── TransactionTable.tsx
│   ├── FilterBar.tsx
│   └── ExportButton.tsx
└── lib/
    └── api.ts                  ← fetch wrappers for FastAPI
```

FastAPI runs separately. Frontend fetches from it via `lib/api.ts`.

---

## API Contracts

### Existing endpoints (consumed as-is)

| Method | Path | Params |
|---|---|---|
| GET | `/transactions` | `date_from`, `date_to`, `category`, `type`, `format` |
| GET | `/accounts` | `format` |
| GET | `/categories` | — |

### New endpoint (to be added to `api/api.py`)

```
POST /query
Body: { "sql": "SELECT ..." }
Response: { "columns": [...], "rows": [[...], ...] } | { "error": "..." }
```

Executes arbitrary SQL via DuckDB against Delta files. Local use only — no auth required until multi-user.

---

## Route: `/transactions`

Three vertical sections:

1. **FilterBar** — inputs: date_from, date_to, category (dropdown from `/categories`), type (CREDIT / DEBIT / all). "Filter" button triggers fetch.

2. **TransactionTable** — columns: date, description, amount, category, type, account. Client-side pagination (50 rows/page). Negative amounts in red, positive in green.

3. **ExportButton** — dropdown: CSV / JSON / Excel. Downloads via direct link to API with active filters as query params.

---

## Route: `/query`

Two vertical sections:

1. **SQL Editor** — `<textarea>` with monospace font. "Run" button. Sends `POST /query`. Shows inline error if SQL is invalid.

2. **ResultTable** — dynamic columns generated from query result. Export CSV button for result set.

---

## Security

- `/query` endpoint exposed locally only (no auth)
- Add authentication when moving to multi-user
- No user input is interpolated into Delta file paths — only the SQL string is passed to DuckDB

---

## Out of Scope (this phase)

- Authentication / multi-user
- Dashboard with summary cards
- Real-time data refresh
- Mobile layout optimization
