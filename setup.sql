-- ============================================================
-- NOAA GHCN Weather Data — ClickHouse Setup (2 tables)
--
-- Table 1: noaa_weather    — daily weather measurements
-- Table 2: ghcnd_stations  — station metadata + auto-computed Point
--
-- The `location` column on ghcnd_stations is MATERIALIZED from
-- (longitude, latitude), so no separate geo table is needed.
--
-- Run:  clickhouse client --multiquery < setup.sql
-- ============================================================

-- Clean slate
DROP TABLE IF EXISTS noaa_weather;
DROP TABLE IF EXISTS ghcnd_stations;

-- -------------------------------------------------------
-- 1. Weather measurements
-- -------------------------------------------------------
CREATE TABLE noaa_weather
(
    station_id  String,
    date        Date,
    measurement LowCardinality(String),
    value       Int64,
    mFlag       Nullable(String),
    qFlag       Nullable(String),
    sFlag       Nullable(String),
    obsTime     Nullable(String)
)
ENGINE = MergeTree
ORDER BY (station_id, date, measurement);

INSERT INTO noaa_weather
SELECT
    station_id,
    toDate(date, 'YYYYMMDD'),
    measurement,
    value,
    nullIf(mFlag, ''),
    nullIf(qFlag, ''),
    nullIf(sFlag, ''),
    nullIf(obsTime, '')
FROM url(
    'http://127.0.0.1:8000/2022.csv.gz',
    'CSV',
    'station_id String, date String, measurement String, value Int64,
     mFlag String, qFlag String, sFlag String, obsTime String'
);

-- -------------------------------------------------------
-- 2. Station metadata  (with auto-computed geo Point)
-- -------------------------------------------------------
CREATE TABLE ghcnd_stations
(
    id           String,
    latitude     Float64,
    longitude    Float64,
    elevation    Float32,
    state        Nullable(String),
    name         String,
    gsn_flag     Nullable(String),
    hcn_crn_flag Nullable(String),
    wmo_id       Nullable(String),
    location     Point MATERIALIZED CAST((longitude, latitude), 'Point')
)
ENGINE = MergeTree
ORDER BY id;

INSERT INTO ghcnd_stations
SELECT
    trim(substring(line, 1, 11))                AS id,
    toFloat64(trim(substring(line, 13, 8)))     AS latitude,
    toFloat64(trim(substring(line, 22, 9)))     AS longitude,
    toFloat32(trim(substring(line, 32, 6)))     AS elevation,
    nullIf(trim(substring(line, 39, 2)), '')    AS state,
    trim(substring(line, 42, 30))               AS name,
    nullIf(trim(substring(line, 73, 3)), '')    AS gsn_flag,
    nullIf(trim(substring(line, 77, 3)), '')    AS hcn_crn_flag,
    nullIf(trim(substring(line, 81, 5)), '')    AS wmo_id
FROM url(
    'http://127.0.0.1:8000/ghcnd-stations.txt',
    'LineAsString',
    'line String'
);

-- -------------------------------------------------------
-- 3. Verify
-- -------------------------------------------------------
SELECT 'noaa_weather rows :', count() FROM noaa_weather;
SELECT 'ghcnd_stations rows:', count() FROM ghcnd_stations;
SELECT id, state, latitude, longitude, location
FROM ghcnd_stations
WHERE state IS NOT NULL
LIMIT 5;
