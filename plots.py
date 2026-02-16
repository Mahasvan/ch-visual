"""Matplotlib / Cartopy plotting utilities."""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Patch
from shapely.geometry import MultiPolygon, Polygon


def fill_polygon(ax, geom, transform=None, **kwargs):
    """Fill a Shapely Polygon or MultiPolygon on *ax*."""
    if isinstance(geom, MultiPolygon):
        for p in geom.geoms:
            fill_polygon(ax, p, transform=transform, **kwargs)
        return
    x, y = geom.exterior.xy
    kw = dict(kwargs)
    if transform:
        kw["transform"] = transform
    ax.fill(x, y, **kw)


def outline_polygon(ax, geom, transform=None, **kwargs):
    """Draw the outline of a Shapely Polygon or MultiPolygon."""
    if isinstance(geom, MultiPolygon):
        for p in geom.geoms:
            outline_polygon(ax, p, transform=transform, **kwargs)
        return
    x, y = geom.exterior.xy
    kw = dict(kwargs)
    if transform:
        kw["transform"] = transform
    ax.plot(x, y, **kw)


# ------------------------------------------------------------------
# Simple geometry figure (for polygon / linestring demos)
# ------------------------------------------------------------------

def geom_figure(originals, result, title, original_label="Polygon",
                result_color="red", result_label="Result"):
    """Plot original geometries + an aggregate result on a plain axes."""
    fig, ax = plt.subplots()

    # originals
    for i, g in enumerate(originals):
        if isinstance(g, (Polygon, MultiPolygon)):
            fill_polygon(ax, g, alpha=0.3, fc="blue", ec="black", lw=1,
                         label=f"{original_label} {i+1}")
        else:  # LineString
            xs, ys = zip(*g.coords)
            ax.plot(xs, ys, "b-o", lw=2, ms=5, label=f"{original_label} {i+1}")

    # result
    fill_polygon(ax, result, alpha=0.45, fc=result_color, ec="dark" + result_color
                 if "dark" + result_color in ("darkred", "darkorange", "darkgreen")
                 else result_color, lw=3, label=result_label)

    ax.set_aspect("equal", "box")
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
    ax.set_title(title)
    ax.grid(True)
    fig.tight_layout()
    plt.show()


# ------------------------------------------------------------------
# World-map figure (for station demos)
# ------------------------------------------------------------------

def world_map(figsize=(16, 9)):
    """Return (fig, ax) with Cartopy PlateCarree projection and base layers."""
    fig, ax = plt.subplots(figsize=figsize,
                           subplot_kw={"projection": ccrs.PlateCarree()})
    ax.set_global()
    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.OCEAN, facecolor="lightblue")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, linestyle="--")
    ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    return fig, ax


STATE_COLORS = [
    "#e41a1c", "#377eb8", "#4daf4a", "#ff7f00",
    "#984ea3", "#ff7f00", "#a65628", "#f781bf",
    "#999999", "#66c2a5"
]


def state_legend(ax, n_stations):
    """Add station count label to legend (no color patches)."""
    ax.scatter([], [], s=10, c="black", alpha=0.5,
               label=f"Stations ({n_stations})", transform=ax.transAxes)
    ax.legend(loc="lower left", fontsize=9)
