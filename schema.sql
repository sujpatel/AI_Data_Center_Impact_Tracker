-- schema.sql
-- Defines the 5 tables used by this project.
-- ETL scripts use if_exists="replace" so this file only needs to be run once for initial setup.

-- Scraped data center inventory from datacenters.com — one row per facility
CREATE TABLE IF NOT EXISTS data_centers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    operator VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(2)
);

-- EIA SEDS annual electricity prices — one row per state per year
-- Units: dollars per million Btu ($/MMBtu), all sectors combined
-- Source: pr_all.csv, MSN code ESTCD
CREATE TABLE IF NOT EXISTS electricity_prices (
    state VARCHAR(2),
    year INTEGER,
    price_per_mmbtu FLOAT
);

-- EIA SEDS annual CO2 emissions — one row per state per year
-- Units: million metric tons of CO2
-- Source: co2_all.csv, MSN code TETCE
CREATE TABLE IF NOT EXISTS emissions (
    state VARCHAR(2),
    year INTEGER,
    co2_million_metric_tons FLOAT
);

-- Interpolated data center counts + cumulative MW per state per year
-- dc_count is linearly interpolated: 20% of 2025 count in 2010 to 100% in 2025
-- cumulative_mw is from data_center_timelines.csv for the 35 major AI facilities
CREATE TABLE IF NOT EXISTS dc_yearly (
    state VARCHAR(2),
    year INTEGER,
    dc_count FLOAT,
    cumulative_mw FLOAT
);

-- State-level planned data center counts from announcements snapshot
-- Used for forward-looking prediction charts
CREATE TABLE IF NOT EXISTS announcements (
    state VARCHAR(2),
    planned_count INTEGER
);
