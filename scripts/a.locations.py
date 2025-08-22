import requests
import pandas as pd
import os

from dotenv import load_dotenv

# .env yükle
load_dotenv()

api_key = os.getenv("OPENAQ_API_KEY")
base_url = "https://api.openaq.org/v3/locations"

headers = {
    "accept": "application/json",
    "X-API-Key": api_key
}

all_results = []
page = 1

while True:
    params = {
        "limit": 1000,
        "page": page,
        "order_by": "id",
        "sort_order": "asc",
        "countries_id": 66
    }

    response = requests.get(base_url, headers=headers, params=params)
    data = response.json()

    results = data.get("results", [])
    if not results:
        break

    all_results.extend(results)
    page += 1

df = pd.DataFrame([
    {
        "id": r["id"],
        "name": r["name"],
        "city": r["locality"],
        "timezone": r["timezone"],
        "latitude": r["coordinates"]["latitude"] if r.get("coordinates") else None,
        "longitude": r["coordinates"]["longitude"] if r.get("coordinates") else None
    }
    for r in all_results if r.get("coordinates") is not None
])
df.to_csv("data/locations.csv", index=False, encoding="utf-8-sig")

print(f"Toplam çekilen istasyon sayısı (ham): {len(all_results)}")
print(f"VeriFrame satır sayısı (koordinatı olanlar): {df.shape[0]}")
print(f"Benzersiz istasyon ID sayısı: {df['id'].nunique()}")
print(f"Şehir sayısı: {df['city'].nunique()}")