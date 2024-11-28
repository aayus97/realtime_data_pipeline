-- Step 1: Create the database (if not already created)
CREATE DATABASE sensor_db;

-- Step 2: Connect to the database
\c sensor_db;

-- Step 3: Create the table for raw sensor data
--CREATE TABLE raw_sensor_data (
--    id SERIAL PRIMARY KEY,                  -- Auto-incrementing primary key
--    ts TIMESTAMP NOT NULL,                  -- Timestamp of the sensor reading
--    device VARCHAR(50) NOT NULL,            -- Device ID
--    co NUMERIC,                             -- Carbon Monoxide reading
--    humidity NUMERIC,                       -- Humidity reading
--    light BOOLEAN,                          -- Light (true/false)
--    lpg NUMERIC,                            -- LPG sensor reading
--    motion BOOLEAN,                         -- Motion detection (true/false)
--    smoke NUMERIC,                          -- Smoke sensor reading
--    temp NUMERIC,                           -- Temperature reading
--    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Record creation timestamp
--);

-- Create partitioned table for raw sensor data
CREATE TABLE raw_sensor_data (
    id SERIAL NOT NULL,
    ts TIMESTAMP NOT NULL,
    device VARCHAR(255) NOT NULL,
    co NUMERIC,
    humidity NUMERIC,
    light BOOLEAN,
    lpg NUMERIC,
    motion BOOLEAN,
    smoke NUMERIC,
    temp NUMERIC,
    file_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ts, device, id)  -- Include ts in the primary key
) PARTITION BY RANGE (ts);

-- Create monthly partitions
CREATE TABLE raw_sensor_data_2024_11 PARTITION OF raw_sensor_data
FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');

CREATE TABLE raw_sensor_data_2024_12 PARTITION OF raw_sensor_data
FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

-- Add indexes for efficient querying
CREATE INDEX idx_device ON raw_sensor_data (device);
CREATE INDEX idx_ts_device ON raw_sensor_data (ts, device);



-- Step 4: Create the table for aggregated metrics
--CREATE TABLE aggregated_metrics (
--    id SERIAL PRIMARY KEY,                  -- Auto-incrementing primary key
--    device VARCHAR(50),                     -- Device ID
--    metric VARCHAR(50),                     -- Metric name (e.g., "co", "humidity", etc.)
--    min_value NUMERIC,                      -- Minimum value of the metric
--    max_value NUMERIC,                      -- Maximum value of the metric
--    avg_value NUMERIC,                      -- Average value of the metric
--    std_dev NUMERIC,                        -- Standard deviation of the metric
--    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Record creation timestamp
--);

CREATE TABLE aggregated_metrics (
    id SERIAL PRIMARY KEY,
    device VARCHAR(255) NOT NULL,
    metric VARCHAR(50) NOT NULL,
    min_value NUMERIC,
    max_value NUMERIC,
    avg_value NUMERIC,
    std_dev NUMERIC,
    median_value NUMERIC,
    count NUMERIC,
    file_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 5: Add indexes to optimize performance
CREATE INDEX idx_aggregated_metrics_device ON aggregated_metrics (device);
