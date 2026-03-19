"""
Advanced Space Intelligence Module — Echelon Vantage
====================================================

Implements advanced space domain awareness capabilities informed by
state-of-the-art systems and operational requirements:

- **RPO Risk Monitor** — Identifies adversary satellites in similar orbital
  regimes to FVEY military assets, flags potential rendezvous/proximity
  operations based on orbital plane similarity (RAAN, inclination, altitude).
  Inspired by LeoLabs Watchkeeper, ExoAnalytic RPO alerts, and GSSAP mission.

- **Debris Cascade Risk Calculator** — Models debris generation from a
  hypothetical ASAT event at a given altitude using simplified NASA Standard
  Breakup Model (SBM) estimates. Assesses which FVEY constellations face
  increased collision risk. Based on Kessler/Liou cascade models and
  ESA MASTER/ORDEM orbital debris assessments.

- **Space Weather Operational Impact** — Translates real-time NOAA SWPC data
  (Kp, Bz, NOAA R/S/G scales) into specific military operational impacts on
  FVEY capabilities: satellite drag, HF comms, GPS accuracy, ISR degradation.
  Mirrors USSF 2nd Weather Squadron operational products.

- **Launch Window Predictor** — For known adversary launch sites, calculates
  next favorable launch windows for various target orbits (SSO, LEO, GEO).
  Uses site latitude constraints and orbital mechanics fundamentals.

- **Treaty & Norms Tracker** — Monitors key space governance frameworks:
  Outer Space Treaty, PAROS, ASAT moratoriums, Artemis Accords, responsible
  behaviors. Status tracking for FVEY policy coordination.

- **Spectrum Assessment** — Evaluates electromagnetic spectrum threats in
  the space domain: GPS jamming events, SATCOM interference, directed energy,
  and ASAT-related EW capabilities by nation.

Data sources: CelesTrak (GP elements), NOAA SWPC (space weather),
open-source intelligence (NASIC, SWF, DIA, CSIS reports).

Classification: UNCLASSIFIED // OSINT // REL TO FVEY
"""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

import httpx

from data_sources.celestrak import fetch_catalog, propagate_satellite
from data_sources.adversary_sats import (
    identify_country,
    identify_fvey_country,
    classify_satellite,
    classify_fvey_satellite,
)
from data_sources.space_weather import fetch_weather_composite


# ---------------------------------------------------------------------------
# Cache infrastructure
# ---------------------------------------------------------------------------

_cache: Dict[str, dict] = {}
_ADVANCED_TTL = 180  # 3 minutes


def _cached(key: str) -> Optional[dict]:
    cached = _cache.get(key)
    if cached and (time.time() - cached["ts"]) < _ADVANCED_TTL:
        return cached["data"]
    return None


def _store(key: str, data: dict) -> dict:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_R_EARTH_KM = 6371.0
_MU_EARTH = 398600.4418  # km^3/s^2


def _alt_from_period(period_min: float) -> float:
    """Estimate altitude from orbital period."""
    if period_min <= 0:
        return 0.0
    T_sec = period_min * 60.0
    a = (_MU_EARTH * (T_sec / (2 * math.pi)) ** 2) ** (1.0 / 3.0)
    return max(a - _R_EARTH_KM, 0.0)


def _period_from_mm(mean_motion: float) -> float:
    """Period in minutes from mean motion (rev/day)."""
    if mean_motion <= 0:
        return 0.0
    return 1440.0 / mean_motion


# =========================================================================
# 1. RPO RISK MONITOR
# =========================================================================
#
# Concept: Rendezvous & Proximity Operations (RPO) require the adversary
# satellite to be in a similar orbital plane (inclination + RAAN) and at a
# similar altitude. The GSSAP satellites in GEO do exactly this — they
# loiter near adversary GEO assets for inspection.
#
# We compare orbital parameters (not instantaneous positions) to find
# adversary sats that COULD perform RPO against FVEY military assets.
# This is a persistent threat assessment, not just a point-in-time check
# (which the proximity_alert module handles).
#
# Key parameters:
# - Inclination match: within 2 degrees
# - Altitude match: within 100 km (LEO) or 500 km (GEO/MEO)
# - RAAN match: within 15 degrees (same orbital plane)
#
# References:
# - Brian Weeden, "The Space Review: The continuing saga of Cosmos 2542/2543"
# - SWF Global Counterspace Capabilities report (RPO capabilities section)
# - CSpOC conjunction screening methodology
# =========================================================================

# FVEY military satellite patterns that are highest-priority assets
import re

_FVEY_HIGH_VALUE = re.compile(
    r"GPS|NAVSTAR|SBIRS|STSS|DSP|WGS|AEHF|MUOS|MILSTAR|GSSAP|"
    r"USA[ -]\d|NROL|SKYNET|SAPPHIRE|NEOSSAT|SBSS|"
    r"MENTOR|ORION|TRUMPET|ONYX|LACROSSE",
    re.IGNORECASE,
)


def _raan_difference(raan1: float, raan2: float) -> float:
    """Angular difference in RAAN, accounting for 360-degree wrap."""
    diff = abs(raan1 - raan2) % 360.0
    return min(diff, 360.0 - diff)


def _orbital_regime_label(alt_km: float) -> str:
    if alt_km < 2000:
        return "LEO"
    if alt_km < 35000:
        return "MEO"
    if alt_km < 36500:
        return "GEO"
    return "HEO"


def _rpo_threat_level(
    inc_diff: float,
    alt_diff: float,
    raan_diff: float,
    adv_category: str,
) -> Tuple[str, str]:
    """Assess RPO threat based on orbital parameter similarity.

    Returns (threat_level, rationale).
    """
    # Known SDA/ASAT sats always elevated
    is_sda_asat = adv_category in ("sda_asat", "military_isr")

    if inc_diff < 1.0 and alt_diff < 50 and raan_diff < 5:
        level = "CRITICAL"
        rationale = "Near-coplanar orbit within 50 km altitude band"
    elif inc_diff < 2.0 and alt_diff < 100 and raan_diff < 10:
        level = "HIGH"
        rationale = "Similar orbital plane, altitude match within 100 km"
    elif inc_diff < 3.0 and alt_diff < 200 and raan_diff < 15:
        level = "ELEVATED"
        rationale = "Reachable orbital plane with moderate delta-v"
    elif inc_diff < 5.0 and alt_diff < 500:
        level = "MODERATE"
        rationale = "Same altitude band, plane change feasible"
    else:
        level = "LOW"
        rationale = "Different orbital regime or large plane separation"

    # Elevate if the adversary sat is a known SDA/ASAT platform
    if is_sda_asat and level in ("MODERATE", "LOW"):
        level = "ELEVATED"
        rationale += " — adversary platform has known RPO/inspection capability"

    return level, rationale


async def check_rpo_risks(client: httpx.AsyncClient) -> dict:
    """Identify adversary satellites in similar orbits to FVEY military assets.

    Compares orbital planes (RAAN, inclination) and altitudes to flag pairs
    where an adversary satellite could perform RPO against a FVEY asset.

    Unlike the proximity_alert module (which checks instantaneous positions),
    this assesses PERSISTENT orbital geometry threats — an adversary sat in
    the same orbital plane is always a concern, regardless of current phase.
    """
    cached = _cached("rpo_risks")
    if cached is not None:
        return cached

    catalog = await fetch_catalog(client, "active")
    now = datetime.now(timezone.utc)

    # Phase 1: Separate FVEY military and adversary satellites with their
    # orbital parameters (not propagated positions — we need Keplerian elements)
    fvey_assets: List[dict] = []
    adversary_assets: List[dict] = []

    for gp in catalog:
        name = gp.get("OBJECT_NAME", "")
        norad_id = int(gp.get("NORAD_CAT_ID", 0))
        inc = float(gp.get("INCLINATION", 0))
        raan = float(gp.get("RA_OF_ASC_NODE", 0))
        mm = float(gp.get("MEAN_MOTION", 0))
        period = _period_from_mm(mm)
        alt = _alt_from_period(period)
        regime = _orbital_regime_label(alt)

        if _FVEY_HIGH_VALUE.search(name):
            fvey_country = identify_fvey_country(name) or "US"
            fvey_assets.append({
                "norad_id": norad_id,
                "name": name,
                "country": fvey_country,
                "category": classify_fvey_satellite(name),
                "inclination": round(inc, 2),
                "raan": round(raan, 2),
                "alt_km": round(alt, 1),
                "period_min": round(period, 1),
                "regime": regime,
            })
        else:
            adv_country = identify_country(name)
            if adv_country is not None:
                adversary_assets.append({
                    "norad_id": norad_id,
                    "name": name,
                    "country": adv_country,
                    "category": classify_satellite(name, adv_country),
                    "inclination": round(inc, 2),
                    "raan": round(raan, 2),
                    "alt_km": round(alt, 1),
                    "period_min": round(period, 1),
                    "regime": regime,
                })

    # Phase 2: Compare orbital parameters pairwise
    risks: List[dict] = []

    for fvey in fvey_assets:
        for adv in adversary_assets:
            # Quick regime pre-filter — skip if in different orbital regimes
            if fvey["regime"] != adv["regime"]:
                continue

            inc_diff = abs(fvey["inclination"] - adv["inclination"])
            raan_diff = _raan_difference(fvey["raan"], adv["raan"])
            alt_diff = abs(fvey["alt_km"] - adv["alt_km"])

            # Skip if clearly not a match
            regime = fvey["regime"]
            if regime == "LEO" and (inc_diff > 5 or alt_diff > 500):
                continue
            if regime == "GEO" and alt_diff > 1000:
                continue
            if regime == "MEO" and (inc_diff > 5 or alt_diff > 1000):
                continue

            threat_level, rationale = _rpo_threat_level(
                inc_diff, alt_diff, raan_diff, adv["category"],
            )

            if threat_level in ("CRITICAL", "HIGH", "ELEVATED", "MODERATE"):
                risks.append({
                    "fvey_asset": fvey,
                    "adversary_sat": adv,
                    "orbital_comparison": {
                        "inclination_diff_deg": round(inc_diff, 2),
                        "raan_diff_deg": round(raan_diff, 2),
                        "altitude_diff_km": round(alt_diff, 1),
                        "same_regime": True,
                    },
                    "threat_level": threat_level,
                    "rationale": rationale,
                })

    # Sort by threat level (CRITICAL first)
    threat_order = {"CRITICAL": 0, "HIGH": 1, "ELEVATED": 2, "MODERATE": 3}
    risks.sort(key=lambda r: (threat_order.get(r["threat_level"], 99), r["orbital_comparison"]["altitude_diff_km"]))

    # Summary
    by_level = {}
    for r in risks:
        lv = r["threat_level"]
        by_level[lv] = by_level.get(lv, 0) + 1

    by_adversary = {}
    for r in risks:
        c = r["adversary_sat"]["country"]
        by_adversary[c] = by_adversary.get(c, 0) + 1

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "RPO Risk Assessment — Orbital Geometry Analysis",
        "generated_utc": now.isoformat(),
        "methodology": (
            "Compares Keplerian orbital elements (inclination, RAAN, altitude) "
            "between adversary and FVEY military satellites. Flags pairs where "
            "orbital geometry permits rendezvous and proximity operations. "
            "Based on open-source GP elements from CelesTrak."
        ),
        "fvey_assets_analyzed": len(fvey_assets),
        "adversary_sats_analyzed": len(adversary_assets),
        "total_rpo_risks": len(risks),
        "risks_by_threat_level": by_level,
        "risks_by_adversary_nation": by_adversary,
        "rpo_risks": risks[:100],  # Cap at 100 most significant
    }

    return _store("rpo_risks", result)


# =========================================================================
# 2. DEBRIS CASCADE RISK CALCULATOR
# =========================================================================
#
# Models debris generation from a hypothetical ASAT test or collision at
# a given altitude. Uses simplified NASA Standard Breakup Model (SBM)
# estimates from Johnson et al. (2001) and Liou (2006).
#
# Key model parameters:
# - Number of fragments > 10 cm: N = 0.1 * M^0.75 (catastrophic collision)
# - For DA-ASAT: N = 0.1 * M_target^0.75 (kinetic impactor fragments)
# - Fragment distribution across altitude bands follows a Gaussian spread
#   centered on the intercept altitude
# - Orbital lifetime depends on altitude (atmospheric drag at LEO)
#
# FVEY risk assessment: which constellations operate in affected altitude
# bands and how their collision probability increases.
#
# References:
# - NASA Standard Breakup Model (Johnson et al., 2001)
# - Liou, "Risks in Space from Orbiting Debris", Science 311, 2006
# - ESA MASTER debris environment model
# - Fengyun-1C (2007) and Cosmos 2251 (2009) breakup data
# - India ASAT (2019) low-altitude test as best-practice example
# =========================================================================

# Altitude bands where FVEY constellations operate
_FVEY_ASSETS_BY_ALTITUDE = {
    "LEO_low": {
        "alt_range_km": (200, 600),
        "label": "Low LEO (200–600 km)",
        "fvey_assets": [
            {"name": "ISS", "alt_km": 420, "nation": "US/International"},
            {"name": "Starlink (Gen 1)", "alt_km": 550, "nation": "US", "count": 4500},
            {"name": "OneWeb", "alt_km": 600, "nation": "UK", "count": 600},
        ],
    },
    "LEO_mid": {
        "alt_range_km": (600, 1000),
        "label": "Mid LEO (600–1000 km)",
        "fvey_assets": [
            {"name": "Iridium NEXT", "alt_km": 780, "nation": "US", "count": 66},
            {"name": "Planet Dove", "alt_km": 500, "nation": "US", "count": 200},
            {"name": "WorldView Legion", "alt_km": 600, "nation": "US", "count": 6},
        ],
    },
    "LEO_high": {
        "alt_range_km": (1000, 2000),
        "label": "High LEO / SSO (1000–2000 km)",
        "fvey_assets": [
            {"name": "Starlink (Gen 2 shell)", "alt_km": 1150, "nation": "US", "count": 7500},
            {"name": "NROL classified", "alt_km": 1100, "nation": "US"},
        ],
    },
    "MEO": {
        "alt_range_km": (2000, 35000),
        "label": "MEO (2,000–35,000 km)",
        "fvey_assets": [
            {"name": "GPS III", "alt_km": 20200, "nation": "US", "count": 31},
            {"name": "Galileo", "alt_km": 23222, "nation": "EU/Allied", "count": 28},
        ],
    },
    "GEO": {
        "alt_range_km": (35000, 36500),
        "label": "GEO (35,786 km)",
        "fvey_assets": [
            {"name": "SBIRS GEO", "alt_km": 35786, "nation": "US", "count": 6},
            {"name": "WGS", "alt_km": 35786, "nation": "US", "count": 10},
            {"name": "AEHF/EPS", "alt_km": 35786, "nation": "US", "count": 6},
            {"name": "MUOS", "alt_km": 35786, "nation": "US", "count": 5},
            {"name": "Skynet 5/6", "alt_km": 35786, "nation": "UK", "count": 5},
            {"name": "Optus Defence", "alt_km": 35786, "nation": "AU", "count": 2},
        ],
    },
}

# Historical ASAT events for calibration
_ASAT_HISTORICAL = [
    {
        "event": "PRC FY-1C DA-ASAT",
        "year": 2007,
        "altitude_km": 865,
        "target_mass_kg": 750,
        "tracked_fragments": 3438,
        "fragments_10cm_plus": 3438,
        "orbital_lifetime_years": "decades to centuries",
        "note": "Worst debris event in history. Still 80%+ on orbit.",
    },
    {
        "event": "US ASM-135 Solwind P78-1",
        "year": 1985,
        "altitude_km": 525,
        "target_mass_kg": 850,
        "tracked_fragments": 285,
        "fragments_10cm_plus": 285,
        "orbital_lifetime_years": "17 (all decayed by 2008)",
        "note": "Low-altitude intercept — debris decayed rapidly.",
    },
    {
        "event": "India Mission Shakti (Microsat-R)",
        "year": 2019,
        "altitude_km": 283,
        "target_mass_kg": 740,
        "tracked_fragments": 125,
        "fragments_10cm_plus": 125,
        "orbital_lifetime_years": "<1",
        "note": "Low altitude chosen specifically to minimize debris.",
    },
    {
        "event": "Russia Cosmos 1408 DA-ASAT",
        "year": 2021,
        "altitude_km": 480,
        "target_mass_kg": 2200,
        "tracked_fragments": 1632,
        "fragments_10cm_plus": 1632,
        "orbital_lifetime_years": "5-10",
        "note": "Forced ISS crew to shelter. Orbit near ISS.",
    },
    {
        "event": "Cosmos 2251 / Iridium 33 collision",
        "year": 2009,
        "altitude_km": 790,
        "target_mass_kg": 1000,
        "tracked_fragments": 2296,
        "fragments_10cm_plus": 2296,
        "orbital_lifetime_years": "decades",
        "note": "First accidental hypervelocity collision.",
    },
]


def _estimate_debris_fragments(mass_kg: float, is_catastrophic: bool = True) -> dict:
    """Estimate debris fragments using calibrated NASA Standard Breakup Model.

    Calibrated against known ASAT events:
      FY-1C (750 kg) -> 3438 tracked fragments  => k ~ 25.8
      Cosmos 1408 (2200 kg) -> 1632 fragments    => k ~ 5.1
      Cosmos 2251 (~1000 kg) -> 2296 fragments   => k ~ 12.9

    We use k = 15 as an empirically-calibrated coefficient:
      N(> 10 cm) = 15 * M^0.75  (trackable fragments)
      N(> 1 cm) ~ 8 * N(> 10 cm) (lethal non-trackable)
      N(> 1 mm) ~ 60 * N(> 10 cm) (total debris cloud)

    For non-catastrophic (low energy) events, fragment count ~N/10.
    """
    if mass_kg <= 0:
        return {"gt_10cm": 0, "gt_1cm": 0, "gt_1mm": 0}

    factor = 1.0 if is_catastrophic else 0.1
    n_10cm = int(factor * 15 * (mass_kg ** 0.75))
    n_1cm = n_10cm * 8
    n_1mm = n_10cm * 60

    return {
        "gt_10cm": n_10cm,
        "gt_1cm": n_1cm,
        "gt_1mm": n_1mm,
    }


def _debris_orbital_lifetime_years(altitude_km: float) -> str:
    """Estimate orbital lifetime of debris at a given altitude.

    Based on atmospheric drag models:
    - < 300 km: days to weeks
    - 300-400 km: months to 1 year
    - 400-600 km: 1-5 years
    - 600-800 km: 5-25 years
    - 800-1000 km: 25-100 years
    - > 1000 km: centuries (effectively permanent)
    """
    if altitude_km < 200:
        return "days"
    if altitude_km < 300:
        return "weeks to months"
    if altitude_km < 400:
        return "months to 1 year"
    if altitude_km < 600:
        return "1-5 years"
    if altitude_km < 800:
        return "5-25 years"
    if altitude_km < 1000:
        return "25-100 years"
    return "centuries (effectively permanent)"


def _debris_altitude_spread(center_alt_km: float) -> List[dict]:
    """Model the altitude distribution of debris fragments.

    After a collision/intercept, fragments spread above and below the event
    altitude. The spread depends on delta-v imparted by the collision.
    Typical DA-ASAT delta-v spread: +/- 200-300 km at LEO.
    """
    spread_km = 250  # typical spread for DA-ASAT
    bands = []

    # Gaussian-ish distribution across altitude bands
    for offset in range(-300, 350, 50):
        band_alt = center_alt_km + offset
        if band_alt < 150:
            continue  # below viable orbit
        # Gaussian weighting
        fraction = math.exp(-0.5 * (offset / spread_km) ** 2)
        bands.append({
            "altitude_km": round(band_alt),
            "relative_density": round(fraction, 3),
        })

    return bands


def calculate_debris_cascade(altitude_km: float, mass_kg: float) -> dict:
    """Model debris generation from a hypothetical ASAT event.

    Args:
        altitude_km: Intercept altitude in km
        mass_kg: Target satellite mass in kg

    Returns:
        Comprehensive debris assessment including fragment counts,
        altitude distribution, affected FVEY assets, and historical
        comparison.
    """
    if altitude_km < 150 or altitude_km > 50000:
        return {
            "error": "Altitude must be between 150 and 50,000 km",
            "altitude_km": altitude_km,
        }
    if mass_kg < 1 or mass_kg > 100000:
        return {
            "error": "Mass must be between 1 and 100,000 kg",
            "mass_kg": mass_kg,
        }

    now = datetime.now(timezone.utc)
    fragments = _estimate_debris_fragments(mass_kg, is_catastrophic=True)
    lifetime = _debris_orbital_lifetime_years(altitude_km)
    spread = _debris_altitude_spread(altitude_km)

    # Assess which FVEY assets are in the affected altitude bands
    affected_bands = []
    for band_key, band_info in _FVEY_ASSETS_BY_ALTITUDE.items():
        low, high = band_info["alt_range_km"]
        # Check if debris spread overlaps with this band
        debris_low = altitude_km - 300
        debris_high = altitude_km + 300

        if debris_high >= low and debris_low <= high:
            # Calculate overlap severity
            overlap_center = (max(low, debris_low) + min(high, debris_high)) / 2
            dist_from_event = abs(overlap_center - altitude_km)
            severity_factor = math.exp(-0.5 * (dist_from_event / 250) ** 2)

            # Base collision probability increase per year per satellite
            # Very rough estimate: P_increase ~ N_fragments * cross_section / shell_volume
            shell_volume_km3 = 4 * math.pi * ((_R_EARTH_KM + altitude_km) ** 2) * 600
            cross_section_km2 = 10e-6  # 10 m^2 satellite
            p_increase_per_year = (
                fragments["gt_10cm"] * cross_section_km2 * 365.25 * 86400 * 7.5
                / shell_volume_km3
            ) * severity_factor

            affected_assets = []
            for asset in band_info["fvey_assets"]:
                asset_risk = {
                    **asset,
                    "altitude_distance_from_event_km": round(abs(asset["alt_km"] - altitude_km)),
                    "estimated_collision_probability_increase": f"{p_increase_per_year:.2e}/year",
                }
                affected_assets.append(asset_risk)

            affected_bands.append({
                "band": band_info["label"],
                "overlap_severity": round(severity_factor, 3),
                "affected_fvey_assets": affected_assets,
            })

    # Kessler syndrome risk assessment
    kessler_risk = "LOW"
    kessler_note = "Event unlikely to trigger runaway cascade"
    if altitude_km > 700 and fragments["gt_10cm"] > 1000:
        kessler_risk = "HIGH"
        kessler_note = (
            "Altitude above 700 km with 1000+ trackable fragments — "
            "significant contribution to Kessler cascade risk. Debris "
            "will persist for decades. Similar to FY-1C event."
        )
    elif altitude_km > 700 and fragments["gt_10cm"] > 300:
        kessler_risk = "ELEVATED"
        kessler_note = (
            "Moderate fragment count at altitude where debris persists. "
            "Will increase background collision rate for decades."
        )
    elif altitude_km > 500 and fragments["gt_10cm"] > 500:
        kessler_risk = "MODERATE"
        kessler_note = (
            "Significant debris but at altitude where atmospheric drag "
            "provides partial self-cleaning over 5-25 years."
        )

    # Find closest historical comparison
    closest_historical = None
    min_diff = 99999
    for hist in _ASAT_HISTORICAL:
        diff = abs(hist["altitude_km"] - altitude_km) + abs(hist["target_mass_kg"] - mass_kg) * 0.1
        if diff < min_diff:
            min_diff = diff
            closest_historical = hist

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Debris Cascade Risk Assessment",
        "generated_utc": now.isoformat(),
        "scenario": {
            "intercept_altitude_km": altitude_km,
            "target_mass_kg": mass_kg,
            "event_type": "Kinetic DA-ASAT intercept",
        },
        "debris_generation": {
            "trackable_fragments_gt_10cm": fragments["gt_10cm"],
            "lethal_fragments_gt_1cm": fragments["gt_1cm"],
            "total_fragments_gt_1mm": fragments["gt_1mm"],
            "estimated_orbital_lifetime": lifetime,
            "model": "Simplified NASA Standard Breakup Model (Johnson et al., 2001)",
        },
        "altitude_distribution": spread,
        "fvey_impact_assessment": affected_bands,
        "kessler_cascade_risk": {
            "risk_level": kessler_risk,
            "assessment": kessler_note,
        },
        "historical_comparison": closest_historical,
        "historical_asat_events": _ASAT_HISTORICAL,
        "recommendations": _debris_recommendations(altitude_km, fragments["gt_10cm"], kessler_risk),
    }

    return result


def _debris_recommendations(altitude_km: float, trackable_fragments: int, kessler_risk: str) -> List[str]:
    """Generate operational recommendations based on debris assessment."""
    recs = []

    if trackable_fragments > 100:
        recs.append(
            f"IMMEDIATE: Update conjunction screening for all FVEY assets "
            f"in {altitude_km-300:.0f}–{altitude_km+300:.0f} km altitude band."
        )

    if altitude_km > 400 and altitude_km < 600:
        recs.append(
            "ISS/CSS THREAT: Debris field intersects crewed spaceflight "
            "altitude. Initiate enhanced tracking and debris avoidance planning."
        )

    if kessler_risk in ("HIGH", "ELEVATED"):
        recs.append(
            "LONG-TERM: Assess impact on future constellation deployment "
            "plans. Consider orbit raise/lower for assets in affected bands."
        )

    recs.append(
        "DIPLOMATIC: Coordinate FVEY response per UN COPUOS Space Debris "
        "Mitigation Guidelines and UNGA Resolution 77/252 on ASAT testing."
    )

    if trackable_fragments > 500:
        recs.append(
            "SPACE FENCE: Task Space Fence and allied SSA sensors for "
            "initial debris cataloging. Expect 48-72 hours for preliminary "
            "catalog of trackable objects."
        )

    return recs


# =========================================================================
# 3. SPACE WEATHER OPERATIONAL IMPACT
# =========================================================================
#
# Translates NOAA SWPC real-time data into specific military operational
# impacts. Modeled after USSF 2nd Weather Squadron (2 WS) products and
# the 557th Weather Wing space weather bulletins.
#
# Impact mapping based on:
# - NOAA Space Weather Scales (R/S/G)
# - Kp index -> geomagnetic effects
# - Bz component -> magnetosphere coupling
# - Solar proton events -> radiation effects
#
# FVEY capability mapping:
# - GPS precision -> PNT-dependent operations
# - HF propagation -> communications
# - Satellite drag -> orbit prediction accuracy
# - Radiation environment -> satellite health, EVA
# - Geomagnetic effects -> over-the-horizon radar
#
# References:
# - NOAA Space Weather Scales (R1-R5, S1-S5, G1-G5)
# - AFWA/557 WW Space Environment Technical Note
# - GPS.gov solar storm impact documentation
# - Knipp, D.J., "Understanding Space Weather and the Physics Behind It"
# =========================================================================

# Impact rules: condition -> FVEY operational impact
_IMPACT_RULES = [
    {
        "condition": "kp_ge_5",
        "threshold_check": lambda w: (w.get("kp_current") or 0) >= 5,
        "severity": "WARNING",
        "domain": "Geomagnetic",
        "headline": "Geomagnetic Storm — Kp >= 5",
        "impacts": [
            "LEO satellite drag increased 50-200% — orbit prediction accuracy degraded",
            "GPS single-frequency error increased to 10-30m (normally 1-3m)",
            "HF propagation disrupted at high latitudes (>60 degrees)",
            "Over-the-horizon radar (JORN, ROTHR) may experience false returns",
            "Geomagnetically induced currents may affect ground infrastructure",
        ],
        "fvey_systems_affected": [
            "GPS-dependent PNT operations",
            "LEO ISR satellite orbit predictions (Starlink, WorldView, etc.)",
            "JORN (Australia) over-the-horizon radar",
            "HF communications at polar routes",
        ],
        "recommended_actions": [
            "Switch to dual-frequency GPS receivers where available",
            "Increase orbit determination cadence for LEO assets",
            "Alert JORN/ROTHR operators to expect increased clutter",
            "Prepare SATCOM backup for HF-dependent units in polar regions",
        ],
    },
    {
        "condition": "kp_ge_7",
        "threshold_check": lambda w: (w.get("kp_current") or 0) >= 7,
        "severity": "CRITICAL",
        "domain": "Geomagnetic",
        "headline": "Severe Geomagnetic Storm — Kp >= 7",
        "impacts": [
            "LEO satellite drag increased 300-500% — some objects temporarily lost from tracking",
            "GPS errors may exceed 50m — precision munitions accuracy degraded",
            "Widespread HF blackout at high and mid latitudes",
            "Potential satellite surface charging — risk of phantom commands",
            "Power grid vulnerabilities — ground C2 infrastructure at risk",
        ],
        "fvey_systems_affected": [
            "ALL GPS-dependent weapons systems",
            "LEO satellite constellation operations",
            "Strategic HF communications",
            "Early warning radar systems",
            "Ground-based C2 power systems",
        ],
        "recommended_actions": [
            "Activate backup INS/celestial navigation for PNT-critical ops",
            "Implement emergency orbit determination for all LEO military assets",
            "Switch all comms to SATCOM/fiber — HF unreliable",
            "Alert space operations centers for potential satellite anomalies",
        ],
    },
    {
        "condition": "bz_strongly_negative",
        "threshold_check": lambda w: (w.get("bz") or 0) < -10,
        "severity": "WARNING",
        "domain": "IMF/Solar Wind",
        "headline": "Strong Southward IMF (Bz < -10 nT)",
        "impacts": [
            "Enhanced magnetosphere-solar wind coupling — energy input to magnetosphere",
            "Substorm activity likely — increased auroral electrojet",
            "HF communications disrupted at high latitudes",
            "Increased radiation belt electron flux within 24-48 hours",
        ],
        "fvey_systems_affected": [
            "HF communications at latitudes >55 degrees",
            "Polar satellite ground station links (Svalbard, McMurdo)",
            "MEO satellites (GPS, Galileo) — elevated radiation",
        ],
        "recommended_actions": [
            "Monitor for Kp escalation — southward Bz is a precursor",
            "Pre-position SATCOM backup for HF-dependent units",
            "Alert satellite operators to monitor MEO radiation levels",
        ],
    },
    {
        "condition": "solar_radiation_storm",
        "threshold_check": lambda w: _get_scale_value(w, "S") >= 2,
        "severity": "WARNING",
        "domain": "Solar Radiation",
        "headline": f"Solar Radiation Storm (S2+)",
        "impacts": [
            "LEO satellite single-event upsets (SEU) likely — bit flips in electronics",
            "Elevated radiation dose for crew on ISS/CSS — EVA prohibited",
            "Polar route radiation exposure increased for high-altitude aircraft",
            "GPS signal scintillation at high latitudes",
        ],
        "fvey_systems_affected": [
            "LEO military satellites — potential anomalies from SEUs",
            "ISS/crewed spaceflight operations",
            "Polar military aviation routes",
            "GPS operations at high latitudes",
        ],
        "recommended_actions": [
            "Implement enhanced monitoring for satellite anomalies",
            "Cancel or postpone non-essential LEO satellite maneuvers",
            "Route military aviation below FL250 on polar routes",
            "Expect degraded GPS at high latitudes",
        ],
    },
    {
        "condition": "radio_blackout",
        "threshold_check": lambda w: _get_scale_value(w, "R") >= 2,
        "severity": "WARNING",
        "domain": "Radio Blackout",
        "headline": "Radio Blackout (R2+)",
        "impacts": [
            "HF radio blackout on sunlit side of Earth — 10-60 minutes",
            "Military HF communications disrupted globally (dayside)",
            "Low-frequency navigation signals degraded",
            "GPS L1 signal may experience brief scintillation",
        ],
        "fvey_systems_affected": [
            "Global HF military communications",
            "Maritime HF-dependent operations",
            "Aviation HF communications",
            "SIGINT collection on HF bands",
        ],
        "recommended_actions": [
            "Switch to SATCOM for all critical communications",
            "Alert SIGINT operators — HF collection will be degraded",
            "Monitor for follow-on CME that could cause geomagnetic storm",
        ],
    },
    {
        "condition": "extreme_solar_wind",
        "threshold_check": lambda w: (w.get("solar_wind_speed") or 0) > 700,
        "severity": "ALERT",
        "domain": "Solar Wind",
        "headline": "High-Speed Solar Wind (>700 km/s)",
        "impacts": [
            "Elevated geomagnetic activity expected within hours",
            "LEO satellite drag noticeably increased",
            "Possible recurrent geomagnetic storm if from coronal hole",
        ],
        "fvey_systems_affected": [
            "LEO satellite orbit prediction",
            "HF communications at high latitudes",
        ],
        "recommended_actions": [
            "Monitor Kp index for escalation",
            "Increase orbit determination frequency for critical LEO assets",
        ],
    },
    {
        "condition": "g_scale_storm",
        "threshold_check": lambda w: _get_scale_value(w, "G") >= 1,
        "severity": "WARNING",
        "domain": "Geomagnetic (NOAA G-Scale)",
        "headline": "Geomagnetic Storm per NOAA G-Scale",
        "impacts": [
            "Power grid fluctuations possible",
            "Minor impacts on satellite operations",
            "Aurora visible at high latitudes — indicates energy input",
        ],
        "fvey_systems_affected": [
            "Ground infrastructure power systems",
            "LEO satellite operations",
        ],
        "recommended_actions": [
            "Monitor for escalation to G2+ (moderate/strong storm)",
            "Review LEO satellite maneuver schedule",
        ],
    },
]


def _get_scale_value(weather: dict, scale_key: str) -> int:
    """Extract NOAA scale value (R/S/G) from weather data."""
    scales = weather.get("scales", {})
    scale_data = scales.get(scale_key, {})
    if isinstance(scale_data, dict):
        val = scale_data.get("Scale", 0)
        try:
            return int(val)
        except (ValueError, TypeError):
            return 0
    return 0


async def assess_space_weather_impact(client: httpx.AsyncClient) -> dict:
    """Translate current space weather into military operational impacts.

    Fetches real-time data from NOAA SWPC and maps conditions to specific
    FVEY capability impacts using operational rules.
    """
    cached = _cached("weather_impact")
    if cached is not None:
        return cached

    weather = await fetch_weather_composite(client)
    now = datetime.now(timezone.utc)

    # Evaluate all impact rules
    active_impacts: List[dict] = []
    all_clear = True

    for rule in _IMPACT_RULES:
        try:
            if rule["threshold_check"](weather):
                all_clear = False
                active_impacts.append({
                    "condition": rule["condition"],
                    "severity": rule["severity"],
                    "domain": rule["domain"],
                    "headline": rule["headline"],
                    "impacts": rule["impacts"],
                    "fvey_systems_affected": rule["fvey_systems_affected"],
                    "recommended_actions": rule["recommended_actions"],
                })
        except (TypeError, KeyError):
            continue

    # Overall assessment
    if not active_impacts:
        overall_status = "GREEN — No significant space weather impacts"
        overall_severity = "NOMINAL"
    elif any(i["severity"] == "CRITICAL" for i in active_impacts):
        overall_status = "RED — Severe space weather conditions affecting operations"
        overall_severity = "CRITICAL"
    elif any(i["severity"] == "WARNING" for i in active_impacts):
        overall_status = "AMBER — Active space weather impacts on FVEY capabilities"
        overall_severity = "WARNING"
    else:
        overall_status = "YELLOW — Elevated space weather activity, monitoring"
        overall_severity = "ALERT"

    # Compile affected FVEY systems across all active impacts
    all_affected_systems = set()
    all_actions = []
    for impact in active_impacts:
        all_affected_systems.update(impact["fvey_systems_affected"])
        all_actions.extend(impact["recommended_actions"])

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Space Weather Operational Impact Assessment",
        "generated_utc": now.isoformat(),
        "overall_status": overall_status,
        "overall_severity": overall_severity,
        "current_conditions": {
            "kp_index": weather.get("kp_current"),
            "solar_wind_speed_kms": weather.get("solar_wind_speed"),
            "imf_bt_nT": weather.get("bt"),
            "imf_bz_nT": weather.get("bz"),
            "solar_flux_sfu": weather.get("sfi"),
            "noaa_r_scale": _get_scale_value(weather, "R"),
            "noaa_s_scale": _get_scale_value(weather, "S"),
            "noaa_g_scale": _get_scale_value(weather, "G"),
        },
        "active_impacts": active_impacts,
        "total_active_impacts": len(active_impacts),
        "all_affected_fvey_systems": sorted(all_affected_systems),
        "consolidated_actions": list(dict.fromkeys(all_actions)),  # deduplicate preserving order
        "reference": {
            "noaa_scales": "https://www.swpc.noaa.gov/noaa-scales-explanation",
            "methodology": (
                "Impact rules based on NOAA Space Weather Scales, USSF 2nd Weather "
                "Squadron operational thresholds, and GPS.gov storm impact data."
            ),
        },
    }

    return _store("weather_impact", result)


# =========================================================================
# 4. LAUNCH WINDOW PREDICTOR
# =========================================================================
#
# For known adversary launch sites, calculate the next favorable launch
# windows for various target orbits. Launch azimuth and achievable
# inclinations are constrained by site latitude and range safety.
#
# Key physics:
# - Minimum inclination = site latitude (you can't launch to an orbit
#   with lower inclination than your site latitude without dog-leg)
# - SSO requires specific RAAN rate -> specific inclination for altitude
# - GEO transfer requires equatorial insertion
#
# References:
# - "Space Mission Analysis and Design" (SMAD), Wertz & Larson
# - NRO launch azimuth constraints documentation
# - Public data on adversary launch site coordinates
# =========================================================================

_ADVERSARY_LAUNCH_SITES = [
    {
        "name": "Jiuquan Satellite Launch Center (JSLC)",
        "country": "PRC",
        "lat": 40.96,
        "lng": 100.28,
        "azimuth_range_deg": (135, 170),
        "typical_targets": ["LEO", "SSO"],
        "vehicles": ["Long March 2C/D", "Kuaizhou-1A", "Long March 4B"],
        "notes": "Primary PRC LEO/SSO launch site (inland, desert).",
    },
    {
        "name": "Taiyuan Satellite Launch Center (TSLC)",
        "country": "PRC",
        "lat": 38.85,
        "lng": 111.60,
        "azimuth_range_deg": (170, 210),
        "typical_targets": ["SSO", "LEO"],
        "vehicles": ["Long March 4B/C", "Long March 6"],
        "notes": "PRC SSO workhorse. Launches south over unpopulated terrain.",
    },
    {
        "name": "Xichang Satellite Launch Center (XSLC)",
        "country": "PRC",
        "lat": 28.25,
        "lng": 102.03,
        "azimuth_range_deg": (97, 175),
        "typical_targets": ["GTO", "GEO", "MEO", "Lunar"],
        "vehicles": ["Long March 3B/E", "Long March 2C"],
        "notes": "PRC primary GEO launch site. Also BeiDou MEO.",
    },
    {
        "name": "Wenchang Space Launch Site",
        "country": "PRC",
        "lat": 19.61,
        "lng": 110.95,
        "azimuth_range_deg": (90, 175),
        "typical_targets": ["GTO", "GEO", "LEO heavy", "Lunar", "Deep space"],
        "vehicles": ["Long March 5", "Long March 7", "Long March 8"],
        "notes": "PRC newest/largest. Coastal — supports heaviest payloads.",
    },
    {
        "name": "Plesetsk Cosmodrome",
        "country": "CIS",
        "lat": 62.93,
        "lng": 40.58,
        "azimuth_range_deg": (0, 110),
        "typical_targets": ["SSO", "LEO", "Molniya", "HEO"],
        "vehicles": ["Soyuz-2.1a/b/v", "Angara-A5", "Rokot"],
        "notes": "Russia primary military launch site. High latitude enables SSO directly.",
    },
    {
        "name": "Baikonur Cosmodrome",
        "country": "CIS",
        "lat": 45.62,
        "lng": 63.36,
        "azimuth_range_deg": (49, 99),
        "typical_targets": ["ISS/LEO", "GTO", "GEO", "Interplanetary"],
        "vehicles": ["Soyuz-2", "Proton-M", "Zenit (retired)"],
        "notes": "Russia/Kazakhstan primary GEO and crewed launch site.",
    },
    {
        "name": "Vostochny Cosmodrome",
        "country": "CIS",
        "lat": 51.88,
        "lng": 128.33,
        "azimuth_range_deg": (60, 110),
        "typical_targets": ["LEO", "SSO", "GTO"],
        "vehicles": ["Soyuz-2.1a/b", "Angara-A5 (future)"],
        "notes": "Russia's new civilian launch site, under expansion.",
    },
    {
        "name": "Sohae Satellite Launching Station",
        "country": "DPRK",
        "lat": 39.66,
        "lng": 124.71,
        "azimuth_range_deg": (170, 195),
        "typical_targets": ["SSO", "LEO"],
        "vehicles": ["Unha-3", "Chollima-1"],
        "notes": "DPRK west coast site. Launches south over Yellow Sea.",
    },
    {
        "name": "Tonghae Satellite Launching Ground",
        "country": "DPRK",
        "lat": 40.85,
        "lng": 129.67,
        "azimuth_range_deg": (80, 140),
        "typical_targets": ["LEO", "Ballistic test"],
        "vehicles": ["Unha variants"],
        "notes": "DPRK east coast site. Also used for ballistic missile tests.",
    },
    {
        "name": "Imam Khomeini Spaceport (Semnan)",
        "country": "IRAN",
        "lat": 35.23,
        "lng": 53.92,
        "azimuth_range_deg": (55, 115),
        "typical_targets": ["LEO"],
        "vehicles": ["Simorgh", "Qased", "Zuljanah"],
        "notes": "Iran's primary launch site. Limited to LEO payloads.",
    },
    {
        "name": "Chabahar (proposed)",
        "country": "IRAN",
        "lat": 25.29,
        "lng": 60.62,
        "azimuth_range_deg": (90, 170),
        "typical_targets": ["LEO", "SSO"],
        "vehicles": ["Future SLVs"],
        "notes": "Proposed southern Iranian launch site — would enable lower inclinations.",
    },
]


def _min_inclination_from_latitude(lat_deg: float) -> float:
    """Minimum orbital inclination achievable from a launch site.

    Physics: You cannot launch into an orbit with inclination less than
    the launch site latitude without a costly plane-change maneuver.
    """
    return abs(lat_deg)


def _sso_inclination(altitude_km: float) -> float:
    """Required inclination for a Sun-Synchronous Orbit at given altitude.

    SSO requires a specific J2-induced RAAN precession rate of ~0.9856 deg/day
    to match the Earth's revolution around the Sun.

    Approximate formula (valid for circular orbits):
    cos(i) = -a^(7/2) * n_sun / (1.5 * R_E^2 * J2 * sqrt(mu))
    """
    J2 = 1.08263e-3
    R_E = 6378.137  # km
    n_sun = 1.991e-7  # rad/s (360 deg / 365.25 days)

    a = R_E + altitude_km
    n_orbit = math.sqrt(_MU_EARTH / a ** 3)  # rad/s

    cos_i = -(2 * a ** 2 * n_sun) / (3 * R_E ** 2 * J2 * n_orbit)

    if abs(cos_i) > 1:
        return 98.0  # default SSO inclination
    return math.degrees(math.acos(cos_i))


def predict_launch_windows(
    site_lat: float,
    site_lng: float,
    target_orbit: str = "SSO",
) -> dict:
    """Predict launch window characteristics for a given site and target orbit.

    Returns orbital mechanics constraints, not specific times (which would
    require precise target RAAN and time of year).

    Args:
        site_lat: Launch site latitude (degrees)
        site_lng: Launch site longitude (degrees)
        target_orbit: One of SSO, LEO, GEO, MEO, Molniya
    """
    now = datetime.now(timezone.utc)
    min_inc = _min_inclination_from_latitude(site_lat)

    target_orbit = target_orbit.upper()

    # Find matching launch site
    matched_site = None
    for site in _ADVERSARY_LAUNCH_SITES:
        if abs(site["lat"] - site_lat) < 1 and abs(site["lng"] - site_lng) < 1:
            matched_site = site
            break

    # Orbital mechanics constraints
    if target_orbit == "SSO":
        target_inc = _sso_inclination(500)  # Typical 500 km SSO
        achievable = target_inc >= min_inc
        target_alt = "400-900 km"
        window_type = "Specific LTAN required — typically dawn-dusk (06:00/18:00 LST) or 10:30 LST"
        window_frequency = "Daily windows, but LTAN-constrained to ~2 per day"
        notes = (
            f"SSO requires inclination ~{target_inc:.1f} deg. "
            f"Site latitude {site_lat:.1f} deg {'allows' if achievable else 'PREVENTS'} "
            f"direct insertion (min inc = {min_inc:.1f} deg)."
        )
    elif target_orbit == "GEO":
        target_inc = 0
        achievable = True  # All sites can reach GEO via GTO, just less efficient
        target_alt = "35,786 km (via GTO)"
        penalty_dv = abs(site_lat) * 57.0  # rough delta-v penalty m/s per degree
        window_type = "2 windows per day aligned with target GEO slot longitude"
        window_frequency = "~2 windows per day for a specific GEO longitude"
        notes = (
            f"GEO accessible from latitude {site_lat:.1f} deg via GTO with "
            f"~{penalty_dv:.0f} m/s plane-change penalty. "
            f"Lower latitude sites (Wenchang, Kourou) are more efficient."
        )
    elif target_orbit == "LEO":
        target_inc = max(min_inc, 28)  # typical LEO at site latitude or ISS
        achievable = True
        target_alt = "200-600 km"
        window_type = "Continuous — LEO windows available any time"
        window_frequency = "Essentially continuous for flexible inclination"
        notes = (
            f"LEO accessible at any inclination >= {min_inc:.1f} deg. "
            f"Typical military reconnaissance orbits: {min_inc:.0f}-98 deg."
        )
    elif target_orbit in ("MEO", "NAVIGATION"):
        target_inc = 55  # GPS/BeiDou-like
        achievable = target_inc >= min_inc
        target_alt = "19,000-23,000 km"
        window_type = "Constellation-dependent — specific orbital plane insertion"
        window_frequency = "~2 windows per day per orbital plane"
        notes = (
            f"MEO navigation orbit (inc ~55 deg). "
            f"{'Achievable' if achievable else 'Requires plane change'} from "
            f"latitude {site_lat:.1f} deg."
        )
    elif target_orbit in ("MOLNIYA", "HEO"):
        target_inc = 63.4  # Frozen orbit critical inclination
        achievable = target_inc >= min_inc
        target_alt = "500-40,000 km (Molniya)"
        window_type = "2 windows per day for target argument of perigee"
        window_frequency = "~2 windows per day"
        notes = (
            f"Molniya/Tundra orbit at critical inclination 63.4 deg. "
            f"Used by Russia for Tundra EW and Meridian comms. "
            f"{'Achievable' if achievable else 'Difficult'} from {site_lat:.1f} deg."
        )
    else:
        target_inc = min_inc
        achievable = True
        target_alt = "Variable"
        window_type = "Dependent on specific orbit parameters"
        window_frequency = "Variable"
        notes = f"Custom orbit target. Minimum inclination from this site: {min_inc:.1f} deg."

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Launch Window Assessment",
        "generated_utc": now.isoformat(),
        "launch_site": {
            "latitude": site_lat,
            "longitude": site_lng,
            "name": matched_site["name"] if matched_site else "Custom / Unknown",
            "country": matched_site["country"] if matched_site else "Unknown",
            "vehicles": matched_site["vehicles"] if matched_site else [],
            "notes": matched_site["notes"] if matched_site else "",
        },
        "target_orbit": {
            "type": target_orbit,
            "altitude": target_alt,
            "target_inclination_deg": round(target_inc, 1),
        },
        "orbital_mechanics": {
            "minimum_inclination_from_site_deg": round(min_inc, 1),
            "direct_insertion_achievable": achievable,
            "window_type": window_type,
            "window_frequency": window_frequency,
        },
        "analysis": notes,
        "all_adversary_launch_sites": _ADVERSARY_LAUNCH_SITES,
    }

    return result


# =========================================================================
# 5. TREATY & NORMS TRACKER
# =========================================================================
#
# Tracks key space governance frameworks and their status. Critical for
# FVEY policy coordination and understanding the legal/normative
# environment for space operations.
#
# References:
# - UN Office for Outer Space Affairs (UNOOSA)
# - Secure World Foundation Counterspace Capabilities report
# - UNCOPUOS sessions and working papers
# - Artemis Accords signatory list (NASA)
# - FVEY joint statements on space (various summits)
# =========================================================================

def get_treaty_status() -> dict:
    """Return current status of key space governance frameworks."""
    now = datetime.now(timezone.utc)

    frameworks = [
        {
            "name": "Outer Space Treaty (OST)",
            "formal_name": "Treaty on Principles Governing the Activities of States in the Exploration and Use of Outer Space",
            "year": 1967,
            "status": "ACTIVE — in force",
            "signatories": 115,
            "ratifications": 113,
            "key_provisions": [
                "Space is free for exploration by all states",
                "No WMD in orbit or on celestial bodies",
                "No military bases on Moon or celestial bodies",
                "States liable for damage caused by space objects",
                "States responsible for national space activities (including private)",
            ],
            "limitations": [
                "Does not prohibit conventional weapons in space",
                "Does not prohibit ASAT weapons",
                "No verification/enforcement mechanism",
                "Ambiguous on 'peaceful purposes' — military use vs weaponization",
            ],
            "fvey_position": "All FVEY states are parties. Cornerstone of space law.",
            "threats_to_treaty": [
                "PRC and Russia have conducted ASAT tests (arguably not violating treaty)",
                "No mechanism to address co-orbital weapons or RPO",
                "Dual-use technology makes space weaponization hard to define",
            ],
        },
        {
            "name": "UN ASAT Testing Moratorium",
            "formal_name": "UNGA Resolution A/RES/77/41 — Destructive DA-ASAT Testing Moratorium",
            "year": 2022,
            "status": "VOLUNTARY MORATORIUM — non-binding",
            "signatories_committed": [
                "United States (Apr 2022)",
                "Canada",
                "New Zealand",
                "Japan",
                "Germany",
                "France",
                "United Kingdom",
                "Australia",
                "South Korea",
                "Switzerland",
            ],
            "nations_not_committed": [
                "China (PRC)",
                "Russia",
                "India",
                "North Korea (DPRK)",
                "Iran",
            ],
            "key_provisions": [
                "Commitment not to conduct destructive direct-ascent ASAT tests",
                "Does NOT cover co-orbital ASAT, EW, cyber, or DEW",
                "Voluntary and non-binding — no verification",
            ],
            "fvey_position": "All FVEY nations committed. US led initiative in April 2022.",
            "assessment": (
                "Important normative signal but limited scope. Does not address "
                "the most concerning counterspace threats (co-orbital, EW, cyber). "
                "PRC and Russia have NOT committed."
            ),
        },
        {
            "name": "PAROS (Prevention of Arms Race in Outer Space)",
            "formal_name": "Prevention of an Arms Race in Outer Space — CD agenda item",
            "year": 1985,
            "status": "STALLED — no progress at Conference on Disarmament",
            "key_provisions": [
                "Proposed ban on weapons in space",
                "Various draft treaties (PRC/Russia PPWT, EU Code of Conduct)",
            ],
            "obstacles": [
                "No agreed definition of 'space weapon'",
                "PRC/Russia PPWT draft rejected by US (no verification, doesn't cover ground-based ASAT)",
                "Conference on Disarmament consensus requirement blocks progress",
                "Dual-use nature of space technology",
            ],
            "fvey_position": (
                "FVEY generally supports space arms control in principle but "
                "rejects the PRC/Russia PPWT draft as unverifiable and incomplete. "
                "US and UK prefer norms-based approach over binding treaty."
            ),
            "assessment": "Effectively dead at the CD. Unlikely to progress without fundamental change.",
        },
        {
            "name": "Artemis Accords",
            "formal_name": "The Artemis Accords: Principles for Cooperation in the Civil Exploration and Use of Outer Space",
            "year": 2020,
            "status": "ACTIVE — expanding membership",
            "signatories": 43,
            "fvey_signatories": ["United States", "United Kingdom", "Canada", "Australia", "New Zealand"],
            "key_provisions": [
                "Peaceful purposes — consistent with OST",
                "Transparency in space activities",
                "Interoperability of space systems",
                "Emergency assistance",
                "Registration of space objects",
                "Release of scientific data",
                "Preservation of outer space heritage",
                "Space resource extraction rights (aligned with US interpretation of OST)",
                "Deconfliction of activities — safety zones concept",
                "Orbital debris mitigation",
            ],
            "non_signatories_of_note": ["China (PRC)", "Russia"],
            "fvey_position": "All FVEY nations are founding signatories. Key framework for allied civil space cooperation.",
            "assessment": (
                "Becoming the de facto governance framework for civil space activities. "
                "PRC and Russia are building parallel frameworks (ILRS partnership). "
                "Strategic bifurcation of space governance emerging."
            ),
        },
        {
            "name": "UN Open-Ended Working Group on Space Threats (OEWG)",
            "formal_name": "UNGA Resolution A/RES/76/231 — OEWG on Space Threats",
            "year": 2022,
            "status": "ACTIVE — multi-year process",
            "key_provisions": [
                "Develop norms, rules, and principles for responsible behavior in space",
                "Assess existing and proposed legally and non-legally binding instruments",
                "Make recommendations on possible norms",
            ],
            "fvey_position": (
                "Actively engaged. US, UK, Australia contributing working papers. "
                "Prefer norms/transparency approach over binding arms control."
            ),
            "assessment": (
                "Most promising current forum for space security governance. "
                "But PRC and Russia promoting competing PPWT framework. "
                "Outcome uncertain — likely non-binding norms at best."
            ),
        },
        {
            "name": "ITU Radio Regulations (Space Spectrum Governance)",
            "formal_name": "International Telecommunication Union Radio Regulations",
            "year": 1906,
            "status": "ACTIVE — regularly updated (WRC cycle)",
            "key_provisions": [
                "Allocation of radio frequency spectrum for space services",
                "Coordination of satellite orbits (especially GEO)",
                "Protection from harmful interference",
                "Notification and registration of space stations",
            ],
            "fvey_position": "All FVEY nations are ITU members. Critical for spectrum operations.",
            "threats": [
                "PRC filing massive constellation spectrum claims",
                "Potential for weaponization of spectrum coordination process",
                "Interference claims used for strategic advantage",
            ],
            "assessment": (
                "Essential but underappreciated framework. Spectrum coordination "
                "increasingly a strategic competition space."
            ),
        },
        {
            "name": "Space Debris Mitigation Guidelines",
            "formal_name": "UN COPUOS Space Debris Mitigation Guidelines (2007) + LTS Guidelines (2019)",
            "year": 2007,
            "status": "ACTIVE — voluntary guidelines",
            "key_provisions": [
                "25-year post-mission disposal rule",
                "Passivation of end-of-life spacecraft",
                "Minimize collision probability during operations",
                "Avoid intentional destruction generating long-lived debris",
            ],
            "compliance": {
                "FVEY": "Generally compliant — US FCC adopted 5-year rule in 2022",
                "PRC": "Partial compliance — Long March upper stages often non-compliant",
                "Russia": "Low compliance — multiple uncontrolled reentries",
            },
            "fvey_position": "Strong advocates. US leading with stricter national rules.",
            "assessment": (
                "Voluntary and non-binding. Growing pressure to make binding. "
                "ASAT testing moratorium addresses debris from one source."
            ),
        },
    ]

    # Summary statistics
    active_count = sum(1 for f in frameworks if "ACTIVE" in f["status"])
    stalled_count = sum(1 for f in frameworks if "STALLED" in f["status"])

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Space Governance & Treaty Tracker",
        "generated_utc": now.isoformat(),
        "summary": {
            "total_frameworks_tracked": len(frameworks),
            "active": active_count,
            "stalled": stalled_count,
            "key_gaps": [
                "No binding prohibition on conventional weapons in space",
                "No binding prohibition on ASAT weapons (only voluntary DA-ASAT moratorium)",
                "No verification mechanisms for any space arms control",
                "No agreed definition of 'space weapon'",
                "Co-orbital ASAT, EW, cyber, DEW — entirely unregulated",
            ],
            "fvey_strategic_posture": (
                "FVEY nations favour norms-based, transparent approach over "
                "binding arms control treaties. All FVEY committed to DA-ASAT moratorium "
                "and Artemis Accords. Engaged in OEWG process."
            ),
        },
        "frameworks": frameworks,
    }

    return result


# =========================================================================
# 6. ELECTROMAGNETIC SPECTRUM ASSESSMENT
# =========================================================================
#
# Evaluates electromagnetic spectrum threats in the space domain.
# Covers GPS jamming/spoofing, SATCOM interference, directed energy
# weapons, and electronic warfare capabilities by nation.
#
# References:
# - C4ADS "Above Us Only Stars" GPS spoofing report
# - CSIS "Space Threat Assessment" annual reports
# - SWF "Global Counterspace Capabilities" — EW chapter
# - NASIC "Competing in Space"
# - Todd Harrison, CSIS "Space-Based Electronic Warfare"
# =========================================================================

_SPECTRUM_THREATS = [
    {
        "threat_type": "GPS Jamming",
        "actors": {
            "CIS": {
                "status": "OPERATIONAL — actively deployed",
                "systems": [
                    {
                        "name": "Pole-21",
                        "type": "Ground-based GPS/GNSS jammer",
                        "range_km": 80,
                        "status": "Deployed at multiple military facilities",
                        "notes": "Integrated into Russian strategic site defense. Protects military installations.",
                    },
                    {
                        "name": "R-330Zh Zhitel",
                        "type": "Mobile GPS/GNSS jamming complex",
                        "range_km": 50,
                        "status": "Operational with ground forces",
                        "notes": "Deployed in Syria and Ukraine. Also jams SATCOM.",
                    },
                    {
                        "name": "Krasukha-2/4",
                        "type": "Mobile electronic warfare complex",
                        "range_km": 200,
                        "status": "Operational",
                        "notes": "Primarily designed against radar but has GNSS jamming mode.",
                    },
                ],
                "observed_activity": [
                    "Persistent GPS jamming in Syria/Eastern Mediterranean",
                    "GPS disruption during NATO exercises in Scandinavia",
                    "Widespread GPS/GLONASS jamming in Ukraine conflict zone",
                    "GPS spoofing around Putin's known locations",
                ],
            },
            "PRC": {
                "status": "OPERATIONAL — capability demonstrated",
                "systems": [
                    {
                        "name": "Unknown designation",
                        "type": "Ground-based and vehicle-mounted GPS jammers",
                        "range_km": 100,
                        "status": "Deployed",
                        "notes": "NASIC reports PRC has developed GPS jamming capability for military use.",
                    },
                ],
                "observed_activity": [
                    "GPS disruption reported in South China Sea during exercises",
                    "Maritime GPS spoofing near Shanghai port documented by C4ADS",
                ],
            },
            "DPRK": {
                "status": "LIMITED — demonstrated capability",
                "systems": [
                    {
                        "name": "Vehicle-mounted jammers (Soviet-origin)",
                        "type": "Ground-based GPS jammer",
                        "range_km": 50,
                        "status": "Limited deployment",
                        "notes": "Used in provocations against South Korea.",
                    },
                ],
                "observed_activity": [
                    "GPS jamming incidents along DMZ (2010-2016)",
                    "Affected South Korean aviation and maritime operations",
                ],
            },
            "IRAN": {
                "status": "LIMITED",
                "systems": [
                    {
                        "name": "Claimed indigenous jammer",
                        "type": "GPS jammer",
                        "range_km": 30,
                        "status": "Unknown operational status",
                        "notes": "Iran claims GPS jamming capability. Demonstrated during capture of US RQ-170 (2011).",
                    },
                ],
                "observed_activity": [
                    "GPS spoofing incidents in Persian Gulf region",
                    "Claimed role in RQ-170 Sentinel capture (disputed)",
                ],
            },
        },
        "fvey_impact": "GPS-dependent precision munitions, navigation, and timing all at risk",
        "countermeasures": [
            "M-code GPS (military encrypted, more jam-resistant)",
            "GPS anti-jam antennas (CRPA — Controlled Reception Pattern Antenna)",
            "Alternative PNT: INS, celestial navigation, eLoran",
            "Multi-GNSS receivers (GPS + Galileo + QZSS + allied SBAS)",
        ],
    },
    {
        "threat_type": "SATCOM Uplink Jamming",
        "actors": {
            "CIS": {
                "status": "OPERATIONAL",
                "systems": [
                    {
                        "name": "Tirada-2",
                        "type": "SATCOM uplink jammer",
                        "status": "Operational",
                        "notes": "Targets military SATCOM uplinks. Used in Syria.",
                    },
                ],
            },
            "PRC": {
                "status": "DEVELOPMENT — assessed capable",
                "systems": [
                    {
                        "name": "Unknown designations",
                        "type": "SATCOM jammers",
                        "status": "Assessed operational",
                        "notes": "DIA/NASIC assess PRC has SATCOM jamming capability targeting military UHF and SHF.",
                    },
                ],
            },
        },
        "fvey_impact": "Military SATCOM (WGS, AEHF, Skynet) could be jammed in theater",
        "countermeasures": [
            "AEHF protected comms (EHF, anti-jam waveforms)",
            "Frequency hopping and spread spectrum",
            "Increased satellite EIRP (Effective Isotropic Radiated Power)",
            "Mesh networking across multiple SATCOM constellations",
        ],
    },
    {
        "threat_type": "Directed Energy / Dazzling",
        "actors": {
            "PRC": {
                "status": "DEVELOPMENT / TESTING",
                "systems": [
                    {
                        "name": "Ground-based laser ASAT (multiple facilities)",
                        "type": "Ground-to-space directed energy",
                        "status": "Testing phase — multiple facilities identified",
                        "notes": (
                            "DIA assesses PRC is developing ground-based laser ASAT capable of "
                            "dazzling/blinding LEO satellite EO sensors by 2025 and potentially "
                            "damaging satellite structures by late 2020s."
                        ),
                    },
                ],
            },
            "CIS": {
                "status": "OPERATIONAL (dazzle) / DEVELOPMENT (damage)",
                "systems": [
                    {
                        "name": "Peresvet",
                        "type": "Ground-based laser system",
                        "status": "Deployed at ICBM bases",
                        "notes": "Deployed since 2019. Assessed as anti-satellite sensor dazzler. May have ASAT damage capability.",
                    },
                    {
                        "name": "Kalina",
                        "type": "Ground-based laser telescope/dazzler",
                        "status": "Under development at Krona complex, Caucasus",
                        "notes": "Designed to dazzle optical sensors on reconnaissance satellites.",
                    },
                ],
            },
        },
        "fvey_impact": "LEO ISR satellites (especially EO/IR) vulnerable to temporary or permanent blinding",
        "countermeasures": [
            "Satellite sensor shuttering on warning",
            "Hardened optical coatings",
            "Distributed architecture — many small sats instead of few large ones",
            "Space-based awareness of ground laser sites",
        ],
    },
    {
        "threat_type": "Space-Based RF Interception / SIGINT",
        "actors": {
            "PRC": {
                "status": "OPERATIONAL",
                "systems": [
                    {
                        "name": "Tongxin Jishu Shiyan (TJSW) series",
                        "type": "GEO SIGINT / EW satellite",
                        "status": "Multiple on orbit",
                        "notes": "PRC GEO SIGINT constellation. Monitors adversary SATCOM and other RF emissions.",
                    },
                    {
                        "name": "Shijian series (selected)",
                        "type": "LEO technology demonstration / SIGINT",
                        "status": "Multiple on orbit",
                        "notes": "Some Shijian satellites assessed to have SIGINT/ELINT payloads.",
                    },
                ],
            },
            "CIS": {
                "status": "OPERATIONAL",
                "systems": [
                    {
                        "name": "Liana (Lotos / Pion)",
                        "type": "LEO SIGINT constellation",
                        "status": "Operational — Lotos ELINT and Pion SIGINT",
                        "notes": "Russian naval SIGINT constellation for maritime targeting.",
                    },
                    {
                        "name": "Luch (Olymp) GEO SIGINT",
                        "type": "GEO relay / SIGINT",
                        "status": "Operational — known to loiter near adversary GEO assets",
                        "notes": "Luch/Olymp satellites perform RPO near FVEY GEO commsats — likely SIGINT collection.",
                    },
                ],
            },
        },
        "fvey_impact": "Adversary collection on FVEY SATCOM, radar emissions, and other RF signatures from space",
        "countermeasures": [
            "Enhanced TRANSEC (Transmission Security) on SATCOM",
            "Low Probability of Intercept/Detection (LPI/LPD) waveforms",
            "Awareness of adversary SIGINT sat positions (this platform)",
            "Emission control (EMCON) protocols",
        ],
    },
]


async def get_spectrum_assessment(client: httpx.AsyncClient) -> dict:
    """Evaluate electromagnetic spectrum threats in the space domain.

    Combines the static threat database with real-time space weather data
    to assess current EW environment conditions.
    """
    cached = _cached("spectrum_assessment")
    if cached is not None:
        return cached

    weather = await fetch_weather_composite(client)
    now = datetime.now(timezone.utc)

    # Natural spectrum environment assessment from space weather
    natural_environment = []

    kp = weather.get("kp_current") or 0
    if kp >= 5:
        natural_environment.append({
            "phenomenon": "Geomagnetic storm",
            "severity": "SIGNIFICANT" if kp >= 7 else "MODERATE",
            "impact": "Ionospheric irregularities degrading HF propagation and GPS accuracy",
            "affected_bands": ["HF (3-30 MHz)", "L-band (GPS L1/L2)", "UHF (scintillation)"],
        })

    r_scale = _get_scale_value(weather, "R")
    if r_scale >= 1:
        natural_environment.append({
            "phenomenon": "Solar radio blackout",
            "severity": f"R{r_scale}",
            "impact": "Increased solar radio noise across wide spectrum range. HF absorption.",
            "affected_bands": ["HF (3-30 MHz)", "VHF (partial, if severe)"],
        })

    s_scale = _get_scale_value(weather, "S")
    if s_scale >= 1:
        natural_environment.append({
            "phenomenon": "Solar radiation storm",
            "severity": f"S{s_scale}",
            "impact": "Polar cap absorption — HF blackout at high latitudes. SEU risk to satellite electronics.",
            "affected_bands": ["HF at polar latitudes", "Satellite electronics"],
        })

    bz = weather.get("bz") or 0
    if bz < -10:
        natural_environment.append({
            "phenomenon": "Strong southward IMF",
            "severity": "ELEVATED",
            "impact": "Ionospheric storm conditions developing. Scintillation likely.",
            "affected_bands": ["GPS L-band", "SATCOM UHF", "HF"],
        })

    # Overall spectrum readiness
    threat_count = len(natural_environment)
    if threat_count == 0:
        spectrum_status = "GREEN — Benign electromagnetic environment"
    elif any(
        n.get("severity", "").startswith(("R3", "R4", "R5", "S3", "S4", "S5", "SIGNIFICANT"))
        for n in natural_environment
    ):
        spectrum_status = "RED — Severely degraded electromagnetic environment"
    elif threat_count >= 2:
        spectrum_status = "AMBER — Multiple spectrum degradation factors active"
    else:
        spectrum_status = "YELLOW — Elevated spectrum activity"

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Electromagnetic Spectrum Operations Assessment — Space Domain",
        "generated_utc": now.isoformat(),
        "spectrum_environment_status": spectrum_status,
        "natural_environment": natural_environment,
        "adversary_ew_capabilities": _SPECTRUM_THREATS,
        "current_conditions": {
            "kp_index": kp,
            "noaa_r_scale": r_scale,
            "noaa_s_scale": s_scale,
            "imf_bz_nT": bz,
        },
        "fvey_spectrum_priorities": [
            "GPS/GNSS protection — M-code transition, anti-jam antennas",
            "Protected SATCOM — AEHF/EPS, Skynet 6",
            "Anti-jam UHF SATCOM — MUOS",
            "Low-probability-of-intercept data links",
            "Resilient PNT alternatives",
        ],
    }

    return _store("spectrum_assessment", result)
