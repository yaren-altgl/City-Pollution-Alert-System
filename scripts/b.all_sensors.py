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

# 1. Location ID’leri oku
locations_df = pd.read_csv("data/locations.csv")
location_ids = locations_df["id"].dropna().astype(int).tolist()


# ... API key, headers ve location_ids tanımı yukarıda olsun

all_rows = []

for location_id in location_ids[:50]:  # önce 50 ile test et
    url = f"https://api.openaq.org/v3/locations/{location_id}"
    try:
        while True:
            response = requests.get(url, headers=headers)

            # Eğer 429 alırsak 10 saniye bekle ve yeniden dene
            if response.status_code == 429:
                print(f"🔁 429 - Bekleniyor... (id={location_id})")
                time.sleep(10)
                continue

            elif response.status_code != 200:
                print(f"❌ Hata (id={location_id}): {response.status_code}")
                break

            data = response.json()
            location = data["results"][0]
            sensors = location.get("sensors", [])

            for sensor in sensors:
                row = {
                    "sensor_id": sensor.get("id"),
                    "parameter": sensor.get("parameter", {}).get("name"),
                    "units": sensor.get("parameter", {}).get("units"),
                    "location_id": location["id"],
                    "location_name": location.get("name"),
                    "city": location.get("locality"),
                    "country": location.get("country", {}).get("code")
                }
                all_rows.append(row)

            print(f"✔ {location_id} işlendi.")
            time.sleep(0.3)  # 1 saniyeden kısa ama yeterli
            break

    except Exception as e:
        print(f"⚠️ Exception for id {location_id}: {e}")
        continue

# DataFrame'e ve CSV’ye yaz
df = pd.DataFrame(all_rows)
df.to_csv("data/all_sensors_with_city_and_location.csv", index=False, encoding="utf-8-sig")
