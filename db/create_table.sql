-- Step 1: Create the database (if not already created)
CREATE DATABASE sensor_db;

-- Step 2: Connect to the database
\c sensor_db;

-- Step 3: Create the table for raw sensor data
CREATE TABLE raw_sensor_data (
    id SERIAL PRIMARY KEY,                  -- Auto-incrementing primary key
    ts TIMESTAMP NOT NULL,                  -- Timestamp of the sensor reading
    device VARCHAR(50) NOT NULL,            -- Device ID
    co NUMERIC,                             -- Carbon Monoxide reading
    humidity NUMERIC,                       -- Humidity reading
    light BOOLEAN,                          -- Light (true/false)
    lpg NUMERIC,                            -- LPG sensor reading
    motion BOOLEAN,                         -- Motion detection (true/false)
    smoke NUMERIC,                          -- Smoke sensor reading
    temp NUMERIC,                           -- Temperature reading
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Record creation timestamp
);

-- Step 4: Create the table for aggregated metrics
CREATE TABLE aggregated_metrics (
    id SERIAL PRIMARY KEY,                  -- Auto-incrementing primary key
    device VARCHAR(50),                     -- Device ID
    metric VARCHAR(50),                     -- Metric name (e.g., "co", "humidity", etc.)
    min_value NUMERIC,                      -- Minimum value of the metric
    max_value NUMERIC,                      -- Maximum value of the metric
    avg_value NUMERIC,                      -- Average value of the metric
    std_dev NUMERIC,                        -- Standard deviation of the metric
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Record creation timestamp
);

-- Step 5: Add indexes to optimize performance
CREATE INDEX idx_raw_sensor_data_ts ON raw_sensor_data (ts);
CREATE INDEX idx_raw_sensor_data_device ON raw_sensor_data (device);
CREATE INDEX idx_aggregated_metrics_device ON aggregated_metrics (device);
