import requests
import pandas as pd
import time
import os

from dotenv import load_dotenv

# .env yükle
load_dotenv()

api_key = os.getenv("OPENAQ_API_KEY")
headers = {
    "accept": "application/json",
    "X-API-Key": api_key
}

# PM10 sensörlerini filtrele
df_all_sensors = pd.read_csv("data/all_sensors_with_city_and_location.csv")
pm10_sensors = df_all_sensors[df_all_sensors["parameter"] == "pm10"]

all_data = []

for idx, row in pm10_sensors.iterrows():
    sensor_id = row["sensor_id"]
    location_id = row["location_id"]
    city = row["city"]
    country = row["country"]

    page = 1
    while True:
        url = f"https://api.openaq.org/v3/sensors/{sensor_id}/days"
        params = {
            "limit": 100,
            "page": page
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 429:
            print(f"⏳ Rate limit! Bekleniyor... (sensor_id={sensor_id})")
            time.sleep(10)
            continue
        elif response.status_code != 200:
            print(f"❌ Hata: {response.status_code} (sensor_id={sensor_id})")
            break

        data = response.json().get("results", [])
        if not data:
            break

        for d in data:
            all_data.append({
                "sensor_id": sensor_id,
                "location_id": location_id,
                "city": city,
                "country": country,
                "date_utc": d["period"]["datetimeFrom"]["utc"],
                "value": d["value"],
                "avg": d["summary"]["avg"],
                "max": d["summary"]["max"],
                "min": d["summary"]["min"],
                "std_dev": d["summary"].get("sd")
            })

        print(f"✅ {sensor_id} - page {page} işlendi.")
        page += 1
        time.sleep(0.3)

# CSV’ye kaydet
df_result = pd.DataFrame(all_data)
df_result.to_csv("data/pm10_daily_measurements.csv", index=False, encoding="utf-8-sig")

print(f"Toplam kayıt sayısı: {len(df_result)}")

