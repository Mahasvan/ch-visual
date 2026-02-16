"""Six demo visualizations using ClickHouse geo aggregates."""

import random
import time
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from shapely.geometry import Polygon, LineString

import db
import plots

# Two overlapping squares used by polygon demos
SQUARE1 = [(0, 0), (10, 0), (10, 10), (0, 10)]
SQUARE2 = [(5, 5), (15, 5), (15, 15), (5, 15)]


def _polygon_demo(client, func, title, color):
    """Generic polygon-aggregate demo (union / intersection / convex hull)."""
    coords = [SQUARE1, SQUARE2]
    tbl = db.load_polygons(client, coords)
    result, wkt_str = db.aggregate_geom(client, tbl, func)
    print(f"  {func} → {wkt_str}")
    db.drop(client, tbl)
    plots.geom_figure(
        [Polygon(c) for c in coords], result, title,
        original_label="Square", result_color=color, result_label=f"{func} result",
    )


def demo_union(client):
    _polygon_demo(client, "groupPolygonUnion",
                  "groupPolygonUnion", "red")

def demo_intersection(client):
    _polygon_demo(client, "groupPolygonIntersection",
                  "groupPolygonIntersection", "green")

def demo_convex_hull_polygons(client):
    _polygon_demo(client, "groupConvexHull",
                  "groupConvexHull (Polygons)", "orange")


def demo_convex_hull_linestrings(client):
    lines = [
        [(0, 0), (5, 3), (10, 0)],
        [(2, 5), (8, 7), (12, 4)],
        [(1, 10), (6, 12), (11, 9)],
        [(3, 15), (7, 18), (9, 14)],
    ]
    tbl = db.load_linestrings(client, lines)
    result, wkt_str = db.aggregate_geom(client, tbl, "groupConvexHull")
    print(f"  groupConvexHull → {wkt_str}")
    db.drop(client, tbl)
    plots.geom_figure(
        [LineString(c) for c in lines], result,
        "groupConvexHull (LineStrings)",
        original_label="LineString", result_color="orange",
        result_label="groupConvexHull result",
    )


def demo_stations_hull(client):
    lons, lats = db.fetch_station_points(client)
    
    start = time.perf_counter()
    hull = db.station_convex_hull(client)
    elapsed = time.perf_counter() - start
    
    print(f"  {len(lons)} stations, hull has {len(hull.exterior.coords)} vertices")
    print(f"  Computed in {elapsed:.3f}s")

    fig, ax = plots.world_map()
    proj = ccrs.PlateCarree()
    ax.scatter(lons, lats, s=1, c="blue", alpha=0.3, transform=proj,
               label=f"Stations ({len(lons)})")
    plots.outline_polygon(ax, hull, transform=proj, color="red", lw=2,
                          label="groupConvexHull")
    plots.fill_polygon(ax, hull, transform=proj, alpha=0.15, fc="red")
    ax.legend(loc="lower left", fontsize=10)
    ax.set_title(f"GHCND Stations — groupConvexHull ({elapsed:.3f}s)", fontsize=14)
    fig.tight_layout()
    plt.show()


def demo_stations_hull_by_state(client):
    lons, lats = db.fetch_station_points(client)
    
    start = time.perf_counter()
    state_hulls = db.station_hulls_by_state(client)
    elapsed = time.perf_counter() - start
    
    print(f"  {len(lons)} stations, {len(state_hulls)} state hulls")
    print(f"  Computed in {elapsed:.3f}s")

    fig, ax = plots.world_map()
    proj = ccrs.PlateCarree()
    ax.scatter(lons, lats, s=1, c="black", alpha=0.2, transform=proj, zorder=5)

    # Randomize color assignment for each state
    color_assignment = {i: random.choice(plots.STATE_COLORS) for i in range(len(state_hulls))}

    for i, (_, hull) in enumerate(state_hulls):
        c = color_assignment[i]
        plots.outline_polygon(ax, hull, transform=proj, color=c, lw=1.5)
        plots.fill_polygon(ax, hull, transform=proj, alpha=0.2, fc=c)

    plots.state_legend(ax, len(lons))
    ax.set_title(
        f"GHCND Stations — groupConvexHull by State ({len(state_hulls)} states, {elapsed:.3f}s)",
        fontsize=14,
    )
    fig.tight_layout()
    plt.show()
