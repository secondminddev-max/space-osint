"""
Real-time Intelligence Generation Engine
Produces automated intelligence assessments by combining live satellite data,
space weather, launch activity, and research feeds.

Functions:
- generate_situation_report  — live SITREP
- generate_daily_brief       — daily intelligence brief
- get_area_of_interest_coverage — adversary ISR sat coverage for an AOI
- get_hotspot_analysis       — pre-computed coverage for strategic hotspots

Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

import httpx

from data_sources.celestrak import propagate_satellite, fetch_catalog
from data_sources.adversary_sats import (
    identify_country,
    classify_satellite,
    get_adversary_stats,
)
from data_sources.space_weather import fetch_weather_composite
from data_sources.launches import fetch_launches
from data_sources import researcher

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache: Dict[str, dict] = {}
_SITREP_TTL = 120   # 2 minutes
_BRIEF_TTL = 600    # 10 minutes
_AOI_TTL = 120       # 2 minutes
_HOTSPOT_TTL = 120   # 2 minutes

_ISR_DETECT_RADIUS_KM = 1500  # Typical ISR swath for 500 km altitude


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
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# Threat Level Assessment
# ---------------------------------------------------------------------------

def _assess_threat_level(
    weather: Optional[dict],
    adversary_sats_over_hotspots: int,
    active_alerts: int,
    recent_launches: int,
) -> str:
    """Simple rule-based threat level from composite indicators."""
    score = 0

    # Space weather factor
    if weather:
        kp = weather.get("kp_current")
        if kp is not None:
            if kp >= 7:
                score += 3  # Major storm — degrades ISR
            elif kp >= 5:
                score += 2
            elif kp >= 4:
                score += 1

        alerts = weather.get("alerts", [])
        score += min(len(alerts), 3)

    # Adversary presence
    if adversary_sats_over_hotspots > 20:
        score += 3
    elif adversary_sats_over_hotspots > 10:
        score += 2
    elif adversary_sats_over_hotspots > 5:
        score += 1

    # Active SWPC alerts
    score += min(active_alerts, 2)

    # Recent adversary launch activity
    score += min(recent_launches, 2)

    if score >= 8:
        return "CRITICAL"
    if score >= 5:
        return "HIGH"
    if score >= 3:
        return "ELEVATED"
    return "GUARDED"


# ---------------------------------------------------------------------------
# Area of Interest Coverage
# ---------------------------------------------------------------------------

async def get_area_of_interest_coverage(
    client: httpx.AsyncClient,
    lat: float,
    lng: float,
    radius_km: float = 1500,
) -> dict:
    """Check which adversary ISR sats will pass over an AOI in the next 2 hours.

    Uses SGP4 propagation to check sub-satellite points against the AOI.
    """
    cache_key = f"aoi_{lat:.1f}_{lng:.1f}_{radius_km:.0f}"
    cached = _cached(cache_key, _AOI_TTL)
    if cached is not None:
        return cached

    catalog = await fetch_catalog(client, "active")
    now = datetime.now(timezone.utc)

    # Pre-filter: only adversary sats (PRC, CIS, NKOR, IRAN)
    adversary_gps = []
    for gp in catalog:
        name = gp.get("OBJECT_NAME", "")
        country = identify_country(name)
        if country:
            adversary_gps.append((gp, name, country))

    # Check current position + propagate forward in 10-minute steps for 2 hours
    steps = list(range(0, 121, 10))  # 0, 10, 20, ... 120 minutes
    passes = []  # type: List[dict]
    seen_ids = set()  # type: set

    for gp, name, country in adversary_gps:
        category = classify_satellite(name, country)
        # Focus on ISR-relevant categories
        if category not in ("military_isr", "sda_asat", "early_warning", "unknown"):
            continue

        for step_min in steps:
            dt = now + timedelta(minutes=step_min)
            pos = propagate_satellite(gp, dt)
            if pos is None:
                continue

            dist = _haversine_km(lat, lng, pos["lat"], pos["lng"])
            if dist <= radius_km:
                norad_id = int(gp.get("NORAD_CAT_ID", 0))
                if norad_id not in seen_ids:
                    seen_ids.add(norad_id)
                    passes.append({
                        "norad_id": norad_id,
                        "name": name,
                        "country": country,
                        "category": category,
                        "closest_approach_min": step_min,
                        "distance_km": round(dist, 0),
                        "lat": pos["lat"],
                        "lng": pos["lng"],
                        "alt_km": pos["alt_km"],
                    })
                break  # Found first pass for this sat, move to next

    passes.sort(key=lambda p: p["closest_approach_min"])

    result = {
        "area_of_interest": {"lat": lat, "lng": lng, "radius_km": radius_km},
        "window_hours": 2,
        "generated_utc": now.isoformat(),
        "total_adversary_passes": len(passes),
        "passes_by_country": _count_by(passes, "country"),
        "passes_by_category": _count_by(passes, "category"),
        "passes": passes,
    }

    return _store(cache_key, result)


def _count_by(items: List[dict], key: str) -> Dict[str, int]:
    counts = {}  # type: Dict[str, int]
    for item in items:
        val = item.get(key, "unknown")
        counts[val] = counts.get(val, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Hotspot Analysis
# ---------------------------------------------------------------------------

_HOTSPOTS = [
    {"name": "Taiwan Strait", "lat": 23.5, "lng": 120.5},
    {"name": "South China Sea", "lat": 12.0, "lng": 115.0},
    {"name": "Baltic Sea", "lat": 57.0, "lng": 20.0},
    {"name": "Korean Peninsula", "lat": 38.0, "lng": 127.0},
    {"name": "Persian Gulf", "lat": 26.0, "lng": 52.0},
    {"name": "Arctic", "lat": 75.0, "lng": 40.0},
]


async def get_hotspot_analysis(client: httpx.AsyncClient) -> dict:
    """Pre-computed adversary ISR coverage analysis for key strategic areas."""
    cached = _cached("hotspots", _HOTSPOT_TTL)
    if cached is not None:
        return cached

    import asyncio
    tasks = [
        get_area_of_interest_coverage(client, hs["lat"], hs["lng"], _ISR_DETECT_RADIUS_KM)
        for hs in _HOTSPOTS
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    hotspot_reports = []
    for hs, result in zip(_HOTSPOTS, results):
        if isinstance(result, Exception):
            hotspot_reports.append({
                "name": hs["name"],
                "lat": hs["lat"],
                "lng": hs["lng"],
                "error": str(result),
            })
        else:
            hotspot_reports.append({
                "name": hs["name"],
                "lat": hs["lat"],
                "lng": hs["lng"],
                "total_adversary_passes": result.get("total_adversary_passes", 0),
                "passes_by_country": result.get("passes_by_country", {}),
                "passes_by_category": result.get("passes_by_category", {}),
                "top_threats": result.get("passes", [])[:5],
            })

    # Overall assessment
    total_passes = sum(
        r.get("total_adversary_passes", 0) for r in hotspot_reports if isinstance(r, dict)
    )
    most_covered = max(
        hotspot_reports,
        key=lambda r: r.get("total_adversary_passes", 0),
        default=None,
    )

    data = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "detection_radius_km": _ISR_DETECT_RADIUS_KM,
        "window_hours": 2,
        "total_passes_all_hotspots": total_passes,
        "most_covered_area": most_covered.get("name", "N/A") if most_covered else "N/A",
        "hotspots": hotspot_reports,
    }

    return _store("hotspots", data)


# ---------------------------------------------------------------------------
# Situation Report (SITREP)
# ---------------------------------------------------------------------------

async def generate_situation_report(client: httpx.AsyncClient) -> dict:
    """Generate a live situation report combining all intelligence sources."""
    cached = _cached("sitrep", _SITREP_TTL)
    if cached is not None:
        return cached

    import asyncio

    # Gather data concurrently
    weather_task = fetch_weather_composite(client)
    launches_task = fetch_launches(client)
    stats_task = get_adversary_stats(client)
    # Check Taiwan Strait as primary hotspot
    taiwan_task = get_area_of_interest_coverage(client, 23.5, 120.5, _ISR_DETECT_RADIUS_KM)
    scs_task = get_area_of_interest_coverage(client, 12.0, 115.0, _ISR_DETECT_RADIUS_KM)

    weather, launches_data, adv_stats, taiwan_cov, scs_cov = await asyncio.gather(
        weather_task, launches_task, stats_task, taiwan_task, scs_task,
        return_exceptions=True,
    )

    # Handle exceptions gracefully
    if isinstance(weather, Exception):
        weather = {}
    if isinstance(launches_data, Exception):
        launches_data = []
    if isinstance(adv_stats, Exception):
        adv_stats = {}
    if isinstance(taiwan_cov, Exception):
        taiwan_cov = {"total_adversary_passes": 0}
    if isinstance(scs_cov, Exception):
        scs_cov = {"total_adversary_passes": 0}

    now = datetime.now(timezone.utc)

    # Count adversary sats over hotspots
    hotspot_count = (
        taiwan_cov.get("total_adversary_passes", 0)
        + scs_cov.get("total_adversary_passes", 0)
    )

    # Count recent adversary launches
    adversary_launch_count = 0
    for launch in launches_data:
        provider = (launch.get("provider") or "").lower()
        if any(kw in provider for kw in ["casc", "china", "roscosmos", "russia", "iran", "dprk", "korea"]):
            adversary_launch_count += 1

    # Active SWPC alerts
    alert_count = len(weather.get("alerts", [])) if isinstance(weather, dict) else 0

    threat_level = _assess_threat_level(
        weather if isinstance(weather, dict) else None,
        hotspot_count,
        alert_count,
        adversary_launch_count,
    )

    # Build key events
    key_events = []

    # Space weather events
    if isinstance(weather, dict):
        kp = weather.get("kp_current")
        if kp is not None and kp >= 4:
            key_events.append({
                "type": "SPACE_WEATHER",
                "severity": "HIGH" if kp >= 6 else "ELEVATED",
                "description": f"Kp index at {kp} — geomagnetic storm conditions may degrade satellite operations",
            })

        wind_speed = weather.get("solar_wind_speed")
        if wind_speed is not None and wind_speed > 600:
            key_events.append({
                "type": "SPACE_WEATHER",
                "severity": "ELEVATED",
                "description": f"Solar wind speed elevated at {wind_speed} km/s",
            })

    # Taiwan Strait coverage
    tw_passes = taiwan_cov.get("total_adversary_passes", 0)
    if tw_passes > 0:
        tw_by_country = taiwan_cov.get("passes_by_country", {})
        key_events.append({
            "type": "ADVERSARY_ISR",
            "severity": "HIGH" if tw_passes > 5 else "ELEVATED",
            "description": (
                f"{tw_passes} adversary ISR satellites covering Taiwan Strait "
                f"in next 2 hours — {tw_by_country}"
            ),
        })

    # South China Sea coverage
    scs_passes = scs_cov.get("total_adversary_passes", 0)
    if scs_passes > 0:
        scs_by_country = scs_cov.get("passes_by_country", {})
        key_events.append({
            "type": "ADVERSARY_ISR",
            "severity": "HIGH" if scs_passes > 5 else "ELEVATED",
            "description": (
                f"{scs_passes} adversary ISR satellites covering South China Sea "
                f"in next 2 hours — {scs_by_country}"
            ),
        })

    # Upcoming adversary launches
    for launch in launches_data[:5]:
        provider = (launch.get("provider") or "").lower()
        if any(kw in provider for kw in ["casc", "china", "roscosmos", "russia"]):
            key_events.append({
                "type": "ADVERSARY_LAUNCH",
                "severity": "INFO",
                "description": f"Upcoming adversary launch: {launch.get('name', 'Unknown')} — {launch.get('net', 'TBD')}",
            })

    # Space weather impact assessment
    weather_impact = "NOMINAL"
    if isinstance(weather, dict):
        kp = weather.get("kp_current")
        if kp is not None:
            if kp >= 7:
                weather_impact = "SEVERE — HF blackout, satellite drag increase, GPS degradation likely"
            elif kp >= 5:
                weather_impact = "MODERATE — Possible GPS accuracy reduction, increased LEO satellite drag"
            elif kp >= 4:
                weather_impact = "MINOR — Marginal impact on HF propagation"

    # Assessment text
    prc_total = 0
    cis_total = 0
    if isinstance(adv_stats, dict):
        prc_data = adv_stats.get("PRC", {})
        cis_data = adv_stats.get("CIS", {})
        prc_total = prc_data.get("total", 0) if isinstance(prc_data, dict) else 0
        cis_total = cis_data.get("total", 0) if isinstance(cis_data, dict) else 0

    assessment = (
        f"FVEY Space OSINT SITREP — {now.strftime('%d %b %Y %H:%M')}Z. "
        f"Threat level: {threat_level}. "
        f"Tracking {prc_total} PRC and {cis_total} Russian satellites. "
        f"{tw_passes} adversary ISR assets covering Taiwan Strait, "
        f"{scs_passes} covering South China Sea (next 2hr window). "
        f"Space weather impact: {weather_impact}. "
        f"{adversary_launch_count} adversary launches in upcoming manifest."
    )

    sitrep = {
        "classification": "UNCLASSIFIED // OSINT",
        "timestamp": now.isoformat(),
        "threat_level": threat_level,
        "key_events": key_events,
        "assessment": assessment,
        "space_weather_impact": weather_impact,
        "adversary_satellite_totals": {
            "PRC": prc_total,
            "CIS": cis_total,
        },
        "hotspot_coverage": {
            "taiwan_strait": tw_passes,
            "south_china_sea": scs_passes,
        },
        "upcoming_adversary_launches": adversary_launch_count,
        "active_swpc_alerts": alert_count,
    }

    return _store("sitrep", sitrep)


# ---------------------------------------------------------------------------
# Daily Intelligence Brief
# ---------------------------------------------------------------------------

async def generate_daily_brief(client: httpx.AsyncClient) -> dict:
    """Generate a comprehensive daily intelligence brief."""
    cached = _cached("daily_brief", _BRIEF_TTL)
    if cached is not None:
        return cached

    import asyncio

    weather_task = fetch_weather_composite(client)
    launches_task = fetch_launches(client)
    stats_task = get_adversary_stats(client)
    research_task = researcher.fetch_research_feed(client)
    policy_task = researcher.fetch_policy_updates(client)
    hotspot_task = get_hotspot_analysis(client)

    weather, launches_data, adv_stats, research_feed, policy_docs, hotspots = await asyncio.gather(
        weather_task, launches_task, stats_task, research_task, policy_task, hotspot_task,
        return_exceptions=True,
    )

    # Handle exceptions
    if isinstance(weather, Exception):
        weather = {}
    if isinstance(launches_data, Exception):
        launches_data = []
    if isinstance(adv_stats, Exception):
        adv_stats = {}
    if isinstance(research_feed, Exception):
        research_feed = []
    if isinstance(policy_docs, Exception):
        policy_docs = []
    if isinstance(hotspots, Exception):
        hotspots = {}

    now = datetime.now(timezone.utc)

    # Section 1: Adversary Orbital Activity
    prc_stats = adv_stats.get("PRC", {}) if isinstance(adv_stats, dict) else {}
    cis_stats = adv_stats.get("CIS", {}) if isinstance(adv_stats, dict) else {}
    nkor_stats = adv_stats.get("NKOR", {}) if isinstance(adv_stats, dict) else {}
    iran_stats = adv_stats.get("IRAN", {}) if isinstance(adv_stats, dict) else {}

    orbital_summary = {
        "PRC": {
            "total": prc_stats.get("total", 0) if isinstance(prc_stats, dict) else 0,
            "military_isr": prc_stats.get("military_isr", 0) if isinstance(prc_stats, dict) else 0,
            "navigation": prc_stats.get("navigation", 0) if isinstance(prc_stats, dict) else 0,
        },
        "Russia": {
            "total": cis_stats.get("total", 0) if isinstance(cis_stats, dict) else 0,
            "military_isr": cis_stats.get("military_isr", 0) if isinstance(cis_stats, dict) else 0,
            "navigation": cis_stats.get("navigation", 0) if isinstance(cis_stats, dict) else 0,
        },
        "DPRK": {
            "total": nkor_stats.get("total", 0) if isinstance(nkor_stats, dict) else 0,
        },
        "Iran": {
            "total": iran_stats.get("total", 0) if isinstance(iran_stats, dict) else 0,
        },
    }

    # Section 2: Upcoming Launches
    adversary_launches = []
    fvey_launches = []
    for launch in launches_data:
        provider = (launch.get("provider") or "").lower()
        entry = {
            "name": launch.get("name", ""),
            "net": launch.get("net", ""),
            "provider": launch.get("provider", ""),
            "pad": launch.get("pad_location", ""),
        }
        if any(kw in provider for kw in ["casc", "china", "roscosmos", "russia", "iran", "dprk", "korea"]):
            adversary_launches.append(entry)
        elif any(kw in provider for kw in ["spacex", "ula", "rocket lab", "northrop", "blue origin", "arianespace"]):
            fvey_launches.append(entry)

    # Section 3: Space Weather Forecast
    weather_section = {}
    if isinstance(weather, dict):
        weather_section = {
            "kp_current": weather.get("kp_current"),
            "solar_wind_speed": weather.get("solar_wind_speed"),
            "bt": weather.get("bt"),
            "bz": weather.get("bz"),
            "sfi": weather.get("sfi"),
            "scales": weather.get("scales", {}),
            "alert_count": len(weather.get("alerts", [])),
            "impact_assessment": _weather_forecast_text(weather),
        }

    # Section 4: Policy / Diplomatic
    policy_section = []
    if isinstance(policy_docs, list):
        for doc in policy_docs[:5]:
            policy_section.append({
                "title": doc.get("title", ""),
                "source": doc.get("source", ""),
                "published_at": doc.get("published_at", ""),
                "url": doc.get("url", ""),
            })

    # Section 5: Research highlights
    research_highlights = []
    if isinstance(research_feed, list):
        for item in research_feed[:10]:
            research_highlights.append({
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "relevance_tag": item.get("relevance_tag", ""),
                "url": item.get("url", ""),
            })

    # Section 6: Watch Items
    watch_items = [
        "Monitor PRC Yaogan constellation for new launches and orbital adjustments",
        "Track Russian inspector satellite activity (Cosmos 2558 and successors)",
        "SWPC alerts for geomagnetic storm watch — potential ISR degradation",
    ]

    # Add specific watch items based on data
    if isinstance(hotspots, dict):
        most_covered = hotspots.get("most_covered_area", "")
        total_hp = hotspots.get("total_passes_all_hotspots", 0)
        if total_hp > 10:
            watch_items.append(
                f"Elevated adversary ISR activity: {total_hp} satellite passes across "
                f"strategic hotspots — highest coverage at {most_covered}"
            )

    for launch in adversary_launches[:2]:
        watch_items.append(f"Upcoming adversary launch: {launch['name']} — {launch['net']}")

    brief = {
        "classification": "UNCLASSIFIED // OSINT",
        "brief_date": now.strftime("%Y-%m-%d"),
        "generated_utc": now.isoformat(),
        "sections": {
            "adversary_orbital_activity": orbital_summary,
            "upcoming_launches": {
                "adversary": adversary_launches[:10],
                "fvey_allied": fvey_launches[:10],
            },
            "space_weather_forecast": weather_section,
            "policy_developments": policy_section,
            "research_highlights": research_highlights,
            "hotspot_coverage": hotspots if isinstance(hotspots, dict) else {},
        },
        "watch_items": watch_items,
    }

    return _store("daily_brief", brief)


def _weather_forecast_text(weather: dict) -> str:
    """Generate human-readable space weather impact text."""
    kp = weather.get("kp_current")
    if kp is None:
        return "Space weather data unavailable"

    if kp >= 7:
        return (
            "SEVERE GEOMAGNETIC STORM — Expect HF radio blackouts, significant GPS "
            "accuracy degradation, increased satellite drag affecting LEO orbit predictions. "
            "ISR satellite pointing accuracy may be impacted. Recommend enhanced monitoring "
            "of critical satellite health telemetry."
        )
    if kp >= 5:
        return (
            "GEOMAGNETIC STORM IN PROGRESS — Moderate GPS accuracy reduction possible. "
            "LEO satellite drag increased, may affect orbit predictions for adversary tracking. "
            "HF communications may be intermittently disrupted at high latitudes."
        )
    if kp >= 4:
        return (
            "MINOR GEOMAGNETIC ACTIVITY — Marginal impact expected on space operations. "
            "High-latitude HF propagation may show minor degradation. Normal operations "
            "for most satellite systems."
        )
    return (
        "QUIET CONDITIONS — No significant space weather impact on satellite operations. "
        "GPS accuracy nominal. HF propagation normal."
    )
