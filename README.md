# ch-visual
Visualization for Geo-type aggregate functions in ClickHouse.
Uses the [ClickHouse blogpost](https://clickhouse.com/blog/real-world-data-noaa-climate-data) that uses the NOAA dataset, as reference.

## Setup Instructions

### Clickhouse Server
- Make sure `clickhouse-server` is running, compiled from source, that has the `groupPolygonUnion`, `groupPolygonIntersection`, and `groupConvexHull` aggregate functions present,
- Make sure you have a stable internet connection
- run the `setup.sql` script 

### Python stuff
- make a venv in the current directory using `python3 -m venv .venv` (optional)
  - activate the venv using `source ./.venv/bin/activate` (or `./.venv/bin/activate.ps1` on Windows Powershell) 
- install dependencies using `pip install -r requirements.txt`

## Running the visualization

- make sure the venv is active (if used)
- `python main.py`
- close each visualization window to move to the next visualization

The time taken for clickhouse to calculate the convex hulls for the NOAA dataset is present in the title of their respective visualizations.


## Performance

ClickHouse was compiled and run on the following machines, and tested for query performance.

- MacBook Pro (16", Nov 2023)
  - M3 Pro - ARM64
  - 18 GB Unified Memory, Built-In NVMe SSD
  - macOS Tahoe 26.3
- Lenovo IdeaPad 310-14IKB
  - Intel Core i5 7200U (2C4T) - x86_64
  - 8GB DDR4 RAM, 5400 RPM HDD
  - Ubuntu Server 24.04.3 LTS

| Query                             | Vertices,Hulls | MacBook | IdeaPad |
|-----------------------------------|----------------|---------|---------|
| groupConvexHull, global           | 75846, 1       | 69 ms   | 158 ms  |
| groupConvexHull, GROUP BY state   | 75846, 52      | 61 ms   | 130 ms  |
| groupConvexHull, GROUP BY country | 129657, 219    | 91 ms   | 246 ms  |
