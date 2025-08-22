# repository.py
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from typing import Optional, List, Dict, Literal, Tuple
from datetime import datetime, timedelta

# relative yerine ABSOLUTE:

from api.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SSLMODE

@contextmanager
def get_conn():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode=DB_SSLMODE  # <<< EKLENDİ
    )
    try:
        yield conn
    finally:
        conn.close()

def get_data_end(conn):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT MAX((timestamp)::timestamptz) AS tmax FROM pollution_data;")
        row = cur.fetchone()
        return row["tmax"] if row else None



def fetch_latest_per_location(conn) -> List[Dict]:
    sql = """
    SELECT DISTINCT ON (location_id)
      location_id,
      split_part(location_name,' - ',1) AS city,
      location_name,
      value,
      timestamp
    FROM pollution_data
    WHERE value IS NOT NULL
    ORDER BY location_id, timestamp DESC;
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql)
        return [dict(r) for r in cur.fetchall()]

def fetch_latest_per_city(conn) -> List[Dict]:
    sql = """
    WITH rows AS (
      SELECT
        split_part(location_name,' - ',1) AS city,
        location_id, location_name, value, timestamp,
        ROW_NUMBER() OVER (PARTITION BY split_part(location_name,' - ',1)
                           ORDER BY timestamp DESC) AS rn
      FROM pollution_data
      WHERE value IS NOT NULL
    )
    SELECT city, location_id, location_name, value, timestamp
    FROM rows WHERE rn=1;
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql)
        return [dict(r) for r in cur.fetchall()]

from datetime import datetime, timedelta
import psycopg2, psycopg2.extras

def fetch_alerts(
    conn,
    days: int = 7,
    threshold: str = "both",
    value_cap: float = 1000.0,
    tr_limit: float = 50.0,
    who_limit: float = 15.0,
):
    # 1) tmax'ı alias ile ve timestamptz cast ederek al
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT MAX((timestamp)::timestamptz) AS tmax FROM pollution_data;")
        row = cur.fetchone()
        tmax = row["tmax"] if row else None
        if tmax is None:
            return []

        # Emniyet: nadir durumda string gelirse parse et
        if isinstance(tmax, str):
            tmax = datetime.fromisoformat(tmax.replace(" ", "T"))

        start = tmax - timedelta(days=days)

        sql = """
        WITH windowed AS (
          SELECT
            split_part(location_name,' - ',1) AS city,
            location_name, location_id, value,
            (timestamp)::timestamptz AS ts
          FROM pollution_data
          WHERE value IS NOT NULL
            AND value < %(value_cap)s
            AND (timestamp)::timestamptz BETWEEN %(start)s AND %(end)s
        ),
        agg AS (
          SELECT
            city,
            COUNT(*) FILTER (WHERE value >= %(tr_limit)s)  AS tr_exceed_count,
            COUNT(*) FILTER (WHERE value >= %(who_limit)s) AS who_exceed_count,
            MAX(value) AS worst_value,
            MAX(ts)    AS latest_exceed_ts
          FROM windowed
          GROUP BY city
        )
        SELECT city, tr_exceed_count, who_exceed_count, worst_value, latest_exceed_ts
        FROM agg
        WHERE (%(threshold)s = 'tr'   AND tr_exceed_count  > 0)
           OR (%(threshold)s = 'who'  AND who_exceed_count > 0)
           OR (%(threshold)s = 'both' AND (tr_exceed_count > 0 OR who_exceed_count > 0))
        ORDER BY
          CASE WHEN %(threshold)s = 'tr'  THEN tr_exceed_count  END DESC NULLS LAST,
          CASE WHEN %(threshold)s = 'who' THEN who_exceed_count END DESC NULLS LAST,
          worst_value DESC;
        """
        params = {
            "value_cap": value_cap,
            "start": start,
            "end": tmax,
            "tr_limit": tr_limit,
            "who_limit": who_limit,
            "threshold": threshold,
        }
        cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        for r in rows:
            r["window"] = {"end": tmax.isoformat(), "days": days}
        return rows

def _ranking_sql(order: Literal["asc","desc"]) -> str:
    return f"""
    SELECT
      split_part(location_name,' - ',1) AS city,
      ROUND(AVG(NULLIF(value,0))::numeric, 2) AS avg_pm10,
      ROUND(MAX(value)::numeric, 2)           AS max_pm10,
      COUNT(*)                                AS sample_count
    FROM {{source}}
    WHERE value IS NOT NULL AND value < %(value_cap)s
    GROUP BY city
    HAVING COUNT(*) >= %(min_samples)s
    ORDER BY avg_pm10 {order}
    LIMIT %(limit)s;
    """

def _apply_window(conn, days: Optional[int]) -> Tuple[str, dict]:
    """days verilirse zaman pencereli CTE döndür; yoksa tabloyu doğrudan kullan."""
    if not days:
        return "pollution_data", {}
    tmax = get_data_end(conn)
    if tmax is None:
        return "pollution_data", {}
    from datetime import timedelta
    start = tmax - timedelta(days=days)
    source = f"(SELECT * FROM pollution_data WHERE timestamp BETWEEN %(start)s AND %(end)s) AS sub"
    return source, {"start": start, "end": tmax}

def fetch_rankings(
    conn,
    kind: Literal["dirtiest","cleanest"],
    days: Optional[int] = None,
    min_samples: int = 5,
    value_cap: float = 1000.0,
    limit: int = 10,
) -> List[Dict]:
    order = "DESC" if kind == "dirtiest" else "ASC" 
    base_sql = _ranking_sql(order.lower())
    source, extra = _apply_window(conn, days)
    sql = base_sql.replace("{source}", source)
    params = {"min_samples": min_samples, "value_cap": value_cap, "limit": limit, **extra}
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        if days:
            tmax = get_data_end(conn)
            if tmax:
                for r in rows:
                    r["window"] = {"end": tmax.isoformat(), "days": days}
        return rows
