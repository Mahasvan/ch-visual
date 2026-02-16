# NOAA GHCN Weather Data — ClickHouse Setup & Visualization

## Overview

Two-table schema for NOAA Global Historical Climatology Network data:

| Table | Purpose |
|-------|---------|
| `noaa_weather` | Daily weather measurements (2022) |
| `ghcnd_stations` | Station metadata with auto-computed `Point` geo column |

The `location` column on `ghcnd_stations` is defined as
`MATERIALIZED CAST((longitude, latitude), 'Point')` — it is computed
automatically on insert, so no separate geo table or materialized view
is required.

---

## Prerequisites

* ClickHouse server running on `localhost`
* A local HTTP file server (`python -m http.server 8000`) serving:
  * `2022.csv.gz` — NOAA daily weather CSV
  * `ghcnd-stations.txt` — fixed-width station list
* Python packages: `clickhouse-connect`, `shapely`, `matplotlib`, `cartopy`

---

## Step 1 — Run the SQL setup

```bash
~/Quest1/Clickhouse/build/programs/clickhouse client --multiquery < setup.sql
```

This will:

1. Drop existing tables (safe to re-run)
2. Create `noaa_weather` and insert 2022 data (~22M rows)
3. Create `ghcnd_stations` and insert station metadata (~130k rows)
4. Print row counts and a sample for verification

---

## Step 2 — Verify in the client

```sql
-- Row counts
SELECT count() FROM noaa_weather;       -- ~22M
SELECT count() FROM ghcnd_stations;     -- ~130k

-- The location column is auto-computed
SELECT id, state, latitude, longitude, location
FROM ghcnd_stations
WHERE id LIKE 'US%'
LIMIT 5;

-- Closest stations to Miami (US only)
SELECT id, name,
       geoDistance(longitude, latitude, -80.1918, 25.7617) / 1000 AS km
FROM ghcnd_stations
WHERE id LIKE 'US%'
ORDER BY km
LIMIT 10;

-- Stations within 50 km of Miami
SELECT count()
FROM ghcnd_stations
WHERE id LIKE 'US%'
  AND geoDistance(longitude, latitude, -80.1918, 25.7617) < 50000;

-- Convex hull of all US stations
SELECT wkt(groupConvexHull(location))
FROM ghcnd_stations
WHERE id LIKE 'US%';
```

---

## Step 3 — Run the visualizations

```bash
python main.py
```

This produces six plots:

1. **groupPolygonUnion** — union of two overlapping squares
2. **groupPolygonIntersection** — intersection of two overlapping squares
3. **groupConvexHull (Polygons)** — convex hull of two overlapping squares
4. **groupConvexHull (LineStrings)** — convex hull of four line segments
5. **Station Convex Hull** — US stations on a world map with overall hull (includes query time)
6. **Station Hulls by State** — per-state convex hulls with 10 randomized colours (includes query time)

Station demos filter to US-only stations (`id LIKE 'US%'`) and display
ClickHouse query time in the plot title.

---

## Project Structure

```
setup.sql       SQL schema + data load (idempotent)
instructions.md This file
db.py           ClickHouse connection & query helpers
plots.py        Matplotlib / Cartopy plotting utilities
demos.py        Six demo visualizations
main.py         Entry point
```

---

## Schema Details

### `noaa_weather`

```sql
CREATE TABLE noaa_weather (
    station_id  String,
    date        Date,
    measurement LowCardinality(String),
    value       Int64,
    mFlag       Nullable(String),
    qFlag       Nullable(String),
    sFlag       Nullable(String),
    obsTime     Nullable(String)
) ENGINE = MergeTree
ORDER BY (station_id, date, measurement);
```

### `ghcnd_stations`

```sql
CREATE TABLE ghcnd_stations (
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
) ENGINE = MergeTree
ORDER BY id;
```

The `MATERIALIZED` keyword means ClickHouse computes `location`
automatically whenever a row is inserted — no manual population needed.
