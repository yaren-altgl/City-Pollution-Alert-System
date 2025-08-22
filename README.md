# 🌍 City Pollution Alert System  

**Gerçek zamanlı hava kirliliği takip ve uyarı sistemi**.  
Bu proje, **OpenAQ API**’den hava kirliliği verilerini çekip işleyen, **PostgreSQL (Neon)** üzerinde depolayan ve **FastAPI** ile uç noktalar üzerinden servis eden uçtan uca bir **Data Engineering Pipeline**’dır.  

**Demo Linkleri:**  
- API Base: [https://city-pollution-alert-system.onrender.com](https://city-pollution-alert-system.onrender.com)  
- Swagger Docs: [https://city-pollution-alert-system.onrender.com/docs](https://city-pollution-alert-system.onrender.com/docs)  
- Örnek endpoint:  
  - [Latest Data](https://city-pollution-alert-system.onrender.com/latest-data)  
  - [Alerts](https://city-pollution-alert-system.onrender.com/alerts?days=7&threshold=both)  

---

## Proje Amacı  
- Türkiye’de hava kirliliği seviyelerini analiz etmek  
- WHO ve TR standartlarını aşan ölçümleri tespit etmek  
- Kritik kirlilik seviyelerinde uyarı verecek API servisleri geliştirmek  
- Uçtan uca bir **ETL → Database → API → Deployment** sürecini uygulamalı olarak göstermek  

---

## Kullanılan Teknolojiler  
- **Python (Pandas, Requests, Psycopg2)** → ETL süreci  
- **PostgreSQL (Neon, Docker)** → Veri tabanı  
- **SQL** → Analitik sorgular  
- **FastAPI** → REST API geliştirme  
- **Docker & Docker Compose** → Containerizasyon  
- **Render** → Deployment  

---

## Pipeline Akışı
1. **Veri Çekme** → OpenAQ API’den PM10 ölçümleri alındı  
2. **ETL** → Eksik/yanlış değerler temizlendi, DataFrame’e dönüştürüldü  
3. **Database** → PostgreSQL’e yüklendi (Docker & Neon)  
4. **SQL Analizi** → “En kirli şehirler”, “eşik aşımı yapan şehirler”, “zaman trendi” sorguları yazıldı  
5. **API Geliştirme** →  
   - `/latest-data` → Son ölçümler  
   - `/alerts` → Limit aşımı yapan şehirler  
6. **Deployment** → Render üzerinde canlıya alındı  

---

## Örnek SQL Analizleri  
- **En kirli şehirler (PM10 ortalaması en yüksek 10 şehir)**  
- **En temiz şehirler (PM10 ortalaması en düşük 10 şehir)**  
- **Eşik aşımları (TR ≥50 µg/m³, WHO ≥15 µg/m³)**  
- **2016 vs 2022 trend karşılaştırması**  

---

## API Uç Noktaları
- `GET /latest-data` → Tüm şehirler için en güncel ölçüm  
- `GET /alerts?days=7&threshold=both` → Son N günde TR/WHO eşiklerini aşan şehirler  

Swagger arayüzünden test et:  
👉 [https://city-pollution-alert-system.onrender.com/docs](https://city-pollution-alert-system.onrender.com/docs)  

---

## Çalıştırma (lokalde)
```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. PostgreSQL Docker container başlat
docker-compose up -d

# 3. ETL scriptleri çalıştır
python scripts/d.etl_prepare.py
python scripts/e.upload_to_db.py

# 4. FastAPI başlat
uvicorn api.app:app --reload
```

---

## Notlar
- OpenAQ verilerinde **timestamp’ler 00:00 olarak geliyor** → zaman bazlı analizlerde bu bir kısıt.  
- Bu proje, **gerçek zamanlı pipeline** mantığını göstermek için tasarlandı → canlı veri akışı eklenirse gerçek-time alert sistemi kolayca aktif hale gelir.  

---

##
> Developed and deployed a real-time air quality data pipeline and alert system using Python, PostgreSQL, and FastAPI. Delivered a fully functional API that helps users monitor pollution levels and receive alerts. Demonstrated data engineering skills through end-to-end pipeline design, cloud deployment, and real-time data processing.
