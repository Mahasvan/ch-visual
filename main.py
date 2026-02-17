"""Entry point — run all six ClickHouse geo-visualization demos."""

import db, demos

DEMOS = [
    ("groupPolygonUnion",              demos.demo_union),
    ("groupPolygonIntersection",       demos.demo_intersection),
    ("groupConvexHull (Polygons)",     demos.demo_convex_hull_polygons),
    ("groupConvexHull (LineStrings)",  demos.demo_convex_hull_linestrings),
    ("Station Convex Hull",           demos.demo_stations_hull),
    ("Station Hulls by State",        demos.demo_stations_hull_by_state),
    ("Station Hulls by Country",      demos.demo_stations_hull_by_country),
]

if __name__ == "__main__":
    client = db.connect()
    for title, fn in DEMOS:
        print(f"\n=== {title} ===")
        fn(client)

