-- ===========================================================
-- City Pollution Alert System - Analiz Sorguları (tarihsiz set)
-- Şema: pollution_data(id, sensor_id, location_id, location_name, value, timestamp)
-- Not: Saatler 00:00 olduğundan saatlik analizler yok; şehir/limit/trend odaklıyız.
-- ===========================================================

\pset pager off
\timing on

-- ===========================================================
\echo === 1) EN KIRLI ŞEHİRLER (ortalaması en yüksek ilk 10) ===
SELECT
  split_part(location_name, ' - ', 1) AS city,
  ROUND(AVG(NULLIF(value,0))::numeric, 2) AS avg_pm10,
  ROUND(MAX(value)::numeric, 2)           AS max_pm10,
  COUNT(*)                                AS sample_count
FROM pollution_data
WHERE value IS NOT NULL AND value < 1000
GROUP BY city
HAVING COUNT(*) >= 5
ORDER BY avg_pm10 DESC
LIMIT 10;


\echo === 2) EN TEMIZ ŞEHİRLER (ortalaması en düşük ilk 10) ===
SELECT
  split_part(location_name, ' - ', 1) AS city,
  ROUND(AVG(NULLIF(value,0))::numeric, 2) AS avg_pm10,
  ROUND(MAX(value)::numeric, 2)           AS max_pm10,
  COUNT(*)                                AS sample_count
FROM pollution_data
WHERE value IS NOT NULL AND value < 1000
GROUP BY city
HAVING COUNT(*) >= 5
ORDER BY avg_pm10 ASC
LIMIT 10;


\echo === 3) EŞİK AŞIMLARI (TR 50 µg/m³) EN ÇOK İHLAL ===
SELECT
  split_part(location_name, ' - ', 1) AS city,
  COUNT(*) AS exceed_count
FROM pollution_data
WHERE value >= 50
GROUP BY city
ORDER BY exceed_count DESC
LIMIT 10;

\echo === 3b) EŞİK AŞIMLARI (WHO 15 µg/m³) EN ÇOK İHLAL ===
SELECT
  split_part(location_name, ' - ', 1) AS city,
  COUNT(*) AS exceed_count
FROM pollution_data
WHERE value >= 50 
GROUP BY city
ORDER BY exceed_count DESC
LIMIT 10;


\echo === 4) TREND: 2016 vs 2022 ORTALAMALARI ===
SELECT
  EXTRACT(YEAR FROM timestamp)::int AS year,
  ROUND(AVG(NULLIF(value,0))::numeric, 2) AS avg_pm10,
  COUNT(*) AS sample_count
FROM pollution_data
WHERE value IS NOT NULL AND value < 1000
  AND EXTRACT(YEAR FROM timestamp) IN (2016, 2022)
GROUP BY year
ORDER BY year;


\echo === 5) TREND: Her lokasyon için en güncel ölçüm ===
-- Her lokasyon için en güncel kayıt
SELECT DISTINCT ON (location_id)
  location_id,
  split_part(location_name,' - ',1) AS city,
  location_name,
  value,
  timestamp
FROM pollution_data
WHERE value IS NOT NULL
ORDER BY location_id, timestamp DESC;


\echo === 6) TREND: Son N günde eşik aşımı ===
-- Son N gün penceresini verideki son tarihten kur
WITH bounds AS (
  SELECT MAX(timestamp) AS tmax FROM pollution_data
),
windowed AS (
  SELECT
    split_part(location_name,' - ',1) AS city,
    location_name, location_id, value, timestamp
  FROM pollution_data p, bounds b
  WHERE p.value IS NOT NULL
    AND p.timestamp >= b.tmax - INTERVAL '7 days'  -- N=7 örnek
),
agg AS (
  SELECT
    city,
    COUNT(*) FILTER (WHERE value >= 50) AS tr_exceed_count,
    COUNT(*) FILTER (WHERE value >= 15) AS who_exceed_count,
    MAX(value) AS worst_value,
    MAX(timestamp) AS latest_exceed_ts
  FROM windowed
  GROUP BY city
)
SELECT *
FROM agg
WHERE tr_exceed_count > 0 OR who_exceed_count > 0
ORDER BY COALESCE(tr_exceed_count,0) DESC, COALESCE(who_exceed_count,0) DESC, worst_value DESC;
