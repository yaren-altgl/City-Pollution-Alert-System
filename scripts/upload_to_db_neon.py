# scripts/upload_to_db_neon.py
import os
import sys
import math
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# .env'i güvenli şekilde bul ve yükle
try:
    from dotenv import load_dotenv, find_dotenv  # pip install python-dotenv
    env_path = find_dotenv(usecwd=True)
    if not env_path:
        # Proje kökü = bu dosyanın iki klasör üstü (scripts/ -> proje kökü)
        env_path = str(Path(__file__).resolve().parents[1] / ".env")
    load_dotenv(env_path, override=True)
except Exception as e:
    print(f"⚠️ .env yüklenemedi: {e}")

def require_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        print(f"❌ Gerekli değişken eksik: {key}. Lütfen proje kökündeki .env dosyanı kontrol et.")
        sys.exit(1)
    return val

NEON_HOST = require_env("NEON_HOST")
NEON_DB   = require_env("NEON_DATABASE")
NEON_USER = require_env("NEON_USER")
NEON_PASS = require_env("NEON_PASSWORD")
NEON_PORT = int(os.getenv("NEON_PORT", "5432"))
SSL_MODE  = os.getenv("NEON_SSLMODE", "require")  # Neon için 'require' şart

CSV_PATH   = os.getenv("CSV_PATH", str(Path(__file__).resolve().parents[1] / "data" / "clean_data.csv"))
SCHEMA_PATH= os.getenv("SCHEMA_PATH", str(Path(__file__).resolve().parents[1] / "db" / "schema.sql"))
CHUNK_SIZE = int(os.getenv("BULK_CHUNK_SIZE", "5000"))

def connect_neon():
    return psycopg2.connect(
        host=NEON_HOST,
        database=NEON_DB,
        user=NEON_USER,
        password=NEON_PASS,
        port=NEON_PORT,
        sslmode=SSL_MODE,
    )

def create_table():
    if not Path(SCHEMA_PATH).exists():
        print(f"⚠️ Şema dosyası bulunamadı: {SCHEMA_PATH}. Bu adımı atlıyorum.")
        return
    with connect_neon() as conn, conn.cursor() as cur:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        print("✅ (Neon) Tablo/şema oluşturuldu.")

def load_data():
    if not Path(CSV_PATH).exists():
        print(f"❌ CSV bulunamadı: {CSV_PATH}")
        sys.exit(1)

    df = pd.read_csv(
        CSV_PATH,
        encoding="utf-8-sig",
        dtype={"sensor_id":"Int64","location_id":"Int64","location_name":"string","value":"float64"},
        parse_dates=["timestamp"],
        infer_datetime_format=True
    )

    # Gerekli kolon kontrolü
    req = {"sensor_id","location_id","location_name","value","timestamp"}
    miss = req - set(df.columns)
    if miss:
        print(f"❌ Eksik kolon(lar): {miss}")
        sys.exit(1)

    # Temizlik
    before = len(df)
    df = df.dropna(subset=list(req))
    if len(df) < before:
        print(f"ℹ️ {before-len(df)} satır eksik veri nedeniyle atlandı.")

    df["sensor_id"] = df["sensor_id"].astype("int64")
    df["location_id"] = df["location_id"].astype("int64")
    df["location_name"] = df["location_name"].astype(str)
    df["value"] = df["value"].astype(float)

    rows = list(df[["sensor_id","location_id","location_name","value","timestamp"]].itertuples(index=False, name=None))
    if not rows:
        print("ℹ️ Yüklenecek satır yok.")
        return

    total = len(rows)
    with connect_neon() as conn, conn.cursor() as cur:
        for i in range(0, total, CHUNK_SIZE):
            batch = rows[i:i+CHUNK_SIZE]
            execute_values(cur, """
                INSERT INTO pollution_data
                  (sensor_id, location_id, location_name, value, timestamp)
                VALUES %s
            """, batch)
            print(f"↳ {min(i+CHUNK_SIZE, total)}/{total} satır yüklendi...")
        print(f"✅ (Neon) {total} satır başarıyla yüklendi.")

if __name__ == "__main__":
    masked_host = NEON_HOST.split(".")[0] + "...neon.tech" if ".neon.tech" in NEON_HOST else NEON_HOST
    print(f"🔌 Bağlanılıyor: {masked_host} | db={NEON_DB} | sslmode={SSL_MODE}")
    create_table()
    load_data()
