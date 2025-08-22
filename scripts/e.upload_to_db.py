import psycopg2
import pandas as pd
import os

def create_table():
    conn = psycopg2.connect(
        host="localhost",
        database="pollution_db",
        user="pollution_user",
        password="pollution_pass",
        port=5432
    )

    schema_path = os.path.join(os.getcwd(), "db", "schema.sql")
    
    with conn.cursor() as cur:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            cur.execute(schema_sql)
            conn.commit()
            print("✅ Tablo oluşturuldu.")
    
    conn.close()

def load_data():
    df = pd.read_csv("data/clean_data.csv", encoding="utf-8-sig")

    conn = psycopg2.connect(
        host="localhost",
        database="pollution_db",
        user="pollution_user",
        password="pollution_pass",
        port=5432
    )

    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO pollution_data (sensor_id, location_id, location_name, value, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                int(row["sensor_id"]),
                int(row["location_id"]),
                row["location_name"],
                float(row["value"]),
                row["timestamp"]
            ))
        conn.commit()
        print(f"✅ {len(df)} satır başarıyla yüklendi.")

    conn.close()

if __name__ == "__main__":
    create_table()
    load_data()
