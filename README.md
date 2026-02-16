# ch-visual
Visualization for Geo-type aggregate functions in ClickHouse

## Setup Instructions

### Fileserver
- Make sure you have a HTTP file server running on `localhost:8000`
  - Make sure `2022.csv.gz` and `ghcnd-stations.txt` are present in the root.
  - In the folder you have those two files downloaded, run `python3 -m http.server`
  - You can also change the setup sql script to use the S3 URL, instead of the localhost fileserver.

### Clickhouse Server
- Make sure `clickhouse-server` is running, compiled from source, that has the `groupPolygonUnion`, `groupPolygonIntersection`, and `groupConvexHull` aggregate functions present,
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

| Machine | Global groupConvexHull | groupConvexHull grouped by state |
|---------|------------------------|----------------------------------|
| M3 Pro  | 1                      | 2                                |
