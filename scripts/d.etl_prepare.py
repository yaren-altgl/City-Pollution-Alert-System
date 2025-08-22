import pandas as pd
from pathlib import Path

# 📂 Dosya yolları
RAW_DATA_PATH = Path("data/pm10_daily_measurements.csv")
METADATA_PATH = Path("data/all_sensors_with_city_and_location.csv")
OUTPUT_PATH = Path("data/clean_data.csv")

# 1. Ana veri dosyasını oku
df_raw = pd.read_csv(RAW_DATA_PATH)

# 2. Sensor metadata dosyasını oku (sadece utf-8-sig yeterli)
df_meta = pd.read_csv(METADATA_PATH, encoding="utf-8-sig")
df_meta.columns = df_meta.columns.str.strip().str.lower().str.replace(" ", "_")
df_meta = df_meta[["sensor_id", "location_name"]]

# 3. Gerekli sütunları seç
df_raw = df_raw[["sensor_id", "location_id", "date_utc", "value"]]

# 4. Eksik verileri temizle
df_raw = df_raw.dropna(subset=["sensor_id", "value", "date_utc"])

# 5. UTC → İstanbul saatine çevir
df_raw["date_utc"] = pd.to_datetime(df_raw["date_utc"])
if df_raw["date_utc"].dt.tz is None:
    df_raw["timestamp"] = df_raw["date_utc"].dt.tz_localize("UTC").dt.tz_convert("Europe/Istanbul")
else:
    df_raw["timestamp"] = df_raw["date_utc"].dt.tz_convert("Europe/Istanbul")
df_raw["timestamp"] = df_raw["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

# 6. sensor_id üzerinden eşleştir
df_merged = df_raw.merge(df_meta, on="sensor_id", how="left")

# 7. Final sütunları belirle
df_final = df_merged[[
    "sensor_id",
    "location_id",
    "location_name",
    "timestamp",
    "value"
]]

# 8. Kaydet
df_final.to_csv(OUTPUT_PATH, index=False)
print(f"✅ Temiz veri başarıyla kaydedildi: {OUTPUT_PATH}")
