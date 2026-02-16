"""ClickHouse connection and geometry query helpers."""

import clickhouse_connect
from shapely import wkt


def connect(host="localhost", port=8123):
    """Return a clickhouse-connect client."""
    return clickhouse_connect.get_client(host=host, port=port)


# ------------------------------------------------------------------
# Temporary geometry tables (for polygon / linestring demos)
# ------------------------------------------------------------------

def _to_wkt_polygon(coords):
    if coords[0] != coords[-1]:
        coords = coords + [coords[0]]
    pts = ", ".join(f"{x} {y}" for x, y in coords)
    return f"POLYGON(({pts}))"


def _to_wkt_linestring(coords):
    pts = ", ".join(f"{x} {y}" for x, y in coords)
    return f"LINESTRING({pts})"


def _create_temp(client, name, geom_type):
    client.command(f"DROP TABLE IF EXISTS {name}")
    client.command(
        f"CREATE TABLE {name} (id UInt32, geom {geom_type}) ENGINE = Memory"
    )


def load_polygons(client, coords_list, table="_poly_tmp"):
    """Create a temp Polygon table and insert geometries. Returns table name."""
    _create_temp(client, table, "Polygon")
    for i, c in enumerate(coords_list):
        client.command(
            f"INSERT INTO {table} VALUES ({i+1}, readWKTPolygon('{_to_wkt_polygon(c)}'))"
        )
    return table


def load_linestrings(client, coords_list, table="_line_tmp"):
    """Create a temp LineString table and insert geometries. Returns table name."""
    _create_temp(client, table, "LineString")
    for i, c in enumerate(coords_list):
        client.command(
            f"INSERT INTO {table} VALUES ({i+1}, readWKTLineString('{_to_wkt_linestring(c)}'))"
        )
    return table


def aggregate_geom(client, table, func):
    """Run an aggregate geo function and return a Shapely geometry.

    func: 'groupPolygonUnion' | 'groupPolygonIntersection' | 'groupConvexHull'
    """
    row = client.query(f"SELECT wkt({func}(geom)) FROM {table}")
    wkt_str = row.result_rows[0][0]
    return wkt.loads(wkt_str), wkt_str


def drop(client, table):
    client.command(f"DROP TABLE IF EXISTS {table}")


# ------------------------------------------------------------------
# Station queries  (uses ghcnd_stations directly)
# ------------------------------------------------------------------

US_FILTER = "id LIKE 'US%'"


def fetch_station_points(client, where=US_FILTER):
    """Return (lons, lats) lists for stations matching *where*."""
    rows = client.query(
        f"SELECT longitude, latitude FROM ghcnd_stations WHERE {where}"
    ).result_rows
    return [r[0] for r in rows], [r[1] for r in rows]


def station_convex_hull(client, where=US_FILTER):
    """Return Shapely geometry of the convex hull of matching stations."""
    row = client.query(
        f"SELECT wkt(groupConvexHull(location)) FROM ghcnd_stations WHERE {where}"
    )
    return wkt.loads(row.result_rows[0][0])


def station_hulls_by_state(client):
    """Return list of (state, shapely_geom) for per-state convex hulls."""
    rows = client.query(f"""
        SELECT state, wkt(groupConvexHull(location))
        FROM ghcnd_stations
        WHERE {US_FILTER}
        GROUP BY state ORDER BY state
    """).result_rows
    return [(r[0], wkt.loads(r[1])) for r in rows]
