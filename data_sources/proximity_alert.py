"""
FVEY Asset Proximity Alerting System
Cross-references adversary satellite positions against FVEY military satellite
positions and alerts on close approaches (RPO, co-orbital maneuvers).

No public tool (LeoLabs, ExoAnalytic, 18th SDS public data) provides this as
a real-time dashboard feature.

Functions:
- check_proximity_alerts   — pairwise adversary-vs-FVEY distance check
- get_proximity_history    — rolling history of close-approach events

Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx

from data_sources.celestrak import propagate_satellite, fetch_catalog
from data_sources.adversary_sats import (
    identify_country,
    identify_fvey_country,
    classify_satellite,
    classify_fvey_satellite,
)

# ---------------------------------------------------------------------------
# FVEY military satellite name patterns to specifically watch
# ---------------------------------------------------------------------------
import re

_FVEY_MIL_PATTERN = re.compile(
    r"GPS|NAVSTAR|SBIRS|USA[ -]\d|NROL|WGS|GSSAP|AEHF|MUOS|DSP|"
    r"MILSTAR|SKYNET|SAPPHIRE|NEOSSAT|SBSS|"
    r"STSS|MENTOR|ORION|TRUMPET|ONYX|LACROSSE",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache: Dict[str, dict] = {}
_PROXIMITY_TTL = 120  # 2 minutes

# Rolling history — persists across requests (in-memory, max 50 events)
_proximity_history: List[dict] = []
_MAX_HISTORY = 50


def _cached(key: str, ttl: int) -> Optional[dict]:
    cached = _cache.get(key)
    if cached and (time.time() - cached["ts"]) < ttl:
        return cached["data"]
    return None


def _store(key: str, data: dict) -> dict:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# ---------------------------------------------------------------------------
# Haversine distance (ground track, km)
# ---------------------------------------------------------------------------

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two lat/lng points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.asin(min(1.0, math.sqrt(a)))


def _3d_distance_km(
    lat1: float, lng1: float, alt1: float,
    lat2: float, lng2: float, alt2: float,
) -> float:
    """Approximate 3-D distance between two satellites.

    Converts geodetic (lat, lng, alt) to ECEF, then Euclidean distance.
    More accurate than haversine for satellites at different altitudes.
    """
    R = 6371.0

    def _to_ecef(lat: float, lng: float, alt: float):
        r = R + alt
        lat_r = math.radians(lat)
        lng_r = math.radians(lng)
        x = r * math.cos(lat_r) * math.cos(lng_r)
        y = r * math.cos(lat_r) * math.sin(lng_r)
        z = r * math.sin(lat_r)
        return x, y, z

    x1, y1, z1 = _to_ecef(lat1, lng1, alt1)
    x2, y2, z2 = _to_ecef(lat2, lng2, alt2)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


# ---------------------------------------------------------------------------
# Threat assessment
# ---------------------------------------------------------------------------

def _assess_threat(distance_km: float) -> str:
    """Classify the proximity event threat level."""
    if distance_km < 50:
        return "CRITICAL — POTENTIAL RPO / INSPECTION"
    if distance_km < 100:
        return "RPO"
    if distance_km < 200:
        return "CLOSE APPROACH — HIGH"
    if distance_km < 500:
        return "CLOSE APPROACH"
    return "MONITORING"


# ---------------------------------------------------------------------------
# Core: Proximity Alert Check
# ---------------------------------------------------------------------------

async def check_proximity_alerts(
    client: httpx.AsyncClient,
    threshold_km: float = 500,
) -> dict:
    """Check all FVEY military satellites against all adversary satellites.

    For each pair within threshold_km, generate an alert with:
    - fvey_sat: name, norad_id, country, category, lat, lng, alt
    - adversary_sat: name, norad_id, country, category, lat, lng, alt
    - distance_km: 3-D distance between them
    - threat_assessment: RPO / CLOSE APPROACH / MONITORING

    Returns dict with alerts list, summary stats, and timestamp.
    """
    cached = _cached("proximity_alerts", _PROXIMITY_TTL)
    if cached is not None:
        return cached

    catalog = await fetch_catalog(client, "active")
    now = datetime.now(timezone.utc)

    # ---- Phase 1: Identify and propagate FVEY military satellites ----
    fvey_sats = []  # type: List[dict]
    adversary_sats = []  # type: List[dict]

    for gp in catalog:
        name = gp.get("OBJECT_NAME", "")
        norad_id = int(gp.get("NORAD_CAT_ID", 0))

        # Check if it's a FVEY military sat
        if _FVEY_MIL_PATTERN.search(name):
            fvey_country = identify_fvey_country(name)
            if fvey_country is None:
                fvey_country = "US"  # Default for military patterns
            pos = propagate_satellite(gp, now)
            if pos is not None:
                fvey_sats.append({
                    "norad_id": norad_id,
                    "name": name,
                    "country": fvey_country,
                    "category": classify_fvey_satellite(name),
                    "lat": pos["lat"],
                    "lng": pos["lng"],
                    "alt_km": pos["alt_km"],
                })
            continue

        # Check if it's an adversary sat
        adv_country = identify_country(name)
        if adv_country is not None:
            pos = propagate_satellite(gp, now)
            if pos is not None:
                adversary_sats.append({
                    "norad_id": norad_id,
                    "name": name,
                    "country": adv_country,
                    "category": classify_satellite(name, adv_country),
                    "lat": pos["lat"],
                    "lng": pos["lng"],
                    "alt_km": pos["alt_km"],
                })

    # ---- Phase 2: Pairwise distance check (O(n*m)) ----
    alerts = []  # type: List[dict]

    for fvey in fvey_sats:
        for adv in adversary_sats:
            # Quick latitude pre-filter — skip if > ~5 degrees apart
            # (at LEO, 5 degrees latitude ~ 555 km ground distance)
            if abs(fvey["lat"] - adv["lat"]) > 8:
                continue
            if abs(fvey["lng"] - adv["lng"]) > 8:
                continue

            dist = _3d_distance_km(
                fvey["lat"], fvey["lng"], fvey["alt_km"],
                adv["lat"], adv["lng"], adv["alt_km"],
            )

            if dist <= threshold_km:
                alert = {
                    "fvey_sat": {
                        "name": fvey["name"],
                        "norad_id": fvey["norad_id"],
                        "country": fvey["country"],
                        "category": fvey["category"],
                        "lat": fvey["lat"],
                        "lng": fvey["lng"],
                        "alt_km": fvey["alt_km"],
                    },
                    "adversary_sat": {
                        "name": adv["name"],
                        "norad_id": adv["norad_id"],
                        "country": adv["country"],
                        "category": adv["category"],
                        "lat": adv["lat"],
                        "lng": adv["lng"],
                        "alt_km": adv["alt_km"],
                    },
                    "distance_km": round(dist, 1),
                    "threat_assessment": _assess_threat(dist),
                    "detected_utc": now.isoformat(),
                }
                alerts.append(alert)

    # Sort by distance (closest first — most urgent)
    alerts.sort(key=lambda a: a["distance_km"])

    # ---- Phase 3: Append new events to rolling history ----
    global _proximity_history
    for alert in alerts:
        _proximity_history.append(alert)
    # Trim to max size
    if len(_proximity_history) > _MAX_HISTORY:
        _proximity_history = _proximity_history[-_MAX_HISTORY:]

    # ---- Summary stats ----
    rpo_count = sum(1 for a in alerts if "RPO" in a["threat_assessment"])
    close_count = sum(1 for a in alerts if "CLOSE APPROACH" in a["threat_assessment"])

    by_adversary_country = {}  # type: Dict[str, int]
    for a in alerts:
        c = a["adversary_sat"]["country"]
        by_adversary_country[c] = by_adversary_country.get(c, 0) + 1

    by_fvey_category = {}  # type: Dict[str, int]
    for a in alerts:
        cat = a["fvey_sat"]["category"]
        by_fvey_category[cat] = by_fvey_category.get(cat, 0) + 1

    result = {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "threshold_km": threshold_km,
        "fvey_military_sats_tracked": len(fvey_sats),
        "adversary_sats_tracked": len(adversary_sats),
        "total_alerts": len(alerts),
        "rpo_events": rpo_count,
        "close_approach_events": close_count,
        "alerts_by_adversary_nation": by_adversary_country,
        "alerts_by_fvey_category": by_fvey_category,
        "alerts": alerts,
    }

    return _store("proximity_alerts", result)


# ---------------------------------------------------------------------------
# Proximity History
# ---------------------------------------------------------------------------

async def get_proximity_history(client: httpx.AsyncClient) -> dict:
    """Return the rolling history of proximity events.

    Automatically triggers a fresh check if no history exists yet.
    Returns up to the last 50 events with timestamps.
    """
    # If history is empty, trigger a fresh scan
    if not _proximity_history:
        await check_proximity_alerts(client)

    now = datetime.now(timezone.utc)
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "total_events_in_history": len(_proximity_history),
        "max_history_size": _MAX_HISTORY,
        "events": list(_proximity_history),
    }
