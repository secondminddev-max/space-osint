"""
Space Warfare Overmatch Calculator — Real-Time Contested Zone Analysis
Calculates domain-by-domain advantage for FVEY vs adversary across strategic zones.

Domains assessed:
- ISR (Intelligence, Surveillance, Reconnaissance)
- COMMS (Communications / C2)
- PNT (Position, Navigation, Timing)
- SDA (Space Domain Awareness)
- ASAT (Counter-space / Anti-satellite)
- EW (Electronic Warfare)

All data from open-source intelligence and real-time satellite catalog.
Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import httpx

from data_sources.celestrak import propagate_satellite, fetch_catalog
from data_sources.adversary_sats import (
    identify_country,
    identify_fvey_country,
    classify_satellite,
    classify_fvey_satellite,
    _alt_from_period,
    _orbital_regime,
)
from data_sources.ground_stations import get_adversary_stations, get_fvey_stations
from data_sources.missile_intel import (
    get_missile_asat_data,
    get_by_country as get_missiles_by_country,
    TYPE_DA_ASAT,
    TYPE_CO_ORBITAL,
    TYPE_RPO,
    TYPE_DEW,
    TYPE_EW,
    TYPE_CYBER,
    STATUS_OPERATIONAL,
    STATUS_TESTED,
)

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache: Dict[str, dict] = {}
_OVERMATCH_TTL = 120  # 2 minutes


def _cached(key: str) -> Optional[dict]:
    cached = _cache.get(key)
    if cached and (time.time() - cached["ts"]) < _OVERMATCH_TTL:
        return cached["data"]
    return None


def _store(key: str, data: dict) -> dict:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# ---------------------------------------------------------------------------
# Strategic Zones — the flashpoints that matter
# ---------------------------------------------------------------------------
STRATEGIC_ZONES = [
    {"name": "Taiwan Strait", "lat": 23.5, "lng": 120.5,
     "primary_adversary": "PRC",
     "context": "Primary INDOPACOM flashpoint. PRC military buildup and grey-zone operations ongoing."},
    {"name": "South China Sea", "lat": 12.0, "lng": 115.0,
     "primary_adversary": "PRC",
     "context": "Contested maritime domain. PRC island fortification and military ISR focus area."},
    {"name": "Korean Peninsula", "lat": 38.0, "lng": 127.0,
     "primary_adversary": "PRC",
     "context": "DPRK nuclear/missile threat. PRC provides strategic overwatch. US/ROK alliance zone."},
    {"name": "Baltic Sea", "lat": 57.0, "lng": 20.0,
     "primary_adversary": "CIS",
     "context": "NATO eastern flank. Russian EW operations and GPS jamming routinely detected."},
    {"name": "Persian Gulf", "lat": 26.0, "lng": 52.0,
     "primary_adversary": "IRAN",
     "context": "Strait of Hormuz critical chokepoint. Iranian GPS spoofing and EW activity."},
    {"name": "Arctic", "lat": 75.0, "lng": 40.0,
     "primary_adversary": "CIS",
     "context": "Emerging strategic domain. Russian Northern Fleet and nuclear submarine bastion."},
]


# ---------------------------------------------------------------------------
# Haversine (distance calc for satellite-to-zone coverage)
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


def _coverage_radius_km(alt_km: float) -> float:
    """Approximate ground coverage radius for a satellite at given altitude.
    Uses minimum elevation angle of ~10 degrees for ISR-relevant coverage."""
    if alt_km <= 0:
        return 0
    R = 6371.0
    # Half-angle at earth center for 10-deg min elevation
    # theta = arccos(R/(R+h) * cos(el)) - el
    el_rad = math.radians(10.0)
    ratio = R / (R + alt_km)
    if ratio * math.cos(el_rad) > 1.0:
        return 0
    theta = math.acos(ratio * math.cos(el_rad)) - el_rad
    return R * theta


# ---------------------------------------------------------------------------
# Internal: count satellites in coverage of a zone, by side and mission
# ---------------------------------------------------------------------------

async def _count_satellites_over_zone(
    client: httpx.AsyncClient,
    lat: float,
    lng: float,
) -> Dict[str, dict]:
    """Count adversary and FVEY satellites that can cover a zone right now.

    Returns dict with adversary and fvey sub-dicts by category.
    """
    catalog = await fetch_catalog(client, "active")

    adv_counts: Dict[str, int] = {
        "military_isr": 0, "navigation": 0, "comms": 0,
        "sda_asat": 0, "early_warning": 0, "unknown": 0,
        "human_spaceflight": 0, "civil_scientific": 0,
    }
    fvey_counts: Dict[str, int] = {
        "military_isr": 0, "navigation": 0, "comms": 0,
        "sda_asat": 0, "early_warning": 0, "unknown": 0,
        "civil_scientific": 0,
    }

    adv_sats: List[dict] = []
    fvey_sats: List[dict] = []

    for gp in catalog:
        name = gp.get("OBJECT_NAME", "")
        mm = float(gp.get("MEAN_MOTION", 0) or 0)
        if mm <= 0:
            continue

        period = 1440.0 / mm
        alt = _alt_from_period(period)
        regime = _orbital_regime(period, alt)

        # Determine coverage radius for this satellite
        cov_radius = _coverage_radius_km(alt)
        if cov_radius <= 0:
            continue

        # Propagate position
        pos = propagate_satellite(gp)
        if pos is None:
            continue

        dist = _haversine_km(lat, lng, pos["lat"], pos["lng"])

        # For GEO satellites, they cover a huge area — use generous radius
        if regime == "GEO":
            effective_radius = 8500.0  # ~70 deg Earth-central angle
        elif regime == "HEO":
            effective_radius = max(cov_radius, 5000.0)
        else:
            effective_radius = cov_radius

        if dist > effective_radius:
            continue

        # This satellite covers the zone — classify it
        adv_country = identify_country(name)
        fvey_country = identify_fvey_country(name)

        if adv_country:
            cat = classify_satellite(name, adv_country)
            adv_counts[cat] = adv_counts.get(cat, 0) + 1
            adv_sats.append({
                "name": name, "country": adv_country, "category": cat,
                "alt_km": round(alt, 0), "regime": regime,
                "dist_km": round(dist, 0),
            })
        elif fvey_country:
            cat = classify_fvey_satellite(name)
            fvey_counts[cat] = fvey_counts.get(cat, 0) + 1
            fvey_sats.append({
                "name": name, "country": fvey_country, "category": cat,
                "alt_km": round(alt, 0), "regime": regime,
                "dist_km": round(dist, 0),
            })

    return {
        "adversary": {
            "counts": adv_counts,
            "total": sum(adv_counts.values()),
            "satellites": sorted(adv_sats, key=lambda s: s["dist_km"])[:20],
        },
        "fvey": {
            "counts": fvey_counts,
            "total": sum(fvey_counts.values()),
            "satellites": sorted(fvey_sats, key=lambda s: s["dist_km"])[:20],
        },
    }


# ---------------------------------------------------------------------------
# Ground station proximity to zone
# ---------------------------------------------------------------------------

def _ground_stations_in_range(lat: float, lng: float, max_range_km: float = 5000.0) -> Dict[str, int]:
    """Count adversary vs FVEY ground stations within range of a zone."""
    adv_stations = get_adversary_stations()
    fvey_stations = get_fvey_stations()
    adv_count = 0
    fvey_count = 0
    adv_surveillance = 0
    fvey_surveillance = 0

    for s in adv_stations:
        d = _haversine_km(lat, lng, s["lat"], s["lng"])
        if d <= max_range_km:
            adv_count += 1
            if s.get("type") in ("surveillance", "radar"):
                adv_surveillance += 1

    for s in fvey_stations:
        d = _haversine_km(lat, lng, s["lat"], s["lng"])
        if d <= max_range_km:
            fvey_count += 1
            if s.get("type") in ("surveillance", "radar"):
                fvey_surveillance += 1

    return {
        "adversary_total": adv_count,
        "fvey_total": fvey_count,
        "adversary_surveillance": adv_surveillance,
        "fvey_surveillance": fvey_surveillance,
    }


# ---------------------------------------------------------------------------
# ASAT capability scoring
# ---------------------------------------------------------------------------

def _score_asat_capability(primary_adversary: str) -> dict:
    """Score ASAT capability based on missile_intel data."""
    # Map adversary codes to missile_intel country names
    country_map = {
        "PRC": "PRC",
        "CIS": "Russia",
        "NKOR": "DPRK",
        "IRAN": "Iran",
    }

    adversary_systems = []
    adversary_da_asat = 0
    adversary_co_orbital = 0
    adversary_total_systems = 0

    # Get primary adversary systems
    primary_name = country_map.get(primary_adversary, primary_adversary)
    primary_systems = get_missiles_by_country(primary_name)

    for s in primary_systems:
        if s.get("status") in (STATUS_OPERATIONAL, STATUS_TESTED):
            adversary_total_systems += 1
            if s["type"] == TYPE_DA_ASAT:
                adversary_da_asat += 1
                adversary_systems.append(s["name"])
            elif s["type"] in (TYPE_CO_ORBITAL, TYPE_RPO):
                adversary_co_orbital += 1
                adversary_systems.append(s["name"])

    # FVEY counter-space: assessed capabilities (open source)
    # US has SM-3 demonstrated ASAT, GSSAP for RPO, undisclosed programs
    fvey_da_asat = 1   # SM-3 demonstrated (Operation Burnt Frost)
    fvey_co_orbital = 2  # GSSAP x2 for RPO/inspection
    fvey_total_systems = 3

    # Score: adversary advantage if more operational ASAT systems
    adv_score = adversary_da_asat * 15 + adversary_co_orbital * 10
    fvey_score = fvey_da_asat * 15 + fvey_co_orbital * 10

    raw = fvey_score - adv_score
    # Clamp to -100..+100
    score = max(-100, min(100, raw))

    return {
        "adversary_systems": adversary_total_systems,
        "adversary_da_asat": adversary_da_asat,
        "adversary_co_orbital": adversary_co_orbital,
        "adversary_system_names": adversary_systems,
        "fvey_systems": fvey_total_systems,
        "score": score,
    }


# ---------------------------------------------------------------------------
# EW capability scoring
# ---------------------------------------------------------------------------

def _score_ew_capability(primary_adversary: str, zone_lat: float, zone_lng: float) -> dict:
    """Score EW capability based on known systems and ground station proximity."""
    country_map = {
        "PRC": "PRC",
        "CIS": "Russia",
        "NKOR": "DPRK",
        "IRAN": "Iran",
    }
    primary_name = country_map.get(primary_adversary, primary_adversary)
    systems = get_missiles_by_country(primary_name)

    adv_ew_count = 0
    adv_ew_systems = []
    for s in systems:
        if s["type"] == TYPE_EW and s.get("status") in (STATUS_OPERATIONAL, STATUS_TESTED):
            adv_ew_count += 1
            adv_ew_systems.append(s["name"])

    # Ground proximity factor — closer adversary ground stations = more EW threat
    gs = _ground_stations_in_range(zone_lat, zone_lng, 3000.0)

    # Adversary EW score: systems + ground station proximity
    adv_score = adv_ew_count * 12 + gs["adversary_total"] * 3
    # FVEY EW resilience: anti-jam improvements, M-code GPS
    fvey_resilience = 15 + gs["fvey_total"] * 2

    raw = fvey_resilience - adv_score
    score = max(-100, min(100, raw))

    return {
        "adversary_ew_systems": adv_ew_count,
        "adversary_ew_names": adv_ew_systems,
        "adversary_ground_stations_nearby": gs["adversary_total"],
        "fvey_ground_stations_nearby": gs["fvey_total"],
        "score": score,
    }


# ---------------------------------------------------------------------------
# Domain scoring helpers
# ---------------------------------------------------------------------------

def _domain_score(adversary_count: int, fvey_count: int, weight: float = 1.0) -> int:
    """Calculate domain score from satellite counts.
    Returns -100 to +100. Negative = adversary advantage."""
    total = adversary_count + fvey_count
    if total == 0:
        return 0
    # Ratio-based scoring
    fvey_ratio = fvey_count / total
    # Map 0..1 ratio to -100..+100
    raw = (fvey_ratio - 0.5) * 200.0 * weight
    return max(-100, min(100, int(round(raw))))


def _assess_domain(domain: str, score: int, adv_count: int, fvey_count: int,
                   primary_adversary: str) -> str:
    """Generate human-readable assessment for a domain score."""
    adv_name = {
        "PRC": "PRC", "CIS": "Russia", "NKOR": "DPRK", "IRAN": "Iran"
    }.get(primary_adversary, primary_adversary)

    if score <= -60:
        status = f"{adv_name} DOMINANT"
    elif score <= -20:
        status = f"{adv_name} ADVANTAGE"
    elif score <= 20:
        status = "CONTESTED / NEAR PARITY"
    elif score <= 60:
        status = "FVEY ADVANTAGE"
    else:
        status = "FVEY DOMINANT"

    details = {
        "ISR": {
            "adversary_focus": "Yaogan, Jilin, Gaofen constellations" if adv_name == "PRC" else "Kondor, Liana, Bars series" if adv_name == "Russia" else "limited ISR",
            "fvey_focus": "NRO assets, commercial augmentation (Maxar, Planet)",
        },
        "COMMS": {
            "adversary_focus": "Zhongxing, Fenghuo MILSATCOM" if adv_name == "PRC" else "Blagovest, Meridian series" if adv_name == "Russia" else "limited SATCOM",
            "fvey_focus": "WGS, AEHF, MUOS, Starlink augmentation",
        },
        "PNT": {
            "adversary_focus": "BeiDou (35 sats, global)" if adv_name == "PRC" else "GLONASS (24 sats)" if adv_name == "Russia" else "GPS-dependent",
            "fvey_focus": "GPS (31 sats), augmented by allied GNSS",
        },
        "SDA": {
            "adversary_focus": "Shijian series, ground radar" if adv_name == "PRC" else "Okno/Krona optical, Voronezh radar" if adv_name == "Russia" else "minimal SDA",
            "fvey_focus": "GSSAP, Space Fence, SSN, commercial SSA",
        },
    }

    domain_detail = details.get(domain, {})
    adv_desc = domain_detail.get("adversary_focus", "")
    fvey_desc = domain_detail.get("fvey_focus", "")

    parts = [status]
    if adv_count > 0 or fvey_count > 0:
        parts.append(f"{adv_count} adversary vs {fvey_count} FVEY assets in coverage")
    if adv_desc:
        parts.append(f"Adversary: {adv_desc}")
    if fvey_desc:
        parts.append(f"FVEY: {fvey_desc}")

    return " -- ".join(parts)


def _overall_assessment(score: int) -> str:
    """Convert score to overall overmatch verdict."""
    if score <= -20:
        return "ADVERSARY"
    elif score >= 20:
        return "FVEY"
    return "CONTESTED"


def _trend_assessment(domains: dict) -> str:
    """Assess trend based on domain balance."""
    # Count domains where adversary has advantage
    adv_domains = sum(1 for d in domains.values() if d.get("score", 0) < -15)
    fvey_domains = sum(1 for d in domains.values() if d.get("score", 0) > 15)

    if adv_domains >= 4:
        return "CRITICAL — FVEY position severely disadvantaged across multiple domains"
    if adv_domains >= 3:
        return "DETERIORATING — Adversary holds advantage in majority of domains"
    if adv_domains == fvey_domains:
        return "STABLE — Domain advantages roughly balanced"
    if fvey_domains >= 3:
        return "FAVORABLE — FVEY maintains advantage in majority of domains"
    return "MIXED — No clear dominant position; contested across multiple domains"


# ---------------------------------------------------------------------------
# Main calculator
# ---------------------------------------------------------------------------

async def calculate_zone_overmatch(
    client: httpx.AsyncClient,
    lat: float,
    lng: float,
    zone_name: str,
    primary_adversary: str = "PRC",
    context: str = "",
) -> dict:
    """Full overmatch calculation for one strategic zone.

    Args:
        client: httpx async client
        lat: zone center latitude
        lng: zone center longitude
        zone_name: human-readable zone name
        primary_adversary: PRC, CIS, NKOR, IRAN
        context: strategic context string

    Returns:
        Comprehensive overmatch assessment dict
    """
    cache_key = f"overmatch_{lat:.1f}_{lng:.1f}"
    cached = _cached(cache_key)
    if cached is not None:
        return cached

    now = datetime.now(timezone.utc)

    # Get satellite coverage counts
    sat_data = await _count_satellites_over_zone(client, lat, lng)
    adv = sat_data["adversary"]
    fvey = sat_data["fvey"]
    adv_c = adv["counts"]
    fvey_c = fvey["counts"]

    # -- ISR Domain --
    adv_isr = adv_c.get("military_isr", 0) + adv_c.get("early_warning", 0)
    fvey_isr = fvey_c.get("military_isr", 0) + fvey_c.get("early_warning", 0)
    isr_score = _domain_score(adv_isr, fvey_isr, weight=1.2)
    isr_assessment = _assess_domain("ISR", isr_score, adv_isr, fvey_isr, primary_adversary)

    # -- COMMS Domain --
    adv_comms = adv_c.get("comms", 0)
    fvey_comms = fvey_c.get("comms", 0)
    comms_score = _domain_score(adv_comms, fvey_comms)
    comms_assessment = _assess_domain("COMMS", comms_score, adv_comms, fvey_comms, primary_adversary)

    # -- PNT Domain --
    adv_pnt = adv_c.get("navigation", 0)
    fvey_pnt = fvey_c.get("navigation", 0)
    pnt_score = _domain_score(adv_pnt, fvey_pnt)
    pnt_assessment = _assess_domain("PNT", pnt_score, adv_pnt, fvey_pnt, primary_adversary)

    # -- SDA Domain --
    adv_sda = adv_c.get("sda_asat", 0)
    fvey_sda = fvey_c.get("sda_asat", 0)
    # Add ground station surveillance assets
    gs = _ground_stations_in_range(lat, lng, 5000.0)
    adv_sda_total = adv_sda + gs["adversary_surveillance"]
    fvey_sda_total = fvey_sda + gs["fvey_surveillance"]
    sda_score = _domain_score(adv_sda_total, fvey_sda_total, weight=0.8)
    sda_assessment = _assess_domain("SDA", sda_score, adv_sda_total, fvey_sda_total, primary_adversary)

    # -- ASAT Domain --
    asat_data = _score_asat_capability(primary_adversary)
    asat_score = asat_data["score"]
    adv_name = {"PRC": "PRC", "CIS": "Russia", "NKOR": "DPRK", "IRAN": "Iran"}.get(
        primary_adversary, primary_adversary)
    if asat_score <= -20:
        asat_assessment = (
            f"{adv_name} holds ASAT advantage with {asat_data['adversary_da_asat']} DA-ASAT "
            f"and {asat_data['adversary_co_orbital']} co-orbital systems "
            f"({', '.join(asat_data['adversary_system_names'][:5])}). "
            f"FVEY counter-space options limited to SM-3 and GSSAP."
        )
    elif asat_score >= 20:
        asat_assessment = (
            f"FVEY maintains counter-space advantage. {adv_name} has "
            f"{asat_data['adversary_systems']} assessed systems but limited operational readiness."
        )
    else:
        asat_assessment = (
            f"CONTESTED — {adv_name} has {asat_data['adversary_systems']} counter-space systems "
            f"including {asat_data['adversary_da_asat']} DA-ASAT. FVEY has SM-3 ASAT-capable "
            f"and GSSAP RPO platforms."
        )

    # -- EW Domain --
    ew_data = _score_ew_capability(primary_adversary, lat, lng)
    ew_score = ew_data["score"]
    if ew_score <= -20:
        ew_assessment = (
            f"{adv_name} GPS/SATCOM jamming advantage with {ew_data['adversary_ew_systems']} "
            f"operational EW systems and {ew_data['adversary_ground_stations_nearby']} ground "
            f"stations within range. FVEY SATCOM resilience improving but GPS vulnerability persists."
        )
    elif ew_score >= 20:
        ew_assessment = (
            f"FVEY EW resilience adequate. {adv_name} has {ew_data['adversary_ew_systems']} "
            f"EW systems but limited regional coverage."
        )
    else:
        ew_assessment = (
            f"CONTESTED — {adv_name} has {ew_data['adversary_ew_systems']} EW systems; "
            f"FVEY deploying anti-jam and M-code GPS. Ground station balance: "
            f"{ew_data['adversary_ground_stations_nearby']} adversary vs "
            f"{ew_data['fvey_ground_stations_nearby']} FVEY within range."
        )

    # Build domains dict
    domains = {
        "ISR": {
            "adversary": adv_isr,
            "fvey": fvey_isr,
            "score": isr_score,
            "assessment": isr_assessment,
        },
        "COMMS": {
            "adversary": adv_comms,
            "fvey": fvey_comms,
            "score": comms_score,
            "assessment": comms_assessment,
        },
        "PNT": {
            "adversary": adv_pnt,
            "fvey": fvey_pnt,
            "score": pnt_score,
            "assessment": pnt_assessment,
        },
        "SDA": {
            "adversary": adv_sda_total,
            "fvey": fvey_sda_total,
            "score": sda_score,
            "assessment": sda_assessment,
        },
        "ASAT": {
            "adversary_systems": asat_data["adversary_systems"],
            "adversary_da_asat": asat_data["adversary_da_asat"],
            "adversary_co_orbital": asat_data["adversary_co_orbital"],
            "fvey_systems": asat_data["fvey_systems"],
            "score": asat_score,
            "assessment": asat_assessment,
        },
        "EW": {
            "adversary_ew_systems": ew_data["adversary_ew_systems"],
            "fvey_ground_stations": ew_data["fvey_ground_stations_nearby"],
            "score": ew_score,
            "assessment": ew_assessment,
        },
    }

    # Overall overmatch score: weighted average of domain scores
    weights = {"ISR": 0.25, "COMMS": 0.20, "PNT": 0.15, "SDA": 0.10, "ASAT": 0.20, "EW": 0.10}
    total_weight = sum(weights.values())
    overmatch_score = int(round(
        sum(domains[d]["score"] * weights[d] for d in weights) / total_weight
    ))
    overmatch_score = max(-100, min(100, overmatch_score))

    overall = _overall_assessment(overmatch_score)
    trend = _trend_assessment(domains)

    # Key finding — the one-paragraph that matters
    # Find the domain with worst FVEY score
    worst_domain = min(domains.items(), key=lambda x: x[1]["score"])
    best_domain = max(domains.items(), key=lambda x: x[1]["score"])

    key_finding = (
        f"{adv_name} {'holds overall advantage' if overall == 'ADVERSARY' else 'is contested' if overall == 'CONTESTED' else 'is at disadvantage'} "
        f"in the {zone_name} (overmatch score: {overmatch_score}). "
        f"Critical gap: {worst_domain[0]} domain (score {worst_domain[1]['score']}). "
        f"FVEY strongest in {best_domain[0]} domain (score {best_domain[1]['score']}). "
        f"Total assets in coverage: {adv['total']} adversary vs {fvey['total']} FVEY satellites."
    )

    # Recommendation
    priority_actions = []
    if domains["ISR"]["score"] < -20:
        priority_actions.append("Deploy additional ISR assets or commercial augmentation to close coverage gap")
    if domains["COMMS"]["score"] < -20:
        priority_actions.append("Harden SATCOM links and expand protected communications capacity")
    if domains["PNT"]["score"] < -10:
        priority_actions.append("Accelerate M-code GPS rollout and alternative PNT development")
    if domains["ASAT"]["score"] < -20:
        priority_actions.append("Develop counter-ASAT deterrence options and satellite hardening")
    if domains["EW"]["score"] < -20:
        priority_actions.append("Deploy anti-jam receivers and SATCOM frequency diversity")
    if domains["SDA"]["score"] < -10:
        priority_actions.append("Expand SSA sensor coverage in this region")
    if not priority_actions:
        priority_actions.append("Maintain current force posture; monitor for adversary capability changes")

    recommendation = "Priority actions: " + "; ".join(priority_actions)

    result = {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "zone": zone_name,
        "lat": lat,
        "lng": lng,
        "primary_adversary": primary_adversary,
        "context": context,
        "overall_overmatch": overall,
        "overmatch_score": overmatch_score,
        "domains": domains,
        "trend": trend,
        "key_finding": key_finding,
        "recommendation": recommendation,
        "satellite_summary": {
            "adversary_total": adv["total"],
            "fvey_total": fvey["total"],
            "adversary_top_assets": adv["satellites"][:10],
            "fvey_top_assets": fvey["satellites"][:10],
        },
        "ground_station_proximity": gs,
    }

    return _store(cache_key, result)


# ---------------------------------------------------------------------------
# All zones
# ---------------------------------------------------------------------------

async def calculate_all_overmatches(client: httpx.AsyncClient) -> dict:
    """Calculate overmatch for all 6 strategic zones."""
    cached = _cached("overmatch_all")
    if cached is not None:
        return cached

    import asyncio
    now = datetime.now(timezone.utc)

    tasks = [
        calculate_zone_overmatch(
            client, z["lat"], z["lng"], z["name"],
            z["primary_adversary"], z.get("context", ""),
        )
        for z in STRATEGIC_ZONES
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    zones = []
    for zone_def, result in zip(STRATEGIC_ZONES, results):
        if isinstance(result, Exception):
            zones.append({
                "zone": zone_def["name"],
                "lat": zone_def["lat"],
                "lng": zone_def["lng"],
                "error": str(result),
                "overmatch_score": 0,
                "overall_overmatch": "ERROR",
            })
        else:
            zones.append(result)

    data = {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "total_zones": len(zones),
        "zones": zones,
    }

    return _store("overmatch_all", data)


# ---------------------------------------------------------------------------
# Global summary
# ---------------------------------------------------------------------------

async def get_global_overmatch_summary(client: httpx.AsyncClient) -> dict:
    """Aggregate overmatch score across all zones — the strategic picture."""
    cached = _cached("overmatch_summary")
    if cached is not None:
        return cached

    all_data = await calculate_all_overmatches(client)
    now = datetime.now(timezone.utc)

    zones = all_data.get("zones", [])
    valid_zones = [z for z in zones if "overmatch_score" in z and z.get("overall_overmatch") != "ERROR"]

    if not valid_zones:
        return _store("overmatch_summary", {
            "classification": "UNCLASSIFIED // OSINT",
            "generated_utc": now.isoformat(),
            "error": "No valid zone calculations available",
        })

    # Global aggregate
    avg_score = int(round(sum(z["overmatch_score"] for z in valid_zones) / len(valid_zones)))
    worst_zone = min(valid_zones, key=lambda z: z["overmatch_score"])
    best_zone = max(valid_zones, key=lambda z: z["overmatch_score"])

    adversary_advantage_zones = [z["zone"] for z in valid_zones if z["overmatch_score"] < -20]
    fvey_advantage_zones = [z["zone"] for z in valid_zones if z["overmatch_score"] > 20]
    contested_zones = [z["zone"] for z in valid_zones if -20 <= z["overmatch_score"] <= 20]

    # Domain averages across all zones
    domain_averages: Dict[str, float] = {}
    for domain_name in ("ISR", "COMMS", "PNT", "SDA", "ASAT", "EW"):
        scores = []
        for z in valid_zones:
            d = z.get("domains", {}).get(domain_name, {})
            if "score" in d:
                scores.append(d["score"])
        if scores:
            domain_averages[domain_name] = int(round(sum(scores) / len(scores)))

    # Weakest domain globally
    weakest_domain = min(domain_averages.items(), key=lambda x: x[1]) if domain_averages else ("N/A", 0)
    strongest_domain = max(domain_averages.items(), key=lambda x: x[1]) if domain_averages else ("N/A", 0)

    # Global assessment
    if avg_score <= -30:
        global_assessment = (
            "CRITICAL: Adversary holds significant overmatch across strategic zones. "
            "FVEY space architecture faces systemic disadvantage, particularly in ISR "
            "and counter-space domains. Urgent investment required."
        )
    elif avg_score <= -10:
        global_assessment = (
            "DISADVANTAGED: Adversary maintains advantage in key strategic zones. "
            "FVEY retains select domain advantages (SATCOM, SDA) but the overall "
            "balance is unfavorable and trending negative."
        )
    elif avg_score <= 10:
        global_assessment = (
            "CONTESTED: No clear overall advantage for either side across strategic zones. "
            "FVEY maintains edge in SATCOM and SDA but adversary ISR and ASAT capabilities "
            "create parity or local advantage in critical areas."
        )
    elif avg_score <= 30:
        global_assessment = (
            "FAVORABLE: FVEY maintains overall space advantage but faces growing challenges "
            "in specific domains and zones. Adversary counter-space investment is eroding "
            "margins, particularly in the Western Pacific."
        )
    else:
        global_assessment = (
            "DOMINANT: FVEY maintains clear space overmatch across most strategic zones "
            "and domains. Continued investment required to sustain advantage."
        )

    summary = {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "global_overmatch_score": avg_score,
        "global_assessment": global_assessment,
        "zones_analyzed": len(valid_zones),
        "adversary_advantage_zones": adversary_advantage_zones,
        "fvey_advantage_zones": fvey_advantage_zones,
        "contested_zones": contested_zones,
        "worst_zone": {
            "name": worst_zone["zone"],
            "score": worst_zone["overmatch_score"],
            "primary_adversary": worst_zone.get("primary_adversary", ""),
        },
        "best_zone": {
            "name": best_zone["zone"],
            "score": best_zone["overmatch_score"],
        },
        "domain_averages": domain_averages,
        "weakest_domain": {
            "domain": weakest_domain[0],
            "avg_score": weakest_domain[1],
        },
        "strongest_domain": {
            "domain": strongest_domain[0],
            "avg_score": strongest_domain[1],
        },
        "zone_scores": [
            {"zone": z["zone"], "score": z["overmatch_score"], "overall": z["overall_overmatch"]}
            for z in valid_zones
        ],
    }

    return _store("overmatch_summary", summary)
