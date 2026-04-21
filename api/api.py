import io
import duckdb
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import date
from typing import Optional
from pydantic import BaseModel

app = FastAPI(title="GetFinance Export API")

TRANSACTIONS_PATH = "data/cleansed/transactions"
ACCOUNTS_PATH = "data/cleansed/accounts"

TRANSACTION_COLS = "date, description, amount, category, type, currency_code, account_id, status, operation_type"
ACCOUNT_COLS = "id, name, number, balance, currency_code, type, subtype"


def get_con():
    con = duckdb.connect()
    con.execute("LOAD delta;")
    return con


def build_transaction_query(date_from, date_to, category, tx_type):
    filters = []
    if date_from:
        filters.append(f"date >= '{date_from}'")
    if date_to:
        filters.append(f"date <= '{date_to}'")
    if category:
        filters.append(f"lower(category) LIKE lower('%{category}%')")
    if tx_type:
        filters.append(f"type = '{tx_type.upper()}'")
    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    return f"SELECT {TRANSACTION_COLS} FROM delta_scan('{TRANSACTIONS_PATH}') {where} ORDER BY date DESC"


@app.get("/transactions")
def export_transactions(
    format: str = Query("csv", pattern="^(csv|json|excel)$"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    category: Optional[str] = None,
    type: Optional[str] = Query(None, pattern="^(CREDIT|DEBIT)$"),
):
    con = get_con()
    query = build_transaction_query(date_from, date_to, category, type)
    rel = con.execute(query)

    if format == "json":
        rows = rel.fetchall()
        cols = [d[0] for d in rel.description] if rows else TRANSACTION_COLS.split(", ")
        data = [dict(zip(cols, r)) for r in rows]
        # re-run for column names
        rel2 = con.execute(query)
        cols = [d[0] for d in rel2.description]
        rows2 = rel2.fetchall()
        data = [dict(zip(cols, r)) for r in rows2]
        import json
        return StreamingResponse(
            io.BytesIO(json.dumps(data, default=str).encode()),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=transactions.json"},
        )

    if format == "excel":
        import openpyxl
        rel2 = con.execute(query)
        cols = [d[0] for d in rel2.description]
        rows2 = rel2.fetchall()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(cols)
        for r in rows2:
            ws.append([str(v) if v is not None else "" for v in r])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=transactions.xlsx"},
        )

    # csv default
    rel2 = con.execute(query)
    cols = [d[0] for d in rel2.description]
    rows2 = rel2.fetchall()
    lines = [",".join(cols)]
    for r in rows2:
        lines.append(",".join(str(v) if v is not None else "" for v in r))
    content = "\n".join(lines)
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@app.get("/accounts")
def export_accounts(format: str = Query("csv", pattern="^(csv|json|excel)$")):
    con = get_con()
    query = f"SELECT * FROM delta_scan('{ACCOUNTS_PATH}')"

    if format == "json":
        rel = con.execute(query)
        cols = [d[0] for d in rel.description]
        rows = rel.fetchall()
        data = [dict(zip(cols, r)) for r in rows]
        import json
        return StreamingResponse(
            io.BytesIO(json.dumps(data, default=str).encode()),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=accounts.json"},
        )

    if format == "excel":
        import openpyxl
        rel = con.execute(query)
        cols = [d[0] for d in rel.description]
        rows = rel.fetchall()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(cols)
        for r in rows:
            ws.append([str(v) if v is not None else "" for v in r])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=accounts.xlsx"},
        )

    rel = con.execute(query)
    cols = [d[0] for d in rel.description]
    rows = rel.fetchall()
    lines = [",".join(cols)]
    for r in rows:
        lines.append(",".join(str(v) if v is not None else "" for v in r))
    content = "\n".join(lines)
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=accounts.csv"},
    )


@app.get("/categories")
def list_categories():
    con = get_con()
    rows = con.execute(
        f"SELECT DISTINCT category, COUNT(*) as count FROM delta_scan('{TRANSACTIONS_PATH}') GROUP BY category ORDER BY count DESC"
    ).fetchall()
    return [{"category": r[0], "count": r[1]} for r in rows]


class QueryRequest(BaseModel):
    sql: str


@app.post("/query")
def run_query(req: QueryRequest):
    try:
        con = get_con()
        rel = con.execute(req.sql)
        cols = [d[0] for d in rel.description]
        rows = rel.fetchall()
        return {"columns": cols, "rows": [list(r) for r in rows]}
    except duckdb.Error as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
