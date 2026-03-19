"""
Deep Intelligence Analysis Engine
Provides adversary constellation analysis, threat correlation, space order of
battle (ORBAT), and daily intelligence summary generation.

Functions:
- analyze_constellation       — in-depth adversary constellation assessment
- correlate_threats            — cross-source threat correlation engine
- generate_orbat               — military-style Space Order of Battle
- generate_daily_summary       — structured morning intelligence brief

Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

import httpx

from data_sources.adversary_sats import (
    get_adversary_stats,
    get_adversary_satellites,
    identify_country,
    classify_satellite,
)
from data_sources.space_weather import fetch_weather_composite
from data_sources.launches import fetch_launches
from data_sources.ground_stations import get_adversary_stations, get_stations_summary
from data_sources.missile_intel import get_missile_asat_data, get_threat_summary as get_missile_threat_summary
from data_sources.live_intel import get_hotspot_analysis

# ---------------------------------------------------------------------------
# Cache — 300-second TTL for all deep analysis products
# ---------------------------------------------------------------------------
_cache: Dict[str, dict] = {}
_DEEP_TTL = 300  # 5 minutes


def _cached(key: str) -> Optional[dict]:
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < _DEEP_TTL:
        return entry["data"]
    return None


def _store(key: str, data: dict) -> dict:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# ---------------------------------------------------------------------------
# Constellation knowledge base (pre-computed intel from open sources)
# ---------------------------------------------------------------------------

_CONSTELLATIONS: Dict[str, dict] = {
    "YAOGAN": {
        "full_name": "Yaogan Weixing (Remote Sensing Satellite)",
        "country": "PRC",
        "operator": "PLA Strategic Support Force / Information Support Force",
        "mission": "Maritime surveillance, ELINT, SAR, and optical ISR",
        "name_patterns": ["YAOGAN"],
        "description": (
            "PRC primary military ISR constellation. Operates in triplet formations "
            "(1 SAR + 2 ELINT) for maritime surveillance. Also includes dedicated "
            "optical and SAR imaging satellites. Provides near-persistent coverage "
            "of the Western Pacific, South China Sea, and Indian Ocean."
        ),
        "estimated_total": 50,
        "orbital_config": {
            "type": "Sun-synchronous LEO, multiple planes",
            "altitude_range_km": "480-1100",
            "planes": "10-12 orbital planes",
            "inclination_range": "63-98 degrees",
            "plane_spacing_notes": (
                "ELINT triplets spaced ~120 deg in-plane for rapid revisit. "
                "SAR/optical in SSO for consistent illumination."
            ),
        },
        "coverage_persistence": {
            "western_pacific": "Near-persistent (revisit < 30 min with full constellation)",
            "south_china_sea": "Near-persistent (revisit < 30 min)",
            "indian_ocean": "Intermittent (revisit 1-3 hours)",
            "global": "Intermittent (revisit 3-6 hours for any point on Earth)",
        },
        "growth_rate": (
            "3-6 launches per year since 2020. Constellation grew from ~30 to 50+ "
            "satellites in 3 years. Assessed to target 80-100 satellites by 2028 "
            "for truly persistent global maritime ISR."
        ),
        "assessed_capability": {
            "optical_resolution": "Sub-1m (Yaogan-33 class)",
            "sar_resolution": "1-3m (stripmap), sub-1m (spotlight)",
            "elint_capability": "Ship radar emission detection and geolocation",
            "revisit_time": "< 30 min Western Pacific, 1-3 hr globally",
            "video_capable": False,
            "night_capable": True,
            "all_weather": "SAR variants are all-weather capable",
        },
        "fvey_countermeasures": [
            "EMCON (emission control) for naval vessels in Western Pacific",
            "Decoy/deception — false radar emissions to confuse ELINT geolocation",
            "Schedule sensitive surface movements during coverage gaps",
            "Develop LEO ISR satellite jamming/dazzling capability",
            "Monitor Yaogan constellation health for degraded coverage windows",
            "Counter-ISR: detect and track Yaogan SAR illumination events",
        ],
        "source_reference": (
            "NASIC 'Competing in Space'; SWF Global Counterspace 2024; "
            "Bart Hendrickx analysis; CSIS Aerospace Security"
        ),
    },
    "JILIN": {
        "full_name": "Jilin-1 (Chang Guang Satellite Technology)",
        "country": "PRC",
        "operator": "Chang Guang Satellite Technology Co. (CGST) / PLA customer",
        "mission": "Commercial-military high-resolution optical and video ISR",
        "name_patterns": ["JILIN"],
        "description": (
            "Ostensibly commercial ISR constellation with significant military "
            "utility. Provides high-resolution optical imagery and HD video from "
            "orbit. CGST has known PLA customer relationships. Planned expansion "
            "to 300+ satellites would provide near-real-time global coverage."
        ),
        "estimated_total": 100,
        "orbital_config": {
            "type": "Sun-synchronous LEO",
            "altitude_range_km": "535-545",
            "planes": "6-8 orbital planes",
            "inclination_range": "97.5 degrees (SSO)",
            "plane_spacing_notes": (
                "Distributed across multiple SSO planes for rapid revisit. "
                "Constellation is designed for persistent coverage of mid-latitudes."
            ),
        },
        "coverage_persistence": {
            "mid_latitudes": "Revisit < 10 min (with full 138-sat phase)",
            "western_pacific": "Revisit < 10 min",
            "global": "Revisit < 30 min (planned 300+ constellation)",
        },
        "growth_rate": (
            "Rapid expansion — 41 satellites launched in a single mission (Jun 2023). "
            "Growth from 30 to 100+ satellites in 2022-2024. Planned 138-sat phase "
            "by 2025, 300-sat full constellation by 2027."
        ),
        "assessed_capability": {
            "optical_resolution": "0.5-0.75m (Jilin-1 Gaofen series)",
            "video_resolution": "0.92m at 30fps (Jilin-1 Video series)",
            "sar_resolution": "N/A (optical only)",
            "revisit_time": "< 10 min (138-sat phase)",
            "video_capable": True,
            "night_capable": False,
            "all_weather": "No — optical only, cloud dependent",
        },
        "fvey_countermeasures": [
            "Camouflage, concealment, and deception (CCD) for ground targets",
            "Exploit cloud cover windows for sensitive operations",
            "Monitor Jilin constellation overpass schedule for evasion",
            "Electronic attack against downlink frequencies",
            "Develop rapid satellite dazzling capability for optical ISR denial",
        ],
        "source_reference": (
            "CGST published specs; Space News; CSIS analysis; "
            "Planet Labs comparison studies; PLA customer relationship reporting"
        ),
    },
    "BEIDOU": {
        "full_name": "BeiDou-3 Navigation Satellite System",
        "country": "PRC",
        "operator": "PLA Strategic Support Force / China Satellite Navigation Office",
        "mission": "Global PNT — military and civilian positioning, navigation, timing",
        "name_patterns": ["BEIDOU", "BD-", "BDS-"],
        "description": (
            "PRC independent PNT constellation providing global coverage. BeiDou-3 "
            "is the operational generation with 30 MEO + 5 GEO + 3 IGSO satellites. "
            "Provides centimeter-level precision via military signal (B3I) and short "
            "message communication capability unique among GNSS constellations."
        ),
        "estimated_total": 38,
        "orbital_config": {
            "type": "Mixed MEO/GEO/IGSO",
            "altitude_range_km": "21,500 (MEO), 35,786 (GEO/IGSO)",
            "planes": "3 MEO planes + 5 GEO slots + 3 IGSO orbits",
            "inclination_range": "55 deg (MEO), 0 deg (GEO), 55 deg (IGSO)",
            "plane_spacing_notes": (
                "MEO: 24 satellites in 3 orbital planes at 21,500 km, 120 deg spacing. "
                "GEO: 5 satellites at geostationary orbit providing Asia-Pacific augmentation. "
                "IGSO: 3 satellites in inclined geosynchronous orbits for regional enhancement."
            ),
        },
        "coverage_persistence": {
            "global": "Continuous (24+ MEO satellites provide full global coverage)",
            "asia_pacific": "Enhanced (GEO + IGSO augmentation provides superior accuracy)",
            "military_signal": "Global B3I military signal — independent of GPS",
        },
        "growth_rate": (
            "BeiDou-3 constellation completed in 2020 with 30 MEO launches. "
            "Now in sustainment phase with replacement launches as satellites age. "
            "BeiDou-3+ (enhanced signals, inter-satellite links) being deployed. "
            "~2-3 replacement/augmentation launches per year."
        ),
        "assessed_capability": {
            "civilian_accuracy": "1.5-2m horizontal (open signal)",
            "military_accuracy": "Centimeter-level (B3I + augmentation)",
            "short_message": "Two-way messaging (unique to BeiDou, 1,000 characters)",
            "timing_accuracy": "< 20 nanoseconds",
            "anti_jam": "Military signal with higher power and anti-spoof features",
            "inter_satellite_links": True,
        },
        "fvey_countermeasures": [
            "Develop BeiDou signal monitoring and characterization capability",
            "GPS M-code acceleration to match BeiDou military signal resilience",
            "Alternative PNT sources (eLoran, LEO PNT) to reduce GPS single-point-of-failure",
            "BeiDou spoofing/jamming capability for theater operations",
            "Monitor BeiDou signal anomalies as indicator of PRC military activity",
        ],
        "source_reference": (
            "China Satellite Navigation Office white papers; USNO BeiDou analysis; "
            "Inside GNSS journal; ESA GNSS Service Centre; DoD PNT Strategy"
        ),
    },
    "SHIJIAN": {
        "full_name": "Shijian (Practice) Technology Demonstration Series",
        "country": "PRC",
        "operator": "PLA / CAST / various PRC space entities",
        "mission": "Technology demonstration, inspector/RPO, ASAT-adjacent capabilities",
        "name_patterns": ["SHIJIAN", "SJ-"],
        "description": (
            "Multi-purpose technology demonstration satellite series. Several Shijian "
            "missions have demonstrated rendezvous and proximity operations (RPO), "
            "robotic arm grappling, and satellite inspection — capabilities directly "
            "applicable to co-orbital ASAT operations. SJ-21 demonstrated GEO "
            "satellite capture and relocation in 2022, a game-changing capability."
        ),
        "estimated_total": 20,
        "orbital_config": {
            "type": "Mixed — LEO, MEO, GEO depending on mission",
            "altitude_range_km": "500-35,786",
            "planes": "Various — mission-dependent orbits",
            "inclination_range": "0-98 degrees",
            "plane_spacing_notes": (
                "Not a traditional constellation — individual missions in diverse orbits. "
                "SJ-17 and SJ-21 operate in GEO. SJ-6 series in LEO. "
                "SJ-23 assessed to be in GEO transfer orbit with RPO capability."
            ),
        },
        "coverage_persistence": {
            "note": "Not an ISR constellation — RPO/inspector satellites operate on-demand",
            "geo_belt": "Persistent presence via SJ-17, SJ-21 (GEO RPO)",
            "leo": "Intermittent presence via SJ-6, SJ-15 series",
        },
        "growth_rate": (
            "1-3 launches per year. SJ-21 launched 2021, SJ-23 launched 2023. "
            "Each new Shijian mission typically demonstrates more advanced RPO "
            "capabilities. Trend is toward increasingly sophisticated on-orbit "
            "servicing/inspection/manipulation missions."
        ),
        "assessed_capability": {
            "rpo_capable": True,
            "robotic_arm": "SJ-21 demonstrated robotic capture of defunct satellite",
            "geo_towing": "SJ-21 relocated a defunct BeiDou satellite to graveyard orbit",
            "inspection": "Close-approach imaging and characterization of target satellites",
            "asat_relevance": "CRITICAL — same techniques used for ASAT: approach, grapple, relocate/disable",
            "debris_removal_cover": "Dual-use: debris removal tech = satellite capture tech",
        },
        "fvey_countermeasures": [
            "Enhanced GEO SSA to detect and track Shijian RPO maneuvers",
            "GSSAP neighborhood watch expansion for GEO belt monitoring",
            "Develop keep-out zone enforcement doctrine for FVEY GEO assets",
            "Satellite self-defense: autonomous evasion of approaching objects",
            "Allied commercial SSA (ExoAnalytic, Slingshot) for continuous GEO monitoring",
            "Pre-planned response options for hostile RPO approach",
        ],
        "source_reference": (
            "ExoAnalytic SJ-21 tracking data; SWF Global Counterspace 2024; "
            "DIA 'Challenges to Security in Space'; T.S. Kelso analysis; "
            "Slingshot Aerospace observations"
        ),
    },
    "GLONASS": {
        "full_name": "GLONASS (Global Navigation Satellite System)",
        "country": "CIS",
        "operator": "Russian Aerospace Forces (VKS) / Roscosmos",
        "mission": "Global PNT — Russian military and civilian positioning, navigation, timing",
        "name_patterns": ["GLONASS", "URAGAN"],
        "description": (
            "Russian PNT constellation providing global coverage. Currently 24 "
            "operational MEO satellites (GLONASS-M and GLONASS-K series). "
            "Augments PRC BeiDou for combined PNT resilience against GPS denial. "
            "Russia-China GNSS cooperation agreement enables combined BeiDou-GLONASS "
            "receivers for enhanced accuracy and redundancy."
        ),
        "estimated_total": 24,
        "orbital_config": {
            "type": "MEO constellation",
            "altitude_range_km": "19,100",
            "planes": "3 orbital planes, 120 degree separation",
            "inclination_range": "64.8 degrees",
            "plane_spacing_notes": (
                "8 satellites per plane, evenly spaced. 3 planes at 64.8 deg "
                "inclination provide superior high-latitude coverage compared to GPS "
                "(55 deg). This gives Russia better PNT performance in its Arctic regions."
            ),
        },
        "coverage_persistence": {
            "global": "Continuous (24 operational satellites)",
            "high_latitude": "Superior to GPS due to 64.8 deg inclination",
            "combined_beidou": "Combined GLONASS+BeiDou provides GPS-independent PNT globally",
        },
        "growth_rate": (
            "Sustainment phase — 1-3 replacement launches per year. GLONASS-K2 "
            "(modernized) satellites being deployed to replace aging GLONASS-M. "
            "GLONASS-K2 introduces CDMA signals for interoperability with BeiDou. "
            "Constellation maintenance challenged by sanctions affecting electronics supply."
        ),
        "assessed_capability": {
            "civilian_accuracy": "2.8m horizontal (standalone), 1m (SDCM augmented)",
            "military_accuracy": "Sub-meter with military signal + augmentation",
            "combined_beidou_accuracy": "< 1m horizontal (military-grade)",
            "timing_accuracy": "< 30 nanoseconds",
            "anti_jam": "Military high-precision signal with anti-spoof features",
            "fdma_legacy": True,
            "cdma_modern": "GLONASS-K2 adds CDMA signals",
        },
        "fvey_countermeasures": [
            "Monitor GLONASS+BeiDou combined receiver development in adversary militaries",
            "Develop GLONASS signal jamming/spoofing capability for theater operations",
            "Track GLONASS constellation health — sanctions may cause degradation",
            "Ensure GPS M-code resilience exceeds combined GLONASS+BeiDou",
            "Allied GNSS resilience (Galileo integration) as NATO standard",
        ],
        "source_reference": (
            "IAC Roscosmos presentations; Information-Analytical Centre (IAC) GLONASS status; "
            "Inside GNSS; ESA GNSS Service Centre; US NGA GNSS assessments"
        ),
    },
    "COSMOS_ISR": {
        "full_name": "Cosmos ISR Constellation (Mixed Russian Military ISR)",
        "country": "CIS",
        "operator": "Russian Aerospace Forces (VKS) / GRU",
        "mission": "Mixed military ISR — optical, SAR, ELINT, SIGINT",
        "name_patterns": ["COSMOS", "KONDOR", "BARS", "PERSONA", "LOTOS", "LIANA", "PION"],
        "description": (
            "Russia's military ISR satellite fleet is a heterogeneous mix of optical, "
            "SAR, and SIGINT satellites. Unlike PRC's purpose-built constellations, "
            "Russian military ISR uses a variety of satellite types under the Cosmos "
            "designation and specialized names. Key systems: Persona (optical), "
            "Bars-M (mapping), Kondor (SAR), Lotos-S/Pion-NKS (ELINT/SIGINT), "
            "Liana system (ELINT constellation)."
        ),
        "estimated_total": 15,
        "orbital_config": {
            "type": "Mixed LEO orbits",
            "altitude_range_km": "200-900",
            "planes": "Various — mission-dependent orbits",
            "inclination_range": "67-98 degrees",
            "plane_spacing_notes": (
                "Persona optical: ~700 km SSO. Bars-M: ~550 km SSO. "
                "Kondor SAR: ~500 km. Lotos-S ELINT: ~900 km, 67 deg. "
                "Pion-NKS: ~500 km, 97.6 deg. Not optimized as a unified constellation."
            ),
        },
        "coverage_persistence": {
            "european_theater": "Intermittent (revisit hours to days with current fleet)",
            "global": "Sparse (significant coverage gaps due to small fleet size)",
            "arctic": "Better coverage due to high-inclination orbits",
        },
        "growth_rate": (
            "Very slow — 1-2 ISR satellite launches per year. Sanctions have severely "
            "impacted Russia's ability to build advanced imaging satellites (radiation-hard "
            "electronics shortages). Kondor-FKA radar satellites partly mitigate this "
            "as SAR sensors are less dependent on imported components. Constellation "
            "is aging and not being replaced at sufficient rate."
        ),
        "assessed_capability": {
            "optical_resolution": "0.5-1m (Persona class) — limited constellation",
            "sar_resolution": "1-3m (Kondor-FKA)",
            "elint_capability": "Lotos-S/Pion-NKS: ship and aircraft radar geolocation",
            "revisit_time": "Hours to days (small constellation)",
            "video_capable": False,
            "night_capable": True,
            "all_weather": "Kondor SAR is all-weather; optical is cloud-limited",
        },
        "fvey_countermeasures": [
            "Monitor Russian ISR satellite health — aging fleet creates coverage gaps",
            "Exploit known coverage gaps for sensitive operations",
            "Track Lotos-S/Pion-NKS ELINT coverage for EMCON scheduling",
            "Sanctions enforcement to delay ISR constellation replenishment",
            "Monitor for Russian purchase of commercial ISR imagery as gap-filler",
        ],
        "source_reference": (
            "Bart Hendrickx analysis (The Space Review); SWF Global Counterspace; "
            "Russian Space Web (Anatoly Zak); NASIC 'Competing in Space'"
        ),
    },
}

# Canonical name map — accept common variants
_CONSTELLATION_ALIASES: Dict[str, str] = {
    "YAOGAN": "YAOGAN",
    "JILIN": "JILIN",
    "JILIN-1": "JILIN",
    "JILIN1": "JILIN",
    "BEIDOU": "BEIDOU",
    "BEIDOU-3": "BEIDOU",
    "BDS": "BEIDOU",
    "SHIJIAN": "SHIJIAN",
    "SJ": "SHIJIAN",
    "GLONASS": "GLONASS",
    "URAGAN": "GLONASS",
    "COSMOS": "COSMOS_ISR",
    "COSMOS_ISR": "COSMOS_ISR",
    "LIANA": "COSMOS_ISR",
    "LOTOS": "COSMOS_ISR",
    "KONDOR": "COSMOS_ISR",
    "PERSONA": "COSMOS_ISR",
}


def _resolve_constellation(name: str) -> Optional[str]:
    """Resolve user-provided constellation name to canonical key."""
    key = name.strip().upper().replace("-", "").replace(" ", "_")
    # Direct match
    if key in _CONSTELLATIONS:
        return key
    # Alias match
    for alias, canon in _CONSTELLATION_ALIASES.items():
        if alias.replace("-", "").replace(" ", "") == key:
            return canon
    # Partial match
    for canon_key in _CONSTELLATIONS:
        if key in canon_key or canon_key in key:
            return canon_key
    return None


# ---------------------------------------------------------------------------
# 1. Adversary Constellation Analysis
# ---------------------------------------------------------------------------

async def analyze_constellation(
    client: httpx.AsyncClient,
    constellation_name: str,
) -> Optional[dict]:
    """Detailed intelligence analysis of an adversary satellite constellation.

    Args:
        client: HTTP client for live data fetching.
        constellation_name: Name of the constellation (e.g. "YAOGAN", "JILIN").

    Returns:
        Dict with constellation intelligence assessment, or None if unknown.
    """
    canon = _resolve_constellation(constellation_name)
    if canon is None:
        return None

    cache_key = f"constellation_{canon}"
    cached = _cached(cache_key)
    if cached is not None:
        return cached

    intel = _CONSTELLATIONS[canon]
    now = datetime.now(timezone.utc)

    # Fetch live satellite data to count actual active satellites
    country = intel["country"]
    try:
        sats = await get_adversary_satellites(client, country)
    except Exception:
        sats = []

    patterns = intel["name_patterns"]
    matched: List[dict] = []
    for sat in sats:
        sat_name = sat.get("name", "").upper()
        if any(p.upper() in sat_name for p in patterns):
            matched.append(sat)

    # Orbital plane analysis
    inclinations: List[float] = []
    altitudes: List[float] = []
    regimes: Dict[str, int] = {}
    for sat in matched:
        inc = sat.get("inclination", 0.0)
        alt = sat.get("alt_km", 0.0)
        regime = sat.get("regime", "unknown")
        if inc > 0:
            inclinations.append(inc)
        if alt > 0:
            altitudes.append(alt)
        regimes[regime] = regimes.get(regime, 0) + 1

    # Cluster inclinations to estimate number of orbital planes
    planes = _estimate_orbital_planes(inclinations)

    result = {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "constellation": canon,
        "full_name": intel["full_name"],
        "country": country,
        "operator": intel["operator"],
        "mission": intel["mission"],
        "description": intel["description"],
        "live_satellite_count": len(matched),
        "estimated_total_reference": intel["estimated_total"],
        "orbital_configuration": {
            **intel["orbital_config"],
            "live_regime_distribution": regimes,
            "estimated_planes_from_data": planes,
            "altitude_stats": {
                "min_km": round(min(altitudes), 1) if altitudes else 0,
                "max_km": round(max(altitudes), 1) if altitudes else 0,
                "mean_km": round(sum(altitudes) / len(altitudes), 1) if altitudes else 0,
            },
            "inclination_stats": {
                "min_deg": round(min(inclinations), 2) if inclinations else 0,
                "max_deg": round(max(inclinations), 2) if inclinations else 0,
                "mean_deg": round(sum(inclinations) / len(inclinations), 2) if inclinations else 0,
            },
        },
        "coverage_persistence": intel["coverage_persistence"],
        "growth_rate_assessment": intel["growth_rate"],
        "assessed_capability": intel["assessed_capability"],
        "fvey_countermeasures": intel["fvey_countermeasures"],
        "source_reference": intel["source_reference"],
        "satellites_in_catalog": [
            {
                "norad_id": s.get("norad_id"),
                "name": s.get("name"),
                "alt_km": s.get("alt_km"),
                "inclination": s.get("inclination"),
                "regime": s.get("regime"),
                "category": s.get("category"),
            }
            for s in matched
        ],
    }

    return _store(cache_key, result)


def _estimate_orbital_planes(inclinations: List[float], tolerance: float = 2.0) -> int:
    """Estimate number of distinct orbital planes from inclination list.

    Groups inclinations within *tolerance* degrees as the same plane family.
    """
    if not inclinations:
        return 0
    sorted_inc = sorted(inclinations)
    planes = 1
    current_group = sorted_inc[0]
    for inc in sorted_inc[1:]:
        if abs(inc - current_group) > tolerance:
            planes += 1
            current_group = inc
    return planes


def get_available_constellations() -> List[dict]:
    """Return list of constellations available for analysis."""
    result: List[dict] = []
    for key, info in _CONSTELLATIONS.items():
        result.append({
            "key": key,
            "full_name": info["full_name"],
            "country": info["country"],
            "mission": info["mission"],
            "estimated_total": info["estimated_total"],
        })
    return result


# ---------------------------------------------------------------------------
# 2. Threat Correlation Engine
# ---------------------------------------------------------------------------

async def correlate_threats(client: httpx.AsyncClient) -> dict:
    """Cross-reference multiple data sources to produce correlated intelligence notes.

    Examines:
    - Recent adversary launches vs constellation growth
    - Space weather impact on ISR capability
    - Adversary ground station activity windows
    - Historical incident pattern matching

    Returns:
        Dict with list of intelligence notes and metadata.
    """
    cached = _cached("threat_correlations")
    if cached is not None:
        return cached

    import asyncio

    stats_task = get_adversary_stats(client)
    weather_task = fetch_weather_composite(client)
    launches_task = fetch_launches(client)

    stats, weather, launches_data = await asyncio.gather(
        stats_task, weather_task, launches_task,
        return_exceptions=True,
    )

    if isinstance(stats, Exception):
        stats = {}
    if isinstance(weather, Exception):
        weather = {}
    if isinstance(launches_data, Exception):
        launches_data = []

    now = datetime.now(timezone.utc)
    notes: List[dict] = []

    # --- Correlation 1: Recent adversary launches → constellation growth ---
    _correlate_launches(launches_data, notes, now)

    # --- Correlation 2: Space weather → ISR degradation ---
    _correlate_space_weather(weather, notes, now)

    # --- Correlation 3: Adversary ground station windows ---
    _correlate_ground_stations(notes, now)

    # --- Correlation 4: Historical pattern matching ---
    _correlate_historical_patterns(launches_data, stats, notes, now)

    # --- Correlation 5: Constellation size anomalies ---
    _correlate_constellation_size(stats, notes, now)

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    notes.sort(key=lambda n: priority_order.get(n.get("priority", "info"), 5))

    result = {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "correlation_count": len(notes),
        "intelligence_notes": notes,
        "data_sources_checked": [
            "CelesTrak active satellite catalog",
            "NOAA SWPC space weather data",
            "Launch Library 2 upcoming launches",
            "Adversary ground station database",
            "Historical space security incident patterns",
        ],
        "methodology": (
            "Automated cross-referencing of live data feeds with structured "
            "intelligence databases. Each note is generated by a specific "
            "correlation rule applied to current data. Confidence levels reflect "
            "the strength of the correlation and data quality."
        ),
    }

    return _store("threat_correlations", result)


def _correlate_launches(
    launches_data: list,
    notes: List[dict],
    now: datetime,
) -> None:
    """Correlate upcoming adversary launches with constellation growth."""
    prc_launches = []
    rus_launches = []
    other_adv_launches = []

    for launch in launches_data:
        provider = (launch.get("provider") or "").lower()
        name = (launch.get("name") or "").lower()
        mission = (launch.get("mission") or "").lower()

        if any(kw in provider for kw in ["casc", "china", "expace", "galactic energy", "ispace", "landspace"]):
            payload_hint = _infer_payload_type(launch)
            prc_launches.append({
                "name": launch.get("name", ""),
                "net": launch.get("net", ""),
                "payload_hint": payload_hint,
            })
        elif any(kw in provider for kw in ["roscosmos", "russia", "khrunichev"]):
            payload_hint = _infer_payload_type(launch)
            rus_launches.append({
                "name": launch.get("name", ""),
                "net": launch.get("net", ""),
                "payload_hint": payload_hint,
            })
        elif any(kw in provider for kw in ["iran", "dprk", "korea"]):
            other_adv_launches.append(launch)

    if prc_launches:
        yaogan_count = sum(1 for l in prc_launches if "yaogan" in l["name"].lower())
        jilin_count = sum(1 for l in prc_launches if "jilin" in l["name"].lower())

        note_text = (
            f"PRC has {len(prc_launches)} launches in the upcoming manifest."
        )
        if yaogan_count > 0:
            note_text += (
                f" {yaogan_count} mission(s) appear to be Yaogan ISR deployments, "
                f"expanding maritime surveillance coverage of the Western Pacific."
            )
        if jilin_count > 0:
            note_text += (
                f" {jilin_count} mission(s) appear to be Jilin-1 commercial-military ISR, "
                f"increasing high-resolution optical/video capability."
            )

        notes.append({
            "id": f"CORR-LAUNCH-PRC-{now.strftime('%Y%m%d')}",
            "type": "LAUNCH_CORRELATION",
            "priority": "high",
            "confidence": "moderate",
            "note": note_text,
            "details": prc_launches,
            "analyst_comment": (
                "Each successful PRC ISR launch incrementally improves adversary "
                "maritime domain awareness. Monitor for orbital deployment confirmation "
                "and initial orbital parameters to assess coverage impact."
            ),
        })

    if rus_launches:
        soyuz_count = sum(1 for l in rus_launches if "soyuz" in l["name"].lower())
        note_text = (
            f"Russia has {len(rus_launches)} launches in the upcoming manifest."
        )
        if soyuz_count > 0:
            note_text += (
                f" {soyuz_count} Soyuz mission(s) scheduled — historically ~40% of "
                f"Soyuz 2.1b missions have deployed military payloads (Bars-M, Lotos-S, GLONASS)."
            )

        notes.append({
            "id": f"CORR-LAUNCH-RUS-{now.strftime('%Y%m%d')}",
            "type": "LAUNCH_CORRELATION",
            "priority": "medium",
            "confidence": "moderate",
            "note": note_text,
            "details": rus_launches,
            "analyst_comment": (
                "Russian launch cadence has slowed since 2022 due to sanctions impact "
                "on the space industrial base. Each successful military launch is "
                "significant for constellation sustainment."
            ),
        })

    if other_adv_launches:
        notes.append({
            "id": f"CORR-LAUNCH-OTHER-{now.strftime('%Y%m%d')}",
            "type": "LAUNCH_CORRELATION",
            "priority": "medium",
            "confidence": "low",
            "note": (
                f"{len(other_adv_launches)} launch(es) from DPRK/Iran in the upcoming "
                f"manifest. Any successful orbital insertion would represent a significant "
                f"capability advancement."
            ),
            "analyst_comment": (
                "DPRK and Iran orbital launch attempts should be treated as high-priority "
                "watch items regardless of declared payload."
            ),
        })


def _correlate_space_weather(
    weather: dict,
    notes: List[dict],
    now: datetime,
) -> None:
    """Correlate space weather conditions with ISR capability impacts."""
    if not isinstance(weather, dict):
        return

    kp = weather.get("kp_current")
    solar_wind = weather.get("solar_wind_speed")
    bz = weather.get("bz")

    if kp is not None and kp >= 5:
        degradation_pct = min(int((kp - 3) * 10), 50)
        notes.append({
            "id": f"CORR-WX-KP-{now.strftime('%Y%m%d')}",
            "type": "SPACE_WEATHER_CORRELATION",
            "priority": "high" if kp >= 7 else "medium",
            "confidence": "high",
            "note": (
                f"Current Kp={kp} conditions degrade LEO ISR pointing accuracy by "
                f"~{degradation_pct}%, temporarily reducing adversary reconnaissance "
                f"effectiveness. FVEY ISR assets are also affected."
            ),
            "analyst_comment": (
                "Geomagnetic storm conditions increase atmospheric drag on LEO satellites, "
                "degrading orbit prediction accuracy. Optical ISR systems may experience "
                "increased pointing jitter from torque rod interactions with the disturbed "
                "magnetic field. This is a temporary effect lasting hours to days."
            ),
        })

    if kp is not None and kp <= 1:
        notes.append({
            "id": f"CORR-WX-QUIET-{now.strftime('%Y%m%d')}",
            "type": "SPACE_WEATHER_CORRELATION",
            "priority": "info",
            "confidence": "high",
            "note": (
                f"Quiet geomagnetic conditions (Kp={kp}) — all adversary ISR systems "
                f"operating at optimal capability. No space weather degradation of "
                f"reconnaissance effectiveness."
            ),
            "analyst_comment": (
                "Quiet conditions mean adversary ISR performance is not degraded by "
                "space weather. Plan sensitive operations for storm periods if possible."
            ),
        })

    if solar_wind is not None and solar_wind > 700:
        notes.append({
            "id": f"CORR-WX-WIND-{now.strftime('%Y%m%d')}",
            "type": "SPACE_WEATHER_CORRELATION",
            "priority": "medium",
            "confidence": "moderate",
            "note": (
                f"Elevated solar wind speed ({solar_wind} km/s) increasing LEO satellite "
                f"drag. Adversary orbit predictions may deviate from TLE-derived positions "
                f"by several km over 24 hours."
            ),
            "analyst_comment": (
                "High solar wind expands the thermosphere, increasing drag on LEO satellites. "
                "This affects FVEY tracking accuracy for adversary assets and vice versa."
            ),
        })

    if bz is not None and bz < -10:
        notes.append({
            "id": f"CORR-WX-BZ-{now.strftime('%Y%m%d')}",
            "type": "SPACE_WEATHER_CORRELATION",
            "priority": "high",
            "confidence": "high",
            "note": (
                f"Strong southward IMF Bz ({bz} nT) — conditions favorable for major "
                f"geomagnetic storm. Expect GPS accuracy degradation, HF blackouts at "
                f"high latitudes, and LEO satellite drag increase within hours."
            ),
            "analyst_comment": (
                "Southward Bz is the primary driver of geomagnetic storms. Current "
                "conditions indicate storm intensification is likely. This will affect "
                "both FVEY and adversary space operations."
            ),
        })


def _correlate_ground_stations(notes: List[dict], now: datetime) -> None:
    """Generate intelligence notes about adversary ground station activity windows."""
    stations = get_adversary_stations()

    prc_stations = [s for s in stations if s.get("country") == "PRC"]
    rus_stations = [s for s in stations if s.get("country") == "Russia"]

    # PRC overseas stations are particularly interesting
    prc_overseas = [
        s for s in prc_stations
        if s.get("location", "").lower() not in ("", "china")
        and "china" not in s.get("location", "").lower()
    ]

    if prc_overseas:
        locations = [s.get("name", s.get("location", "Unknown")) for s in prc_overseas[:5]]
        notes.append({
            "id": f"CORR-GND-PRC-{now.strftime('%Y%m%d')}",
            "type": "GROUND_STATION_CORRELATION",
            "priority": "medium",
            "confidence": "moderate",
            "note": (
                f"PRC operates {len(prc_overseas)} overseas TT&C stations "
                f"({', '.join(locations)}), enabling continuous command and data "
                f"download from ISR satellites outside PRC territory visibility. "
                f"These stations extend effective ISR coverage by reducing data latency."
            ),
            "analyst_comment": (
                "PRC overseas stations (especially Argentina, Namibia, Pakistan, "
                "Kiribati) provide ground contact for PRC satellites over the Southern "
                "Hemisphere and Western Hemisphere — areas not covered by PRC mainland "
                "ground stations. Monitor for new station agreements."
            ),
        })

    hour_utc = now.hour
    # PRC mainland stations active roughly 00:00-16:00 UTC (08:00-24:00 Beijing)
    if 0 <= hour_utc <= 16:
        notes.append({
            "id": f"CORR-GND-PRC-ACTIVE-{now.strftime('%Y%m%d%H')}",
            "type": "GROUND_STATION_CORRELATION",
            "priority": "info",
            "confidence": "high",
            "note": (
                f"PRC mainland TT&C stations are in their primary operating window "
                f"({hour_utc:02d}00Z, ~{(hour_utc + 8) % 24:02d}00 Beijing time). "
                f"Maximum satellite command capacity available."
            ),
            "analyst_comment": (
                "PRC can task ISR satellites for specific target collections during "
                "mainland station visibility windows. Tasking commands issued now "
                "will result in collection in subsequent orbits."
            ),
        })


def _correlate_historical_patterns(
    launches_data: list,
    stats: dict,
    notes: List[dict],
    now: datetime,
) -> None:
    """Match current data against historical incident patterns."""
    # Pattern: pre-conflict ISR surge
    prc_stats = stats.get("PRC", {}) if isinstance(stats, dict) else {}
    prc_isr = prc_stats.get("military_isr", 0) if isinstance(prc_stats, dict) else 0

    if prc_isr > 80:
        notes.append({
            "id": f"CORR-HIST-PRC-ISR-{now.strftime('%Y%m%d')}",
            "type": "HISTORICAL_PATTERN",
            "priority": "high",
            "confidence": "moderate",
            "note": (
                f"PRC military ISR constellation has reached {prc_isr} satellites. "
                f"This exceeds the threshold for near-persistent Western Pacific "
                f"coverage. Historical analysis indicates PRC targeted 80+ ISR satellites "
                f"as the minimum for confident maritime domain awareness in a Taiwan "
                f"contingency."
            ),
            "analyst_comment": (
                "The growth of PRC ISR assets beyond the persistent-coverage threshold "
                "is a strategic indicator. Monitor for corresponding increases in ground "
                "processing capacity and C2 integration exercises."
            ),
        })

    # Pattern: Russian military launch correlation
    for launch in launches_data:
        name = (launch.get("name") or "").lower()
        rocket = (launch.get("rocket") or "").lower()
        if "soyuz" in rocket and "2.1b" in rocket:
            notes.append({
                "id": f"CORR-HIST-RUS-SOYUZ-{now.strftime('%Y%m%d')}",
                "type": "HISTORICAL_PATTERN",
                "priority": "medium",
                "confidence": "moderate",
                "note": (
                    f"Soyuz 2.1b launch scheduled: '{launch.get('name', 'Unknown')}'. "
                    f"Historically ~40% of Soyuz 2.1b missions deploy military payloads "
                    f"(Bars-M mapping, Lotos-S ELINT, GLONASS nav, or Cosmos ISR)."
                ),
                "analyst_comment": (
                    "Monitor post-launch for orbital parameters. Military payloads "
                    "typically deploy to specific inclinations: 67 deg (Lotos-S ELINT), "
                    "98 deg (Bars-M mapping), 64.8 deg (GLONASS)."
                ),
            })
            break  # One note per type is sufficient


def _correlate_constellation_size(
    stats: dict,
    notes: List[dict],
    now: datetime,
) -> None:
    """Note significant constellation sizes and ratios."""
    if not isinstance(stats, dict):
        return

    prc_total = stats.get("PRC", {}).get("total", 0) if isinstance(stats.get("PRC"), dict) else 0
    cis_total = stats.get("CIS", {}).get("total", 0) if isinstance(stats.get("CIS"), dict) else 0
    fvey_total = stats.get("fvey_total", 0)

    combined_adversary = prc_total + cis_total

    if fvey_total > 0 and combined_adversary > 0:
        ratio = combined_adversary / max(fvey_total, 1)
        notes.append({
            "id": f"CORR-SIZE-RATIO-{now.strftime('%Y%m%d')}",
            "type": "FORCE_RATIO",
            "priority": "info",
            "confidence": "high",
            "note": (
                f"Combined PRC+Russian satellite fleet ({combined_adversary} satellites) "
                f"vs FVEY fleet ({fvey_total} satellites). "
                f"Adversary-to-FVEY ratio: {ratio:.2f}:1. "
                f"Note: FVEY total includes commercial assets (Starlink, OneWeb) which "
                f"inflate the count but provide limited military ISR capability."
            ),
            "analyst_comment": (
                "Raw satellite counts are misleading — FVEY commercial broadband "
                "constellations dominate the count. For military-relevant categories "
                "(ISR, PNT, MILCOM, SDA), the balance is more nuanced. PRC military "
                "ISR constellation size now rivals FVEY national security ISR fleet."
            ),
        })


def _infer_payload_type(launch: dict) -> str:
    """Infer probable payload type from launch name and mission."""
    name = (launch.get("name") or "").lower()
    mission = (launch.get("mission") or "").lower()
    combined = name + " " + mission

    if "yaogan" in combined:
        return "military_isr"
    if "jilin" in combined:
        return "commercial_isr"
    if "beidou" in combined:
        return "navigation"
    if "shijian" in combined or "sj-" in combined:
        return "technology_demo_rpo"
    if "glonass" in combined:
        return "navigation"
    if "cosmos" in combined:
        return "military_probable"
    if "soyuz" in combined and "crew" in combined:
        return "crew"
    if "progress" in combined:
        return "resupply"
    return "unknown"


# ---------------------------------------------------------------------------
# 3. Space Order of Battle (ORBAT) Summary
# ---------------------------------------------------------------------------

async def generate_orbat(client: httpx.AsyncClient) -> dict:
    """Generate a formal military-style Space Order of Battle for all adversaries.

    Produces structured ORBAT documents for PRC, Russia, DPRK, and Iran,
    covering ISR, PNT, Comms, SDA/ASAT, Launch, Ground, and Counter-Space forces.

    Returns:
        Dict with ORBAT for each adversary nation.
    """
    cached = _cached("orbat")
    if cached is not None:
        return cached

    now = datetime.now(timezone.utc)

    # Fetch live satellite stats
    try:
        stats = await get_adversary_stats(client)
    except Exception:
        stats = {}

    stations_summary = get_stations_summary()
    missile_summary = get_missile_threat_summary()

    prc_cats = stats.get("PRC", {}).get("by_category", {}) if isinstance(stats.get("PRC"), dict) else {}
    cis_cats = stats.get("CIS", {}).get("by_category", {}) if isinstance(stats.get("CIS"), dict) else {}
    nkor_stats = stats.get("NKOR", {}) if isinstance(stats.get("NKOR"), dict) else {}
    iran_stats = stats.get("IRAN", {}) if isinstance(stats.get("IRAN"), dict) else {}

    prc_orbat = _build_prc_orbat(prc_cats, stats.get("PRC", {}), stations_summary, missile_summary)
    russia_orbat = _build_russia_orbat(cis_cats, stats.get("CIS", {}), stations_summary, missile_summary)
    dprk_orbat = _build_dprk_orbat(nkor_stats, missile_summary)
    iran_orbat = _build_iran_orbat(iran_stats, missile_summary)

    result = {
        "classification": "UNCLASSIFIED // OSINT",
        "document_type": "Space Order of Battle (ORBAT)",
        "generated_utc": now.isoformat(),
        "methodology": (
            "Satellite counts derived from CelesTrak active catalog via name-pattern "
            "identification. Ground infrastructure from open-source databases. "
            "Counter-space capabilities from SWF, DIA, NASIC published assessments. "
            "Launch capacity from historical manifests and facility analysis."
        ),
        "orbat": {
            "PRC": prc_orbat,
            "Russia": russia_orbat,
            "DPRK": dprk_orbat,
            "Iran": iran_orbat,
        },
        "source_references": [
            "CelesTrak GP catalog (live)",
            "SWF Global Counterspace Capabilities 2024",
            "DIA 'Challenges to Security in Space' 2022",
            "NASIC 'Competing in Space'",
            "DoD Annual Report on PRC Military Power",
            "Congressional Research Service space security reports",
        ],
    }

    return _store("orbat", result)


def _build_prc_orbat(
    cats: Dict[str, int],
    prc_stats: dict,
    stations_summary: dict,
    missile_summary: dict,
) -> dict:
    """Build PRC Space ORBAT."""
    prc_total = prc_stats.get("total", 0) if isinstance(prc_stats, dict) else 0
    isr_count = cats.get("military_isr", 0)
    nav_count = cats.get("navigation", 0)
    comms_count = cats.get("comms", 0)
    sda_count = cats.get("sda_asat", 0)
    ew_count = cats.get("early_warning", 0)
    human_count = cats.get("human_spaceflight", 0)
    sci_count = cats.get("civil_scientific", 0)
    unknown_count = cats.get("unknown", 0)

    prc_missiles = missile_summary.get("PRC", {}) if isinstance(missile_summary, dict) else {}
    prc_asat_total = prc_missiles.get("total", 0) if isinstance(prc_missiles, dict) else 0

    return {
        "nation": "People's Republic of China",
        "command_authority": "PLA Information Support Force (formerly Strategic Support Force)",
        "total_satellites": prc_total,
        "forces": {
            "isr_force": {
                "satellites": isr_count,
                "composition": (
                    f"{isr_count} satellites — Yaogan ELINT/SAR/optical triplets, "
                    f"Jilin-1 commercial-military optical/video, Gaofen high-resolution "
                    f"optical, Shiyan/Chuangxin technology/ISR"
                ),
                "capability": (
                    "Persistent Western Pacific maritime surveillance. Sub-1m optical "
                    "resolution. SAR all-weather day/night imaging. ELINT ship radar "
                    "detection and geolocation. Video-capable (Jilin-1)."
                ),
                "coverage": "Persistent Western Pacific, intermittent global",
                "trend": "EXPANDING — 3-6 ISR launches per year",
            },
            "pnt_force": {
                "satellites": nav_count,
                "composition": (
                    f"{nav_count} BeiDou-3 satellites — 24 MEO + 5 GEO + 3 IGSO "
                    f"(planned). Full global operational capability since 2020."
                ),
                "capability": (
                    "Independent PNT — cm-level military signal (B3I). Two-way short "
                    "message communication (unique among GNSS). Inter-satellite links "
                    "for autonomous operation. Military anti-jam/anti-spoof features."
                ),
                "coverage": "Global continuous, Asia-Pacific enhanced",
                "trend": "SUSTAINING — replacement and augmentation launches",
            },
            "comms_force": {
                "satellites": comms_count,
                "composition": (
                    f"{comms_count} satellites — Zhongxing/ChinaSat military SATCOM, "
                    f"Tiantong mobile SATCOM, Tianlian data relay, Fenghuo tactical"
                ),
                "capability": (
                    "Military SATCOM (encrypted, anti-jam), data relay for ISR downlink "
                    "(Tianlian), mobile military communications (Tiantong), tactical "
                    "battlefield communications."
                ),
                "coverage": "Global via relay, primary focus Asia-Pacific",
                "trend": "EXPANDING — new Zhongxing and Tiantong deployments",
            },
            "sda_asat_force": {
                "satellites": sda_count,
                "composition": (
                    f"{sda_count} satellites — Shijian inspector/RPO series, TJS "
                    f"technology demonstration, Banxing subsatellites, Aolong debris/RPO"
                ),
                "capability": (
                    "Inspector satellite RPO (all orbits). GEO satellite capture and "
                    "relocation (SJ-21 demonstrated). Robotic arm grappling. Close-approach "
                    "imaging and characterization. Dual-use debris removal / ASAT capability."
                ),
                "coverage": "GEO belt (SJ-17, SJ-21) and LEO on-demand",
                "trend": "EXPANDING — increasingly sophisticated RPO capabilities each generation",
            },
            "early_warning": {
                "satellites": ew_count,
                "composition": f"{ew_count} early warning / EW technology demonstration satellites",
                "capability": "Missile launch detection, EW signal characterization",
                "trend": "DEVELOPING — growing interest in dedicated space-based early warning",
            },
            "launch_force": {
                "active_pads": "4 launch complexes (Jiuquan, Taiyuan, Xichang, Wenchang)",
                "sea_launch": "Yes — mobile sea launch platform operational",
                "annual_launches": "50-60+ per year (2022-2024 average)",
                "vehicle_types": (
                    "CZ-2C/D (LEO), CZ-3B (GTO), CZ-4B/C (SSO), CZ-5 (heavy), "
                    "CZ-5B (LEO heavy), CZ-6/6A (medium), CZ-7 (medium), CZ-8 (medium), "
                    "CZ-11 (solid/rapid response), Kuaizhou-1A/11 (solid/rapid), "
                    "Lijian-1 (solid), commercial SLVs (CERES, Galactic Energy, etc.)"
                ),
                "rapid_response": (
                    "CZ-11 solid-fuel: 24-hour launch-on-demand capability. "
                    "Kuaizhou solid-fuel: similar rapid-response capability. "
                    "Critical for wartime reconstitution of lost satellites."
                ),
            },
            "ground_force": {
                "ttc_stations": "15+ mainland TT&C stations",
                "overseas_stations": (
                    "Argentina (Neuquen), Namibia (Swakopmund), Pakistan (Multan), "
                    "Kiribati, Kenya — extending coverage to Southern/Western Hemispheres"
                ),
                "tracking_ships": "Yuan Wang fleet (7+ vessels) providing mobile ocean TT&C",
                "deep_space": "Deep space network stations supporting lunar/Mars missions",
                "surveillance": (
                    "Growing SSA network — optical telescopes, radars, laser ranging. "
                    "Capable of tracking LEO and GEO objects."
                ),
            },
            "counter_space_arsenal": {
                "da_asat": (
                    f"SC-19/DN-3 series direct-ascent ASAT (tested 2007, 2013, 2014). "
                    f"Capable of reaching LEO and possibly MEO/GEO targets."
                ),
                "co_orbital": (
                    "Shijian series inspector/RPO satellites. SJ-21 demonstrated GEO "
                    "capture capability. Multiple LEO and GEO RPO missions conducted."
                ),
                "directed_energy": (
                    "Ground-based laser ASAT — assessed capable of dazzling/blinding "
                    "LEO optical ISR satellites. Development of higher-power systems "
                    "for satellite damage."
                ),
                "electronic_warfare": (
                    "GPS jamming/spoofing (deployed in South China Sea). SATCOM uplink "
                    "jamming capability. Dedicated military EW units for counter-space."
                ),
                "cyber": (
                    "APT groups (APT10, APT41, Thrip) have targeted satellite operators "
                    "and aerospace companies. Ground segment cyber intrusion capability."
                ),
                "asat_systems_total": prc_asat_total,
            },
        },
        "human_spaceflight": {
            "satellites": human_count,
            "note": "CSS/Tiangong space station — permanent crewed presence. Dual-use potential.",
        },
        "civil_scientific": {
            "satellites": sci_count,
            "note": "Weather (Fengyun), ocean (Haiyang), Earth observation, deep space exploration.",
        },
        "overall_assessment": (
            "PRC operates the most rapidly expanding military space program globally. "
            "The combination of persistent ISR, independent PNT, military SATCOM, and "
            "full-spectrum counter-space capabilities makes PRC a peer space competitor "
            "to the United States. The PLA's integration of space, cyber, and EW under "
            "a unified command structure provides coherent multi-domain counter-space "
            "operations capability. PRC's rapid-response launch capability (CZ-11, "
            "Kuaizhou) provides wartime reconstitution ability."
        ),
    }


def _build_russia_orbat(
    cats: Dict[str, int],
    cis_stats: dict,
    stations_summary: dict,
    missile_summary: dict,
) -> dict:
    """Build Russian Space ORBAT."""
    cis_total = cis_stats.get("total", 0) if isinstance(cis_stats, dict) else 0
    isr_count = cats.get("military_isr", 0)
    nav_count = cats.get("navigation", 0)
    comms_count = cats.get("comms", 0)
    sda_count = cats.get("sda_asat", 0)
    ew_count = cats.get("early_warning", 0)
    human_count = cats.get("human_spaceflight", 0)

    rus_missiles = missile_summary.get("Russia", {}) if isinstance(missile_summary, dict) else {}
    rus_asat_total = rus_missiles.get("total", 0) if isinstance(rus_missiles, dict) else 0

    return {
        "nation": "Russian Federation",
        "command_authority": "Russian Aerospace Forces (VKS) — 15th Aerospace Army",
        "total_satellites": cis_total,
        "forces": {
            "isr_force": {
                "satellites": isr_count,
                "composition": (
                    f"{isr_count} satellites — Persona optical, Bars-M mapping, "
                    f"Kondor/Kondor-FKA SAR, Lotos-S/Pion-NKS ELINT (Liana system), "
                    f"Cosmos-designated military ISR"
                ),
                "capability": (
                    "Optical: sub-1m resolution (Persona). SAR: 1-3m all-weather (Kondor). "
                    "ELINT: ship/aircraft radar geolocation (Lotos-S, Pion-NKS). "
                    "Mapping: high-accuracy geodetic mapping (Bars-M)."
                ),
                "coverage": "Intermittent — small constellation size limits revisit rates",
                "trend": "DECLINING/STRAINED — sanctions impacting replacement rate",
            },
            "pnt_force": {
                "satellites": nav_count,
                "composition": (
                    f"{nav_count} GLONASS satellites — GLONASS-M legacy + GLONASS-K/K2 "
                    f"modernized. 24 operational target for full global coverage."
                ),
                "capability": (
                    "Global PNT. Superior high-latitude coverage vs GPS (64.8 deg inclination). "
                    "Military signal for precision applications. Combined with BeiDou for "
                    "GPS-independent PNT."
                ),
                "coverage": "Global continuous (when 24 satellites operational)",
                "trend": "SUSTAINING — replacement rate challenged by sanctions",
            },
            "comms_force": {
                "satellites": comms_count,
                "composition": (
                    f"{comms_count} satellites — Blagovest wideband, Meridian/Molniya "
                    f"HEO tactical, Gonets-M low-data, Luch data relay, Yamal/Express "
                    f"commercial-military"
                ),
                "capability": (
                    "Military SATCOM via Blagovest (GEO). Arctic coverage via Meridian "
                    "(HEO Molniya orbit). Data relay via Luch. Low-bandwidth messaging "
                    "via Gonets-M. Commercial capacity via Yamal/Express."
                ),
                "coverage": "Global with Arctic emphasis via HEO orbits",
                "trend": "SUSTAINING — Sfera program planned for modernization",
            },
            "sda_asat_force": {
                "satellites": sda_count,
                "composition": (
                    f"{sda_count} satellites — Cosmos 2542/2543 co-orbital ASAT demonstrators, "
                    f"Cosmos 2558 inspector, Nivelir series, Burevestnik series"
                ),
                "capability": (
                    "Co-orbital ASAT: demonstrated satellite inspection and in-orbit weapons "
                    "release (Cosmos 2543). Inspector satellites can approach and characterize "
                    "adversary satellites. Assessed capability to physically interfere with "
                    "target satellites."
                ),
                "coverage": "On-demand — deployed to shadow specific targets",
                "trend": "ACTIVE — continued deployment of inspector satellites",
            },
            "early_warning": {
                "satellites": ew_count,
                "composition": (
                    f"{ew_count} satellites — Tundra/EKS (Kupol system) infrared early "
                    f"warning in HEO"
                ),
                "capability": "ICBM launch detection from HEO vantage point",
                "trend": "EXPANDING — Kupol constellation build-up continuing",
            },
            "launch_force": {
                "active_pads": "3 launch complexes (Plesetsk, Vostochny, Baikonur lease)",
                "annual_launches": "15-20 per year (reduced from 25+ pre-2022)",
                "vehicle_types": (
                    "Soyuz 2.1a/2.1b/2.1v (workhorse), Angara-1.2/A5 (new heavy), "
                    "Proton-M (GTO, being retired), Rockot/Strela (small LEO)"
                ),
                "rapid_response": (
                    "Limited rapid-response capability. Angara program delayed. "
                    "Sanctions affecting avionics and guidance system production."
                ),
            },
            "ground_force": {
                "ttc_stations": "~10 mainland TT&C stations across Russian territory",
                "deep_space": "Yevpatoria (disputed/Ukraine), Bear Lakes, Ussuriysk",
                "surveillance": (
                    "Voronezh radar network (ABM/SSA). Okno optical station (Tajikistan). "
                    "Krona radar-optical complex. Provides LEO and GEO tracking capability."
                ),
            },
            "counter_space_arsenal": {
                "da_asat": (
                    "Nudol (PL-19/A-235) direct-ascent ASAT — tested 10+ times. "
                    "Destructive test against Cosmos 1408 (Nov 2021) created 1,500+ debris. "
                    "Assessed capable of reaching LEO targets."
                ),
                "co_orbital": (
                    "Cosmos 2542/2543: demonstrated RPO and in-orbit projectile release. "
                    "Cosmos 2558: deployed near classified US satellite. Active inspector "
                    "satellite program with continued deployments."
                ),
                "directed_energy": (
                    "Peresvet laser system deployed at RVSN ICBM bases. Assessed capable "
                    "of dazzling/blinding optical ISR satellites. May have higher-power "
                    "variants in development."
                ),
                "electronic_warfare": (
                    "Tirada-2 SATCOM uplink jammer. Tobol counter-space EW system. "
                    "Extensive GPS jamming (routine in Ukraine, Syria, Baltic). "
                    "Krasukha-4 ground-based EW for satellite signal disruption."
                ),
                "cyber": (
                    "GRU Sandworm: Viasat KA-SAT cyberattack (Feb 2022). SVR/GRU APT "
                    "groups capable of targeting satellite ground infrastructure. "
                    "Demonstrated willingness to use cyber against space systems in conflict."
                ),
                "asat_systems_total": rus_asat_total,
            },
        },
        "human_spaceflight": {
            "satellites": human_count,
            "note": "ISS Russian segment (Zarya, Zvezda, Nauka, Prichal). Soyuz crew rotation.",
        },
        "overall_assessment": (
            "Russia maintains significant counter-space capabilities despite broader "
            "space program constraints from sanctions and the Ukraine conflict. Russia "
            "has DEMONSTRATED willingness to use counter-space in conflict (Viasat cyber, "
            "Cosmos 1408 ASAT test). Counter-space remains a priority investment. However, "
            "ISR constellation replenishment is lagging, GLONASS sustainment is challenged, "
            "and launch cadence has declined. The long-term trajectory of Russian space "
            "power is uncertain, but near-term counter-space threat remains CRITICAL."
        ),
    }


def _build_dprk_orbat(nkor_stats: dict, missile_summary: dict) -> dict:
    """Build DPRK Space ORBAT."""
    nkor_total = nkor_stats.get("total", 0) if isinstance(nkor_stats, dict) else 0

    return {
        "nation": "Democratic People's Republic of Korea",
        "command_authority": "National Aerospace Development Administration (NADA)",
        "total_satellites": nkor_total,
        "forces": {
            "isr_force": {
                "satellites": nkor_total,
                "composition": (
                    f"{nkor_total} satellite(s) — Malligyong-1 reconnaissance satellite "
                    f"(launched Nov 2023 on Chollima-1 SLV)"
                ),
                "capability": (
                    "Basic electro-optical reconnaissance. Actual imaging quality "
                    "unconfirmed — assessed to be low resolution. Represents initial "
                    "capability rather than operational system."
                ),
                "coverage": "Minimal — single satellite provides intermittent passes only",
                "trend": "NASCENT — first successful ISR satellite deployment",
            },
            "launch_force": {
                "active_pads": "1 launch complex (Sohae Satellite Launching Station, Tongchang-ri)",
                "annual_launches": "1-2 attempts per year",
                "vehicle_types": (
                    "Chollima-1 SLV (3-stage, liquid/solid mix). "
                    "Hwasong ICBM series provides latent orbital insertion capability."
                ),
                "rapid_response": "None — liquid-fuel SLV requires days of preparation",
            },
            "counter_space_arsenal": {
                "da_asat": (
                    "Latent capability via Hwasong-15/17 ICBMs (demonstrated altitudes "
                    "of 4,500-6,200 km — well into LEO range). No known dedicated ASAT system."
                ),
                "electronic_warfare": (
                    "GPS jamming demonstrated against South Korea on multiple occasions "
                    "(2012, 2016). Vehicle-mounted GPS jammers affecting Seoul area."
                ),
            },
        },
        "russian_cooperation": (
            "Russia reportedly provided technical assistance for Malligyong-1 satellite "
            "and Chollima-1 SLV development. This cooperation vector could significantly "
            "accelerate DPRK space capabilities if sustained."
        ),
        "overall_assessment": (
            f"DPRK is a nascent space power with {nkor_total} satellite(s) in orbit. "
            f"Current space capability is minimal but trajectory is upward, especially "
            f"with Russian technical assistance. Primary concern is the latent ASAT "
            f"capability inherent in DPRK ICBM program — Hwasong-17 can reach altitudes "
            f"used by most LEO military satellites. GPS jamming is an active and "
            f"demonstrated capability."
        ),
    }


def _build_iran_orbat(iran_stats: dict, missile_summary: dict) -> dict:
    """Build Iran Space ORBAT."""
    iran_total = iran_stats.get("total", 0) if isinstance(iran_stats, dict) else 0

    return {
        "nation": "Islamic Republic of Iran",
        "command_authority": "IRGC Aerospace Force / Iranian Space Agency (ISA)",
        "total_satellites": iran_total,
        "forces": {
            "isr_force": {
                "satellites": iran_total,
                "composition": (
                    f"{iran_total} satellite(s) — Noor-1/2 (IRGC military imaging), "
                    f"Khayyam (launched on Russian Soyuz, reportedly imaging)"
                ),
                "capability": (
                    "Basic imaging capability. Noor series is small-form-factor with "
                    "limited resolution. Khayyam (launched by Russia) may have superior "
                    "sensors. Represents early operational ISR capability."
                ),
                "coverage": "Minimal — small number of satellites limits revisit",
                "trend": "SLOWLY EXPANDING — IRGC prioritizing indigenous ISR capability",
            },
            "launch_force": {
                "active_pads": "1 primary (Imam Khomeini Spaceport, Semnan)",
                "annual_launches": "1-3 attempts per year (many failures historically)",
                "vehicle_types": (
                    "Qased (IRGC, solid-fuel first stage — militarily significant for rapid prep). "
                    "Simorgh (ISA, liquid-fuel — multiple failures). "
                    "Zuljanah (solid-fuel, under development)."
                ),
                "rapid_response": (
                    "Qased solid-fuel first stage enables faster launch preparation than "
                    "liquid-fuel alternatives — militarily relevant for responsive launch."
                ),
            },
            "counter_space_arsenal": {
                "electronic_warfare": (
                    "Basic GPS jamming/spoofing — claimed to have captured US RQ-170 drone "
                    "via GPS spoofing (2011, disputed). GPS interference capability in "
                    "Persian Gulf region."
                ),
                "cyber": (
                    "Iranian APT groups have targeted aerospace and satellite companies "
                    "but no confirmed successful attack on satellite systems."
                ),
            },
        },
        "russian_cooperation": (
            "Russia launched Iran's Khayyam satellite on a Soyuz (2022). This may "
            "indicate growing space cooperation. Iran may seek further Russian "
            "assistance for more capable satellite development."
        ),
        "overall_assessment": (
            f"Iran operates {iran_total} satellite(s) with limited ISR capability. "
            f"The IRGC Qased SLV demonstrates solid-fuel orbital insertion capability, "
            f"which is strategically significant (SLV/ICBM technology overlap). Iran "
            f"does not currently pose a meaningful counter-space threat to FVEY assets. "
            f"Primary concern is the SLV-to-ASAT technology pathway and potential "
            f"Russian cooperation accelerating Iranian space capabilities."
        ),
    }


# ---------------------------------------------------------------------------
# 4. Daily Intelligence Summary Generator
# ---------------------------------------------------------------------------

async def generate_daily_summary(client: httpx.AsyncClient) -> dict:
    """Generate a structured daily intelligence summary for a morning brief.

    Produces a formal intelligence summary with:
    - Classification header
    - Overall threat level with trend
    - Top 3 priority items
    - Adversary activity summary
    - Space environment impact
    - Watch items for next 24 hours
    - Analyst recommendations

    Returns:
        Dict with structured daily intelligence summary.
    """
    cached = _cached("daily_summary")
    if cached is not None:
        return cached

    import asyncio

    stats_task = get_adversary_stats(client)
    weather_task = fetch_weather_composite(client)
    launches_task = fetch_launches(client)
    hotspot_task = get_hotspot_analysis(client)
    correlations_task = correlate_threats(client)

    stats, weather, launches_data, hotspots, correlations = await asyncio.gather(
        stats_task, weather_task, launches_task, hotspot_task, correlations_task,
        return_exceptions=True,
    )

    if isinstance(stats, Exception):
        stats = {}
    if isinstance(weather, Exception):
        weather = {}
    if isinstance(launches_data, Exception):
        launches_data = []
    if isinstance(hotspots, Exception):
        hotspots = {}
    if isinstance(correlations, Exception):
        correlations = {}

    now = datetime.now(timezone.utc)

    # --- Determine threat level ---
    threat_level, threat_trend = _assess_daily_threat(weather, hotspots, launches_data, stats)

    # --- Top 3 priority items ---
    priority_items = _generate_priority_items(
        weather, hotspots, launches_data, stats, correlations, now,
    )

    # --- Adversary activity summary ---
    adversary_summary = _generate_adversary_summary(stats, launches_data)

    # --- Space environment impact ---
    environment_impact = _generate_environment_impact(weather)

    # --- Watch items (next 24 hours) ---
    watch_items = _generate_watch_items(launches_data, weather, hotspots, stats)

    # --- Analyst recommendations ---
    recommendations = _generate_analyst_recommendations(
        weather, hotspots, launches_data, stats, correlations,
    )

    result = {
        "classification": "UNCLASSIFIED // OSINT",
        "document_type": "Daily Intelligence Summary",
        "date": now.strftime("%Y-%m-%d"),
        "time_utc": now.strftime("%H:%M:%SZ"),
        "generated_utc": now.isoformat(),
        "prepared_by": "ECHELON VANTAGE Automated Intelligence Analysis",
        "distribution": "REL TO FVEY",
        "overall_threat_level": threat_level,
        "threat_trend": threat_trend,
        "executive_summary": (
            f"Space threat environment assessed as {threat_level} with "
            f"{threat_trend.lower()} trend. "
            f"{_build_executive_line(stats, hotspots, launches_data, weather)}"
        ),
        "priority_items": priority_items[:3],
        "adversary_activity": adversary_summary,
        "space_environment_impact": environment_impact,
        "watch_items_next_24h": watch_items,
        "analyst_recommendations": recommendations,
        "intelligence_notes": correlations.get("intelligence_notes", [])[:5] if isinstance(correlations, dict) else [],
        "data_freshness": {
            "satellite_catalog": "Live (CelesTrak GP)",
            "space_weather": "Live (NOAA SWPC)",
            "launch_manifest": "Live (Launch Library 2)",
            "threat_assessment": "Structured database + live correlation",
        },
    }

    return _store("daily_summary", result)


def _assess_daily_threat(
    weather: dict,
    hotspots: dict,
    launches_data: list,
    stats: dict,
) -> Tuple[str, str]:
    """Determine overall threat level and trend for daily summary."""
    score = 0

    # Space weather factor
    if isinstance(weather, dict):
        kp = weather.get("kp_current")
        if kp is not None:
            if kp >= 7:
                score += 3
            elif kp >= 5:
                score += 2
            elif kp >= 4:
                score += 1

    # Hotspot activity
    if isinstance(hotspots, dict):
        total_passes = hotspots.get("total_passes_all_hotspots", 0)
        if total_passes > 20:
            score += 3
        elif total_passes > 10:
            score += 2
        elif total_passes > 5:
            score += 1

    # Adversary launch tempo
    adv_launch_count = 0
    for launch in launches_data:
        provider = (launch.get("provider") or "").lower()
        if any(kw in provider for kw in ["casc", "china", "roscosmos", "russia", "iran", "dprk"]):
            adv_launch_count += 1
    score += min(adv_launch_count, 3)

    # PRC ISR constellation size
    prc_isr = 0
    if isinstance(stats, dict):
        prc_data = stats.get("PRC", {})
        if isinstance(prc_data, dict):
            prc_isr = prc_data.get("military_isr", 0)
    if prc_isr > 80:
        score += 2
    elif prc_isr > 50:
        score += 1

    if score >= 9:
        level = "CRITICAL"
    elif score >= 6:
        level = "HIGH"
    elif score >= 3:
        level = "ELEVATED"
    else:
        level = "GUARDED"

    # Trend is always escalating for PRC expansion; steady otherwise
    if prc_isr > 50:
        trend = "ESCALATING"
    else:
        trend = "STEADY"

    return level, trend


def _generate_priority_items(
    weather: dict,
    hotspots: dict,
    launches_data: list,
    stats: dict,
    correlations: dict,
    now: datetime,
) -> List[dict]:
    """Generate top priority items from all data sources."""
    items: List[dict] = []

    # Priority 1: Adversary ISR over hotspots
    if isinstance(hotspots, dict):
        total_passes = hotspots.get("total_passes_all_hotspots", 0)
        most_covered = hotspots.get("most_covered_area", "Unknown")
        if total_passes > 0:
            items.append({
                "priority": 1,
                "title": "Adversary ISR Coverage of Strategic Areas",
                "severity": "HIGH" if total_passes > 10 else "ELEVATED",
                "detail": (
                    f"{total_passes} adversary ISR satellite passes detected across "
                    f"strategic hotspots in the next 2 hours. Highest concentration "
                    f"over {most_covered}."
                ),
                "action": "Monitor for collection activity and correlate with surface movements.",
            })

    # Priority 2: Upcoming adversary launches
    adv_launches = []
    for launch in launches_data:
        provider = (launch.get("provider") or "").lower()
        if any(kw in provider for kw in ["casc", "china", "roscosmos", "russia", "iran", "dprk"]):
            adv_launches.append(launch)

    if adv_launches:
        nearest = adv_launches[0]
        items.append({
            "priority": 2,
            "title": "Adversary Launch Activity",
            "severity": "ELEVATED",
            "detail": (
                f"{len(adv_launches)} adversary launch(es) in upcoming manifest. "
                f"Nearest: {nearest.get('name', 'Unknown')} — {nearest.get('net', 'TBD')}."
            ),
            "action": "Track launch and post-deployment orbital parameters for threat assessment.",
        })

    # Priority 3: Space weather impact
    if isinstance(weather, dict):
        kp = weather.get("kp_current")
        if kp is not None and kp >= 4:
            items.append({
                "priority": 3,
                "title": "Space Weather Impact on Operations",
                "severity": "HIGH" if kp >= 6 else "ELEVATED",
                "detail": (
                    f"Kp index at {kp} — geomagnetic activity affecting satellite operations. "
                    f"LEO ISR pointing degraded, GPS accuracy reduced, orbit predictions less reliable."
                ),
                "action": "Factor space weather degradation into ISR coverage assessments.",
            })
        elif kp is not None:
            items.append({
                "priority": 3,
                "title": "Space Environment Status",
                "severity": "LOW",
                "detail": (
                    f"Quiet space weather (Kp={kp}). All satellite systems operating nominally. "
                    f"Adversary ISR at full capability — no environmental degradation."
                ),
                "action": "No space weather impact on operations.",
            })

    # Priority from correlation engine
    if isinstance(correlations, dict):
        corr_notes = correlations.get("intelligence_notes", [])
        for note in corr_notes[:2]:
            if note.get("priority") in ("critical", "high"):
                items.append({
                    "priority": len(items) + 1,
                    "title": note.get("type", "Intelligence Correlation"),
                    "severity": note.get("priority", "medium").upper(),
                    "detail": note.get("note", ""),
                    "action": note.get("analyst_comment", ""),
                })

    items.sort(key=lambda x: x.get("priority", 99))
    return items


def _generate_adversary_summary(stats: dict, launches_data: list) -> dict:
    """Generate adversary activity section."""
    prc_data = stats.get("PRC", {}) if isinstance(stats, dict) else {}
    cis_data = stats.get("CIS", {}) if isinstance(stats, dict) else {}
    nkor_data = stats.get("NKOR", {}) if isinstance(stats, dict) else {}
    iran_data = stats.get("IRAN", {}) if isinstance(stats, dict) else {}

    prc_total = prc_data.get("total", 0) if isinstance(prc_data, dict) else 0
    cis_total = cis_data.get("total", 0) if isinstance(cis_data, dict) else 0

    return {
        "PRC": {
            "total_satellites": prc_total,
            "military_isr": prc_data.get("military_isr", 0) if isinstance(prc_data, dict) else 0,
            "navigation": prc_data.get("navigation", 0) if isinstance(prc_data, dict) else 0,
            "status": "Active — continued constellation expansion",
            "key_activity": (
                "Monitor for Yaogan/Jilin-1 launches and orbital adjustments. "
                "Track Shijian inspector satellite maneuvers near FVEY assets."
            ),
        },
        "Russia": {
            "total_satellites": cis_total,
            "military_isr": cis_data.get("military_isr", 0) if isinstance(cis_data, dict) else 0,
            "navigation": cis_data.get("navigation", 0) if isinstance(cis_data, dict) else 0,
            "status": "Active — counter-space prioritized despite program constraints",
            "key_activity": (
                "Monitor inspector satellite movements. Track GLONASS constellation "
                "health for sanctions impact. Watch for Nudol ASAT testing."
            ),
        },
        "DPRK": {
            "total_satellites": nkor_data.get("total", 0) if isinstance(nkor_data, dict) else 0,
            "status": "Limited — Malligyong-1 in orbit, future launches expected",
            "key_activity": "Monitor for additional satellite launch attempts.",
        },
        "Iran": {
            "total_satellites": iran_data.get("total", 0) if isinstance(iran_data, dict) else 0,
            "status": "Developing — slow but persistent capability growth",
            "key_activity": "Monitor IRGC Qased SLV launch preparations at Semnan.",
        },
    }


def _generate_environment_impact(weather: dict) -> dict:
    """Generate space environment impact assessment."""
    if not isinstance(weather, dict):
        return {
            "status": "DATA UNAVAILABLE",
            "detail": "Space weather data not available at this time.",
        }

    kp = weather.get("kp_current")
    solar_wind = weather.get("solar_wind_speed")
    bz = weather.get("bz")
    sfi = weather.get("sfi")

    if kp is None:
        return {
            "status": "DATA UNAVAILABLE",
            "detail": "Kp index data not available.",
        }

    impacts: List[str] = []
    if kp >= 7:
        status = "SEVERE"
        impacts.extend([
            "HF radio blackouts likely",
            "GPS accuracy significantly degraded",
            "LEO satellite drag increased 200-500%",
            "ISR satellite pointing accuracy degraded",
            "Satellite anomalies possible from charging effects",
        ])
    elif kp >= 5:
        status = "MODERATE"
        impacts.extend([
            "GPS accuracy reduced by 2-5x",
            "LEO satellite drag increased 50-200%",
            "HF communications intermittently disrupted at high latitudes",
            "Orbit predictions less reliable for LEO tracking",
        ])
    elif kp >= 4:
        status = "MINOR"
        impacts.extend([
            "Marginal HF propagation degradation at high latitudes",
            "Slight increase in LEO satellite drag",
            "GPS accuracy marginally affected",
        ])
    else:
        status = "NOMINAL"
        impacts.append("No significant space weather impact on operations")

    return {
        "status": status,
        "kp_index": kp,
        "solar_wind_speed_km_s": solar_wind,
        "imf_bz_nT": bz,
        "solar_flux_index": sfi,
        "operational_impacts": impacts,
        "detail": (
            f"Kp={kp}, Solar wind={solar_wind or 'N/A'} km/s, "
            f"IMF Bz={bz or 'N/A'} nT, SFI={sfi or 'N/A'}. "
            f"Space weather status: {status}."
        ),
    }


def _generate_watch_items(
    launches_data: list,
    weather: dict,
    hotspots: dict,
    stats: dict,
) -> List[str]:
    """Generate watch items for the next 24 hours."""
    items: List[str] = []

    # Upcoming adversary launches
    for launch in launches_data[:5]:
        provider = (launch.get("provider") or "").lower()
        if any(kw in provider for kw in ["casc", "china", "roscosmos", "russia", "iran", "dprk"]):
            items.append(
                f"LAUNCH WATCH: {launch.get('name', 'Unknown')} — "
                f"NET {launch.get('net', 'TBD')}"
            )

    # Space weather watch
    if isinstance(weather, dict):
        kp = weather.get("kp_current")
        if kp is not None and kp >= 4:
            items.append(
                f"SPACE WEATHER: Kp={kp} geomagnetic activity — monitor for "
                f"further escalation. Impact on ISR and GPS operations."
            )
        alerts = weather.get("alerts", [])
        if isinstance(alerts, list) and len(alerts) > 0:
            items.append(
                f"SWPC ALERTS: {len(alerts)} active alert(s) — review for "
                f"operational impact."
            )

    # Hotspot coverage
    if isinstance(hotspots, dict):
        most_covered = hotspots.get("most_covered_area", "")
        if most_covered:
            items.append(
                f"ISR COVERAGE: Highest adversary concentration over {most_covered} "
                f"— maintain surveillance of adversary collection activity."
            )

    # Standing watch items
    items.extend([
        "STANDING: Monitor PRC Yaogan constellation for new deployments or orbital adjustments",
        "STANDING: Track Russian inspector satellite activity near FVEY assets",
        "STANDING: Monitor DPRK/Iran for satellite launch preparations",
    ])

    return items


def _generate_analyst_recommendations(
    weather: dict,
    hotspots: dict,
    launches_data: list,
    stats: dict,
    correlations: dict,
) -> List[str]:
    """Generate analyst recommendations based on current conditions."""
    recs: List[str] = []

    # Space weather recommendation
    if isinstance(weather, dict):
        kp = weather.get("kp_current")
        if kp is not None and kp >= 5:
            recs.append(
                "RECOMMEND: Factor geomagnetic storm conditions into ISR coverage "
                "assessments — both FVEY and adversary systems are degraded. "
                "Consider rescheduling sensitive operations if dependent on "
                "precision ISR or GPS."
            )
        elif kp is not None and kp <= 1:
            recs.append(
                "RECOMMEND: Quiet space weather — adversary ISR at full capability. "
                "Exercise caution with exposed sensitive operations during clear "
                "geomagnetic conditions."
            )

    # Launch activity recommendation
    adv_launch_count = sum(
        1 for l in launches_data
        if any(kw in (l.get("provider") or "").lower()
               for kw in ["casc", "china", "roscosmos", "russia", "iran", "dprk"])
    )
    if adv_launch_count >= 3:
        recs.append(
            "RECOMMEND: Elevated adversary launch tempo — ensure post-launch "
            "tracking resources are allocated to characterize new deployments "
            "within 24 hours of each launch."
        )

    # Hotspot recommendation
    if isinstance(hotspots, dict):
        total = hotspots.get("total_passes_all_hotspots", 0)
        if total > 15:
            recs.append(
                "RECOMMEND: High adversary ISR activity across strategic hotspots. "
                "Coordinate with combatant commands to ensure sensitive activities "
                "account for adversary overhead collection windows."
            )

    # Standing recommendations
    recs.extend([
        "RECOMMEND: Continue monitoring PRC Shijian inspector satellites for "
        "maneuvers approaching FVEY GEO assets.",
        "RECOMMEND: Maintain enhanced tracking of adversary ELINT satellites "
        "over deployed naval forces — EMCON posture should reflect coverage.",
    ])

    return recs


def _build_executive_line(
    stats: dict,
    hotspots: dict,
    launches_data: list,
    weather: dict,
) -> str:
    """Build a one-line executive summary."""
    parts: List[str] = []

    if isinstance(stats, dict):
        prc_total = stats.get("PRC", {}).get("total", 0) if isinstance(stats.get("PRC"), dict) else 0
        cis_total = stats.get("CIS", {}).get("total", 0) if isinstance(stats.get("CIS"), dict) else 0
        parts.append(f"Tracking {prc_total} PRC and {cis_total} Russian satellites.")

    if isinstance(hotspots, dict):
        total_passes = hotspots.get("total_passes_all_hotspots", 0)
        if total_passes > 0:
            parts.append(
                f"{total_passes} adversary ISR passes across strategic hotspots."
            )

    adv_count = sum(
        1 for l in launches_data
        if any(kw in (l.get("provider") or "").lower()
               for kw in ["casc", "china", "roscosmos", "russia"])
    )
    if adv_count > 0:
        parts.append(f"{adv_count} adversary launches in manifest.")

    if isinstance(weather, dict):
        kp = weather.get("kp_current")
        if kp is not None:
            if kp >= 5:
                parts.append(f"Space weather: storm conditions (Kp={kp}).")
            else:
                parts.append(f"Space weather: nominal (Kp={kp}).")

    return " ".join(parts)
