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

|  | M3 Pro MBP | Some Other Machine |
|---------|------------------------|----------------------------------|
| Global groupConvexHull  | 1 ms                     | 2 ms                                |
| groupConvexHull GROUP BY state  | 1  ms                     | 2 ms                               |
