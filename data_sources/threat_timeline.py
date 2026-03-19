"""
Extended Predictive Threat Windows — 72-Hour Forward-Looking Coverage Forecasts
Propagates adversary ISR satellites forward in time to predict coverage windows
over strategic areas of interest.

No public tool provides 72-hour predictive adversary coverage timelines as a
dashboard feature. ExoAnalytic sells this commercially; we do it from OSINT.

Functions:
- predict_coverage_timeline     — 72hr timeline for a single AOI
- predict_all_hotspot_timelines — 72hr timeline for all 6 strategic hotspots
- get_coverage_density          — hourly adversary ISR pass density

Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

import httpx

from data_sources.celestrak import propagate_satellite, fetch_catalog
from data_sources.adversary_sats import identify_country, classify_satellite

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache: Dict[str, dict] = {}
_TIMELINE_TTL = 300   # 5 minutes
_DENSITY_TTL = 300    # 5 minutes

_ISR_DETECT_RADIUS_KM = 1500  # Typical ISR detection radius for 500km alt


def _cached(key: str, ttl: int) -> Optional[dict]:
    cached = _cache.get(key)
    if cached and (time.time() - cached["ts"]) < ttl:
        return cached["data"]
    return None


def _store(key: str, data: dict) -> dict:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# ---------------------------------------------------------------------------
# Haversine
# ---------------------------------------------------------------------------

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.asin(min(1.0, math.sqrt(a)))


def _elevation_angle(dist_km: float, alt_km: float) -> float:
    """Approximate elevation angle (degrees) from ground point to satellite.

    Uses simple geometry: tan(elev) = (alt - earth_curve) / ground_distance.
    Returns 0.0 if satellite is below horizon.
    """
    if dist_km <= 0:
        return 90.0
    # Account for Earth curvature
    R = 6371.0
    # Angle subtended at Earth center
    gamma = dist_km / R  # radians
    # Elevation angle from ground observer
    try:
        elev = math.degrees(
            math.atan2(
                (R + alt_km) * math.cos(gamma) - R,
                (R + alt_km) * math.sin(gamma),
            )
        )
    except (ValueError, ZeroDivisionError):
        elev = 0.0
    return max(0.0, elev)


# ---------------------------------------------------------------------------
# ISR-relevant adversary category filter
# ---------------------------------------------------------------------------

_ISR_CATEGORIES = frozenset([
    "military_isr", "sda_asat", "early_warning", "unknown",
])


# ---------------------------------------------------------------------------
# Strategic Hotspots (same as live_intel.py)
# ---------------------------------------------------------------------------

HOTSPOTS = [
    {"name": "Taiwan Strait", "lat": 23.5, "lng": 120.5},
    {"name": "South China Sea", "lat": 12.0, "lng": 115.0},
    {"name": "Baltic Sea", "lat": 57.0, "lng": 20.0},
    {"name": "Korean Peninsula", "lat": 38.0, "lng": 127.0},
    {"name": "Persian Gulf", "lat": 26.0, "lng": 52.0},
    {"name": "Arctic", "lat": 75.0, "lng": 40.0},
]


# ---------------------------------------------------------------------------
# Core: Predict Coverage Timeline
# ---------------------------------------------------------------------------

async def predict_coverage_timeline(
    client: httpx.AsyncClient,
    lat: float,
    lng: float,
    name: str = "Custom AOI",
    hours: int = 72,
    step_minutes: int = 30,
) -> dict:
    """Predict adversary ISR satellite coverage over a point for up to 72 hours.

    For each time step, propagates all adversary ISR sats and checks if any
    pass within detection range (1500 km). Builds a timeline of coverage
    windows with satellite identification, distance, and elevation.

    Returns structured timeline data for dashboard rendering.
    """
    cache_key = f"timeline_{lat:.1f}_{lng:.1f}_{hours}_{step_minutes}"
    cached = _cached(cache_key, _TIMELINE_TTL)
    if cached is not None:
        return cached

    catalog = await fetch_catalog(client, "active")
    now = datetime.now(timezone.utc)

    # Pre-filter: only adversary ISR-relevant sats
    adversary_gps = []  # type: List[tuple]
    for gp in catalog:
        obj_name = gp.get("OBJECT_NAME", "")
        country = identify_country(obj_name)
        if country is None:
            continue
        category = classify_satellite(obj_name, country)
        if category in _ISR_CATEGORIES:
            adversary_gps.append((gp, obj_name, country, category))

    # Time steps
    total_steps = int((hours * 60) / step_minutes) + 1
    time_steps = [now + timedelta(minutes=i * step_minutes) for i in range(total_steps)]

    # Track coverage windows per satellite
    # A "window" opens when a sat enters detection range and closes when it leaves
    coverage_windows = []  # type: List[dict]

    for gp, obj_name, country, category in adversary_gps:
        norad_id = int(gp.get("NORAD_CAT_ID", 0))
        in_range = False
        window_start = None  # type: Optional[datetime]
        min_dist = float("inf")
        max_elev = 0.0

        for dt in time_steps:
            pos = propagate_satellite(gp, dt)
            if pos is None:
                if in_range:
                    # Window closes
                    coverage_windows.append({
                        "satellite_name": obj_name,
                        "norad_id": norad_id,
                        "country": country,
                        "category": category,
                        "time_start": window_start.isoformat() if window_start else "",
                        "time_end": dt.isoformat(),
                        "duration_minutes": int((dt - window_start).total_seconds() / 60) if window_start else 0,
                        "min_distance_km": round(min_dist, 0),
                        "max_elevation_deg": round(max_elev, 1),
                    })
                    in_range = False
                    min_dist = float("inf")
                    max_elev = 0.0
                continue

            dist = _haversine_km(lat, lng, pos["lat"], pos["lng"])

            if dist <= _ISR_DETECT_RADIUS_KM:
                elev = _elevation_angle(dist, pos["alt_km"])
                if not in_range:
                    # Window opens
                    in_range = True
                    window_start = dt
                    min_dist = dist
                    max_elev = elev
                else:
                    min_dist = min(min_dist, dist)
                    max_elev = max(max_elev, elev)
            else:
                if in_range:
                    # Window closes
                    coverage_windows.append({
                        "satellite_name": obj_name,
                        "norad_id": norad_id,
                        "country": country,
                        "category": category,
                        "time_start": window_start.isoformat() if window_start else "",
                        "time_end": dt.isoformat(),
                        "duration_minutes": int((dt - window_start).total_seconds() / 60) if window_start else 0,
                        "min_distance_km": round(min_dist, 0),
                        "max_elevation_deg": round(max_elev, 1),
                    })
                    in_range = False
                    min_dist = float("inf")
                    max_elev = 0.0

        # Close any open window at end of timeline
        if in_range and window_start is not None:
            coverage_windows.append({
                "satellite_name": obj_name,
                "norad_id": norad_id,
                "country": country,
                "category": category,
                "time_start": window_start.isoformat(),
                "time_end": time_steps[-1].isoformat(),
                "duration_minutes": int((time_steps[-1] - window_start).total_seconds() / 60),
                "min_distance_km": round(min_dist, 0),
                "max_elevation_deg": round(max_elev, 1),
            })

    # Sort by start time
    coverage_windows.sort(key=lambda w: w["time_start"])

    # Compute simultaneous coverage peaks
    # For each time step, count how many sats are overhead simultaneously
    peak_simultaneous = 0
    peak_time = now.isoformat()

    for dt in time_steps:
        dt_iso = dt.isoformat()
        count = 0
        for w in coverage_windows:
            if w["time_start"] <= dt_iso <= w["time_end"]:
                count += 1
        if count > peak_simultaneous:
            peak_simultaneous = count
            peak_time = dt_iso

    # Country breakdown
    by_country = {}  # type: Dict[str, int]
    for w in coverage_windows:
        c = w["country"]
        by_country[c] = by_country.get(c, 0) + 1

    result = {
        "classification": "UNCLASSIFIED // OSINT",
        "area_of_interest": {"name": name, "lat": lat, "lng": lng},
        "prediction_window_hours": hours,
        "step_minutes": step_minutes,
        "generated_utc": now.isoformat(),
        "prediction_start": now.isoformat(),
        "prediction_end": time_steps[-1].isoformat(),
        "total_coverage_windows": len(coverage_windows),
        "peak_simultaneous_satellites": peak_simultaneous,
        "peak_simultaneous_time": peak_time,
        "windows_by_country": by_country,
        "adversary_isr_sats_evaluated": len(adversary_gps),
        "coverage_windows": coverage_windows,
    }

    return _store(cache_key, result)


# ---------------------------------------------------------------------------
# All Hotspot Timelines
# ---------------------------------------------------------------------------

async def predict_all_hotspot_timelines(client: httpx.AsyncClient) -> dict:
    """Run 72-hour coverage prediction for all 6 strategic hotspots.

    Returns all timelines plus comparative analysis showing which hotspot
    has the most adversary ISR coverage.
    """
    cached = _cached("all_hotspot_timelines", _TIMELINE_TTL)
    if cached is not None:
        return cached

    import asyncio

    tasks = [
        predict_coverage_timeline(client, hs["lat"], hs["lng"], hs["name"], hours=72)
        for hs in HOTSPOTS
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    timelines = []  # type: List[dict]
    for hs, result in zip(HOTSPOTS, results):
        if isinstance(result, Exception):
            timelines.append({
                "name": hs["name"],
                "lat": hs["lat"],
                "lng": hs["lng"],
                "error": str(result),
                "total_coverage_windows": 0,
            })
        else:
            timelines.append({
                "name": hs["name"],
                "lat": hs["lat"],
                "lng": hs["lng"],
                "total_coverage_windows": result.get("total_coverage_windows", 0),
                "peak_simultaneous_satellites": result.get("peak_simultaneous_satellites", 0),
                "peak_simultaneous_time": result.get("peak_simultaneous_time", ""),
                "windows_by_country": result.get("windows_by_country", {}),
                "coverage_windows": result.get("coverage_windows", []),
            })

    # Comparative analysis
    most_covered = max(
        timelines,
        key=lambda t: t.get("total_coverage_windows", 0),
        default=None,
    )
    highest_peak = max(
        timelines,
        key=lambda t: t.get("peak_simultaneous_satellites", 0),
        default=None,
    )

    now = datetime.now(timezone.utc)
    data = {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "prediction_window_hours": 72,
        "hotspot_count": len(HOTSPOTS),
        "most_covered_hotspot": most_covered.get("name", "N/A") if most_covered else "N/A",
        "most_covered_windows": most_covered.get("total_coverage_windows", 0) if most_covered else 0,
        "highest_peak_hotspot": highest_peak.get("name", "N/A") if highest_peak else "N/A",
        "highest_peak_simultaneous": highest_peak.get("peak_simultaneous_satellites", 0) if highest_peak else 0,
        "hotspots": timelines,
    }

    return _store("all_hotspot_timelines", data)


# ---------------------------------------------------------------------------
# Coverage Density (Hourly Heatmap)
# ---------------------------------------------------------------------------

async def get_coverage_density(
    client: httpx.AsyncClient,
    lat: float,
    lng: float,
    hours: int = 24,
) -> dict:
    """For each hour in the next N hours, count adversary ISR passes overhead.

    Returns an hourly density array suitable for heatmap rendering:
    [{hour: "2024-03-19T14:00Z", count: 3, nations: ["PRC", "CIS"]}, ...]
    """
    cache_key = f"density_{lat:.1f}_{lng:.1f}_{hours}"
    cached = _cached(cache_key, _DENSITY_TTL)
    if cached is not None:
        return cached

    catalog = await fetch_catalog(client, "active")
    now = datetime.now(timezone.utc)

    # Pre-filter adversary ISR sats
    adversary_gps = []  # type: List[tuple]
    for gp in catalog:
        obj_name = gp.get("OBJECT_NAME", "")
        country = identify_country(obj_name)
        if country is None:
            continue
        category = classify_satellite(obj_name, country)
        if category in _ISR_CATEGORIES:
            adversary_gps.append((gp, obj_name, country))

    # For each hour, check at 10-minute intervals within that hour
    density = []  # type: List[dict]

    for h in range(hours):
        hour_start = now + timedelta(hours=h)
        hour_label = hour_start.strftime("%Y-%m-%dT%H:00Z")
        sats_in_hour = set()  # type: set
        nations_in_hour = set()  # type: set

        # Check 6 time points within the hour (every 10 min)
        for m in range(0, 60, 10):
            check_time = hour_start + timedelta(minutes=m)
            for gp, obj_name, country in adversary_gps:
                norad_id = int(gp.get("NORAD_CAT_ID", 0))
                if norad_id in sats_in_hour:
                    continue  # Already counted this sat for this hour

                pos = propagate_satellite(gp, check_time)
                if pos is None:
                    continue

                dist = _haversine_km(lat, lng, pos["lat"], pos["lng"])
                if dist <= _ISR_DETECT_RADIUS_KM:
                    sats_in_hour.add(norad_id)
                    nations_in_hour.add(country)

        density.append({
            "hour": hour_label,
            "hour_offset": h,
            "satellite_count": len(sats_in_hour),
            "nations": sorted(nations_in_hour),
        })

    # Summary
    peak_hour = max(density, key=lambda d: d["satellite_count"], default=None)
    avg_count = sum(d["satellite_count"] for d in density) / max(len(density), 1)

    # Identify "gap" hours (zero coverage)
    gap_hours = [d["hour"] for d in density if d["satellite_count"] == 0]

    result = {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "area_of_interest": {"lat": lat, "lng": lng},
        "analysis_window_hours": hours,
        "peak_hour": peak_hour["hour"] if peak_hour else "N/A",
        "peak_satellite_count": peak_hour["satellite_count"] if peak_hour else 0,
        "average_hourly_count": round(avg_count, 1),
        "zero_coverage_hours": len(gap_hours),
        "gap_windows": gap_hours[:10],  # First 10 gaps
        "hourly_density": density,
    }

    return _store(cache_key, result)
