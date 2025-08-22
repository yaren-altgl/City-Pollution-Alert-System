# app.py
from fastapi import FastAPI, Query
from typing import Optional, Literal
# app.py en üstüne ekle
from api.settings import DB_HOST, DB_SSLMODE
from fastapi import HTTPException   # bu da eksikti

from api.repository import (
    get_conn,
    fetch_latest_per_location,
    fetch_latest_per_city,
    fetch_alerts,
    fetch_rankings,
)


app = FastAPI(title="City Pollution Alert System", version="1.0.0")

@app.get("/", include_in_schema=False)
def root():
    return {"message": "City Pollution Alert System API çalışıyor!", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status":"ok"}


@app.get("/latest-data")
def latest_data(scope: Literal["location","city"] = "location"):
    with get_conn() as conn:
        rows = fetch_latest_per_city(conn) if scope=="city" else fetch_latest_per_location(conn)
    return rows

@app.get("/alerts")
def alerts(
    days: int = Query(7, ge=1, le=60),
    threshold: Literal["tr","who","both"] = "both",
    value_cap: float = 1000.0,
):
    with get_conn() as conn:
        rows = fetch_alerts(conn, days=days, threshold=threshold, value_cap=value_cap)
    return rows

@app.get("/rankings/dirtiest")
def rankings_dirtiest(
    days: Optional[int] = Query(None, ge=1, le=60),
    min_samples: int = Query(5, ge=1, le=1000),
    value_cap: float = 1000.0,
    limit: int = Query(10, ge=1, le=100),
):
    with get_conn() as conn:
        rows = fetch_rankings(conn, kind="dirtiest", days=days, min_samples=min_samples, value_cap=value_cap, limit=limit)
    return rows

@app.get("/rankings/cleanest")
def rankings_cleanest(
    days: Optional[int] = Query(None, ge=1, le=60),
    min_samples: int = Query(5, ge=1, le=1000),
    value_cap: float = 1000.0,
    limit: int = Query(10, ge=1, le=100),
):
    with get_conn() as conn:
        rows = fetch_rankings(conn, kind="cleanest", days=days, min_samples=min_samples, value_cap=value_cap, limit=limit)
    return rows
