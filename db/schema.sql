DROP TABLE IF EXISTS pollution_data;

CREATE TABLE pollution_data (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER,
    location_id INTEGER,
    location_name VARCHAR(100),
    value FLOAT,
    timestamp TIMESTAMP
);