"""Geo data for the coverage-map widget on service-area pages.

Sources:
  - City coords + distance-from-Waterloo: src/data/city-research.json
  - State centers + bounds: hardcoded below (well-known geographic centers)
  - Waterloo, IA origin: matches homepage LocalBusiness schema (42.51389, -92.34611)
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Waterloo, IA — our home base, shown as the origin pin on every map.
WATERLOO = {
    "name":   "Waterloo, IA",
    "coords": [42.51389, -92.34611],
    "label":  "Midwest CNC Services (home base)",
}


# State geographic centers + viewport bounds for the coverage map.
# Bounds are [[south, west], [north, east]] — Leaflet fitBounds format.
STATE_GEO = {
    "iowa": {
        "name":   "Iowa",
        "center": [42.0046, -93.5000],
        "bounds": [[40.3754, -96.6395], [43.5012, -90.1401]],
    },
    "illinois": {
        "name":   "Illinois",
        "center": [40.0379, -89.0000],
        "bounds": [[36.9700, -91.5131], [42.5083, -87.0199]],
    },
    "minnesota": {
        "name":   "Minnesota",
        "center": [46.2807, -94.3053],
        "bounds": [[43.4994, -97.2389], [49.3844, -89.4919]],
    },
    "wisconsin": {
        "name":   "Wisconsin",
        "center": [44.2685, -89.6385],
        "bounds": [[42.4919, -92.8881], [47.0808, -86.2492]],
    },
    "nebraska": {
        "name":   "Nebraska",
        "center": [41.5378, -99.7951],
        "bounds": [[40.0000, -104.0532], [43.0017, -95.3083]],
    },
    "missouri": {
        "name":   "Missouri",
        "center": [38.4561, -92.2884],
        "bounds": [[35.9957, -95.7740], [40.6136, -89.0988]],
    },
    "texas": {
        "name":   "Texas",
        "center": [31.0545, -97.5635],
        "bounds": [[25.8371, -106.6456], [36.5007, -93.5083]],
    },
}


def _load_city_research():
    """Read city-research.json, return the cities dict."""
    p = os.path.join(REPO, "src", "data", "city-research.json")
    with open(p) as f:
        d = json.load(f)
    return d.get("cities", {})


def cities_for_state(state_slug):
    """Return the list of served cities in {state_slug}.
    Each entry: {name, slug, coords, url, distance_miles, decision}.
    Filters out CONSOLIDATE cities (no own page)."""
    cities = _load_city_research()
    out = []
    for slug, c in cities.items():
        if c.get("state_slug") != state_slug:
            continue
        if c.get("decision") == "CONSOLIDATE":
            continue
        out.append({
            "name":          c["name"],
            "slug":          slug,
            "coords":        c.get("coords"),
            "url":           f"/service-area/{slug}/",
            "distance_miles":(c.get("distance_from_waterloo") or {}).get("miles"),
        })
    return out


def all_served_cities():
    """Return every ENRICH-decision city across all 7 states.
    Used by the hub overview map."""
    cities = _load_city_research()
    out = []
    for slug, c in cities.items():
        if c.get("decision") == "CONSOLIDATE":
            continue
        out.append({
            "name":          c["name"],
            "state":         c["state"],
            "state_slug":    c["state_slug"],
            "slug":          slug,
            "coords":        c.get("coords"),
            "url":           f"/service-area/{slug}/",
            "distance_miles":(c.get("distance_from_waterloo") or {}).get("miles"),
        })
    return out


def city_geo(city_slug):
    """Return geo info for a single city, or None."""
    cities = _load_city_research()
    c = cities.get(city_slug)
    if not c:
        return None
    return {
        "name":          c["name"],
        "state":         c["state"],
        "state_slug":    c["state_slug"],
        "slug":          city_slug,
        "coords":        c.get("coords"),
        "distance_miles":(c.get("distance_from_waterloo") or {}).get("miles"),
        "distance_hours":(c.get("distance_from_waterloo") or {}).get("hours"),
    }
