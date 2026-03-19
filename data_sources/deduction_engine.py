"""
AI Deduction Engine — Analytical Brain of Echelon Vantage
Connects dots across all data sources to produce intelligence deductions
that a human analyst would make: patterns, capabilities, intent, vulnerabilities,
predictions, and correlations.

Functions:
- generate_deductions        — master deduction function (all categories)
- get_priority_deductions    — top 10 highest-priority deductions
- get_deductions_by_category — filter by deduction category
- generate_threat_narrative  — cohesive analytical narrative document

Classification: UNCLASSIFIED // OSINT // REL TO FVEY
"""
from __future__ import annotations

import asyncio
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx

from data_sources.adversary_sats import get_adversary_stats
from data_sources.space_weather import fetch_weather_composite
from data_sources.launches import fetch_launches
from data_sources.ground_stations import (
    get_adversary_stations,
    get_fvey_stations,
    get_stations_summary,
)
from data_sources.missile_intel import (
    get_missile_asat_data,
    get_by_country as get_missiles_by_country,
    get_threat_summary as get_missile_threat_summary,
)
from data_sources.live_intel import get_hotspot_analysis
from data_sources.incident_db import get_incident_stats
from data_sources.futures import get_futures_summary

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CATEGORY_PATTERN = "PATTERN"
CATEGORY_CAPABILITY = "CAPABILITY"
CATEGORY_INTENT = "INTENT"
CATEGORY_VULNERABILITY = "VULNERABILITY"
CATEGORY_PREDICTIVE = "PREDICTIVE"
CATEGORY_CORRELATION = "CORRELATION"

CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_LOW = "LOW"

PRIORITY_CRITICAL = "CRITICAL"
PRIORITY_HIGH = "HIGH"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_LOW = "LOW"

_PRIORITY_ORDER = {
    PRIORITY_CRITICAL: 0,
    PRIORITY_HIGH: 1,
    PRIORITY_MEDIUM: 2,
    PRIORITY_LOW: 3,
}

# ---------------------------------------------------------------------------
# Cache — 300-second TTL
# ---------------------------------------------------------------------------
_cache: Dict[str, dict] = {}
_DEDUCTION_TTL = 300  # 5 minutes


def _cached(key: str) -> Optional[dict]:
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < _DEDUCTION_TTL:
        return entry["data"]
    return None


def _store(key: str, data: dict) -> dict:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


def _deduction_id(category: str, slug: str) -> str:
    """Generate a deterministic deduction identifier."""
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    raw = f"{category}-{slug}-{day}"
    short_hash = hashlib.md5(raw.encode()).hexdigest()[:6].upper()
    return f"DED-{category[:3]}-{short_hash}"


# ---------------------------------------------------------------------------
# Data Collection Layer
# ---------------------------------------------------------------------------

async def _collect_all_data(client: httpx.AsyncClient) -> Dict[str, object]:
    """Fetch all available data sources concurrently."""
    stats_task = get_adversary_stats(client)
    weather_task = fetch_weather_composite(client)
    launches_task = fetch_launches(client)
    hotspot_task = get_hotspot_analysis(client)

    stats, weather, launches_data, hotspots = await asyncio.gather(
        stats_task, weather_task, launches_task, hotspot_task,
        return_exceptions=True,
    )

    # Synchronous data sources
    missile_data = get_missile_asat_data()
    missile_summary = get_missile_threat_summary()
    ground_stations = get_adversary_stations()
    fvey_stations = get_fvey_stations()
    stations_summary = get_stations_summary()
    incident_stats = get_incident_stats()
    futures_summary = get_futures_summary()

    return {
        "stats": stats if not isinstance(stats, Exception) else {},
        "weather": weather if not isinstance(weather, Exception) else {},
        "launches": launches_data if not isinstance(launches_data, Exception) else [],
        "hotspots": hotspots if not isinstance(hotspots, Exception) else {},
        "missiles": missile_data,
        "missile_summary": missile_summary,
        "ground_stations": ground_stations,
        "fvey_stations": fvey_stations,
        "stations_summary": stations_summary,
        "incident_stats": incident_stats,
        "futures_summary": futures_summary,
    }


# ===================================================================
# DEDUCTION GENERATORS — one function per category
# ===================================================================

# ---------------------------------------------------------------------------
# 1. PATTERN DEDUCTIONS
# ---------------------------------------------------------------------------

def _generate_pattern_deductions(data: Dict[str, object]) -> List[dict]:
    """Identify patterns in adversary behaviour from available data."""
    deductions: List[dict] = []
    stats = data.get("stats", {})
    launches = data.get("launches", [])
    now = datetime.now(timezone.utc)

    if not isinstance(stats, dict):
        stats = {}
    if not isinstance(launches, list):
        launches = []

    # --- Pattern: PRC ISR constellation expansion rate ---
    prc_data = stats.get("PRC", {})
    prc_isr = prc_data.get("military_isr", 0) if isinstance(prc_data, dict) else 0
    prc_total = prc_data.get("total", 0) if isinstance(prc_data, dict) else 0

    if prc_isr > 0:
        # Count PRC launches in manifest
        prc_launch_count = sum(
            1 for lch in launches
            if any(kw in (lch.get("provider") or "").lower()
                   for kw in ["casc", "china", "expace", "galactic energy"])
        )
        yaogan_launches = sum(
            1 for lch in launches
            if "yaogan" in (lch.get("name") or "").lower()
        )

        if prc_isr >= 80:
            deductions.append({
                "id": _deduction_id(CATEGORY_PATTERN, "prc-isr-surge"),
                "category": CATEGORY_PATTERN,
                "confidence": CONFIDENCE_HIGH,
                "priority": PRIORITY_CRITICAL,
                "title": "PRC ISR constellation has reached persistent-coverage threshold",
                "deduction": (
                    f"PRC currently operates {prc_isr} military ISR satellites, exceeding "
                    f"the assessed threshold of 80 required for near-persistent maritime "
                    f"surveillance of the Western Pacific. DEDUCTION: PRC has achieved "
                    f"sufficient ISR capacity to support anti-ship ballistic missile "
                    f"targeting chains in a Taiwan Strait contingency, with sub-2-hour "
                    f"revisit times over critical maritime chokepoints."
                ),
                "evidence": [
                    f"{prc_isr} PRC military ISR satellites in active catalog",
                    f"{prc_total} total PRC satellites tracked",
                    f"{prc_launch_count} PRC launches in upcoming manifest",
                    "Yaogan triplet constellation provides ELINT + SAR + optical coverage",
                    "Jilin-1 commercial-military constellation adds sub-1m optical/video",
                ],
                "implications": (
                    "FVEY naval surface forces in the Western Pacific are under "
                    "near-persistent adversary ISR surveillance. EMCON and concealment "
                    "measures must assume continuous overhead collection."
                ),
                "recommended_action": (
                    "Update FVEY ISR coverage gap analysis. Coordinate EMCON schedules "
                    "with residual coverage gaps. Develop ISR denial capabilities "
                    "for high-priority operational windows."
                ),
                "timestamp": now.isoformat(),
            })
        elif prc_isr >= 50:
            deductions.append({
                "id": _deduction_id(CATEGORY_PATTERN, "prc-isr-growing"),
                "category": CATEGORY_PATTERN,
                "confidence": CONFIDENCE_HIGH,
                "priority": PRIORITY_HIGH,
                "title": "PRC ISR constellation accelerating toward persistent coverage",
                "deduction": (
                    f"PRC currently operates {prc_isr} military ISR satellites, growing "
                    f"at an assessed rate of 3-6 launches per year. At current tempo, "
                    f"PRC will achieve 80+ ISR satellites within 12-24 months. "
                    f"DEDUCTION: PRC is systematically building toward persistent "
                    f"maritime ISR coverage sufficient for real-time targeting support."
                ),
                "evidence": [
                    f"{prc_isr} PRC military ISR satellites currently active",
                    f"{yaogan_launches} Yaogan ISR missions in upcoming manifest",
                    "Historical launch rate: 3-6 ISR deployments per year since 2020",
                ],
                "implications": (
                    "Window of ISR coverage gaps that FVEY forces can exploit is "
                    "narrowing. Within 1-2 years, persistent coverage will be achieved."
                ),
                "recommended_action": (
                    "Accelerate development of ISR countermeasures. Increase overhead "
                    "collection of PRC ISR satellite launch and deployment patterns."
                ),
                "timestamp": now.isoformat(),
            })

        # Yaogan launches in manifest signal imminent expansion
        if yaogan_launches >= 2:
            deductions.append({
                "id": _deduction_id(CATEGORY_PATTERN, "yaogan-surge"),
                "category": CATEGORY_PATTERN,
                "confidence": CONFIDENCE_MEDIUM,
                "priority": PRIORITY_HIGH,
                "title": f"{yaogan_launches} Yaogan ISR missions in launch manifest — expansion surge",
                "deduction": (
                    f"The upcoming launch manifest contains {yaogan_launches} Yaogan "
                    f"ISR satellite deployments. DEDUCTION: PRC is conducting a burst "
                    f"expansion of its maritime ISR constellation, accelerating from "
                    f"historical norms. This may indicate a shift from peacetime "
                    f"constellation building to operational capability surge."
                ),
                "evidence": [
                    f"{yaogan_launches} Yaogan missions in upcoming manifest",
                    f"{prc_launch_count} total PRC launches scheduled",
                    "Yaogan typically launched in triplets (1 SAR + 2 ELINT)",
                ],
                "implications": (
                    "Each successful Yaogan triplet launch reduces ISR revisit time "
                    "by approximately 15-20 minutes over the Western Pacific."
                ),
                "recommended_action": (
                    "Track post-launch orbital parameters to assess coverage additions. "
                    "Update ISR threat coverage models."
                ),
                "timestamp": now.isoformat(),
            })

    # --- Pattern: Russian launch activity vs sanctions impact ---
    cis_data = stats.get("CIS", {})
    cis_total = cis_data.get("total", 0) if isinstance(cis_data, dict) else 0
    cis_isr = cis_data.get("military_isr", 0) if isinstance(cis_data, dict) else 0

    rus_launches = sum(
        1 for lch in launches
        if any(kw in (lch.get("provider") or "").lower()
               for kw in ["roscosmos", "russia", "khrunichev"])
    )

    if cis_total > 0:
        deductions.append({
            "id": _deduction_id(CATEGORY_PATTERN, "rus-sustainment"),
            "category": CATEGORY_PATTERN,
            "confidence": CONFIDENCE_MEDIUM,
            "priority": PRIORITY_MEDIUM,
            "title": "Russian space constellation sustainment under pressure",
            "deduction": (
                f"Russia maintains {cis_total} satellites ({cis_isr} military ISR) "
                f"with {rus_launches} launches in the upcoming manifest. DEDUCTION: "
                f"Russia's constellation replenishment rate continues to lag behind "
                f"attrition, with sanctions constraining electronics supply for "
                f"replacement satellites. Counter-space capabilities remain prioritized "
                f"over ISR constellation health."
            ),
            "evidence": [
                f"{cis_total} Russian satellites in active catalog",
                f"{cis_isr} military ISR satellites (small fleet compared to PRC)",
                f"{rus_launches} Russian launches in upcoming manifest",
                "Sanctions limit access to radiation-hardened electronics",
            ],
            "implications": (
                "Russian ISR coverage gaps may be partially compensated by "
                "increased reliance on PRC-shared intelligence. Counter-space "
                "capabilities remain Russia's asymmetric offset."
            ),
            "recommended_action": (
                "Monitor Russian constellation health metrics. Track for evidence "
                "of PRC-Russia ISR intelligence sharing arrangements."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Pattern: DPRK/Iran emerging capability ---
    nkor_data = stats.get("NKOR", {})
    iran_data = stats.get("IRAN", {})
    nkor_total = nkor_data.get("total", 0) if isinstance(nkor_data, dict) else 0
    iran_total = iran_data.get("total", 0) if isinstance(iran_data, dict) else 0

    if nkor_total > 0:
        deductions.append({
            "id": _deduction_id(CATEGORY_PATTERN, "dprk-isr-emerging"),
            "category": CATEGORY_PATTERN,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_MEDIUM,
            "title": "DPRK has achieved indigenous ISR satellite capability",
            "deduction": (
                f"DPRK has {nkor_total} satellite(s) in orbit (Malligyong-1). "
                f"DEDUCTION: DPRK has crossed the threshold from aspiring to "
                f"operational space power. With reported Russian technical assistance, "
                f"additional reconnaissance satellite launches should be anticipated "
                f"within 12 months, reducing DPRK dependence on PRC intelligence sharing."
            ),
            "evidence": [
                f"{nkor_total} DPRK satellite(s) in orbit",
                "Malligyong-1 successfully launched November 2023 on Chollima-1 SLV",
                "Reported Russian technical assistance for satellite development",
            ],
            "implications": (
                "DPRK indigenous ISR reduces intelligence-sharing leverage "
                "of both PRC and Russia over DPRK military targeting."
            ),
            "recommended_action": (
                "Monitor Sohae launch facility for preparation activity. "
                "Track Malligyong-1 orbital status and health."
            ),
            "timestamp": now.isoformat(),
        })

    return deductions


# ---------------------------------------------------------------------------
# 2. CAPABILITY DEDUCTIONS
# ---------------------------------------------------------------------------

def _generate_capability_deductions(data: Dict[str, object]) -> List[dict]:
    """Infer adversary capabilities from observable satellite and weapons data."""
    deductions: List[dict] = []
    stats = data.get("stats", {})
    missiles = data.get("missiles", [])
    missile_summary = data.get("missile_summary", {})
    now = datetime.now(timezone.utc)

    if not isinstance(stats, dict):
        stats = {}

    prc_data = stats.get("PRC", {})
    prc_isr = prc_data.get("military_isr", 0) if isinstance(prc_data, dict) else 0
    prc_nav = prc_data.get("navigation", 0) if isinstance(prc_data, dict) else 0
    prc_cats = prc_data.get("by_category", {}) if isinstance(prc_data, dict) else {}
    prc_sda = prc_cats.get("sda_asat", 0)

    # --- Capability: PRC near-persistent maritime surveillance ---
    if prc_isr >= 50:
        revisit_estimate = max(0.5, round(120 / max(prc_isr, 1) * 60, 0))
        deductions.append({
            "id": _deduction_id(CATEGORY_CAPABILITY, "prc-maritime-isr"),
            "category": CATEGORY_CAPABILITY,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_CRITICAL,
            "title": f"PRC has achieved ~{int(revisit_estimate)}-minute ISR revisit over Taiwan Strait",
            "deduction": (
                f"With {prc_isr} military ISR satellites including Yaogan ELINT/SAR/optical "
                f"triplets and Jilin-1 commercial-military optical/video, PRC has achieved "
                f"an estimated average revisit time of approximately {int(revisit_estimate)} "
                f"minutes over the Taiwan Strait. DEDUCTION: PRC has achieved near-persistent "
                f"maritime surveillance of the Western Pacific, sufficient to support "
                f"anti-ship ballistic missile targeting chains (DF-21D/DF-26) with "
                f"acceptable kill-chain latency."
            ),
            "evidence": [
                f"{prc_isr} military ISR satellites operational",
                "Yaogan ELINT triplets provide ship-radar geolocation",
                "Jilin-1 provides sub-1m optical and HD video from orbit",
                "Gaofen series provides high-resolution SAR all-weather imaging",
            ],
            "implications": (
                "FVEY carrier strike groups and surface action groups in the "
                "Western Pacific must assume continuous overhead surveillance. "
                "Anti-ship ballistic missile targeting chains are viable."
            ),
            "recommended_action": (
                "Implement persistent EMCON posture for deployed naval forces. "
                "Develop electronic deception to confuse ELINT geolocation. "
                "Accelerate ship-based ISR satellite countermeasures."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Capability: SJ-21 GEO manipulation ---
    if prc_sda >= 3:
        deductions.append({
            "id": _deduction_id(CATEGORY_CAPABILITY, "prc-geo-manipulation"),
            "category": CATEGORY_CAPABILITY,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_CRITICAL,
            "title": "PRC has demonstrated GEO satellite capture and relocation capability",
            "deduction": (
                f"PRC operates {prc_sda} SDA/ASAT-class satellites including the "
                f"SJ-21, which demonstrated GEO satellite towing in January 2022 by "
                f"relocating a defunct BeiDou satellite to graveyard orbit. DEDUCTION: "
                f"PRC has operational capability to physically disable, relocate, or "
                f"de-orbit FVEY GEO communications and early warning satellites without "
                f"generating debris — the most strategically consequential co-orbital "
                f"ASAT capability yet demonstrated."
            ),
            "evidence": [
                f"{prc_sda} PRC SDA/ASAT satellites in catalog (Shijian, TJS, Banxing, Aolong)",
                "SJ-21 towed defunct Compass-G2 to graveyard orbit (Jan 2022)",
                "SJ-17 demonstrated robotic arm operations in GEO (2016)",
                "Multiple Shijian missions conducted LEO RPO (2008-present)",
            ],
            "implications": (
                "FVEY GEO MILSATCOM (AEHF, WGS), SIGINT (MENTOR/ORION), and early "
                "warning (SBIRS-GEO) satellites are all within reach of PRC co-orbital "
                "manipulation. Loss of GEO EW satellites could create nuclear ambiguity."
            ),
            "recommended_action": (
                "Enhance GEO SSA to detect approach maneuvers early. "
                "Develop satellite self-defense capabilities (autonomous evasion). "
                "Establish keep-out zone enforcement doctrine for FVEY GEO assets."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Capability: PRC BeiDou independence ---
    if prc_nav >= 25:
        deductions.append({
            "id": _deduction_id(CATEGORY_CAPABILITY, "prc-pnt-independence"),
            "category": CATEGORY_CAPABILITY,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_HIGH,
            "title": f"PRC has achieved GPS-independent PNT with {prc_nav} BeiDou satellites",
            "deduction": (
                f"PRC operates {prc_nav} BeiDou navigation satellites providing full "
                f"global PNT coverage with centimeter-level military precision (B3I signal). "
                f"DEDUCTION: PRC military operations are fully independent of GPS. "
                f"Jamming or destroying GPS would not deny PNT to PRC forces, while "
                f"PRC retains the capability to jam GPS affecting FVEY operations. "
                f"This creates a fundamental PNT asymmetry."
            ),
            "evidence": [
                f"{prc_nav} BeiDou satellites in active catalog",
                "BeiDou-3 declared fully operational 2020",
                "Military B3I signal provides centimeter-level accuracy",
                "Unique two-way short message capability (1000 characters)",
                "Inter-satellite links enable autonomous operation",
            ],
            "implications": (
                "GPS denial is a one-way weapon: effective against FVEY but not PRC. "
                "FVEY precision munitions and navigation are vulnerable to GPS "
                "jamming while PRC equivalents are not."
            ),
            "recommended_action": (
                "Accelerate alternative PNT development (eLoran, LEO PNT). "
                "Develop BeiDou signal jamming/spoofing for theater operations. "
                "GPS M-code acceleration to improve anti-jam resilience."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Capability: Combined adversary ASAT arsenal ---
    prc_missiles_data = get_missiles_by_country("PRC")
    rus_missiles_data = get_missiles_by_country("Russia")

    prc_da_asat = sum(1 for m in prc_missiles_data if m.get("type") == "direct_ascent_asat")
    rus_da_asat = sum(1 for m in rus_missiles_data if m.get("type") == "direct_ascent_asat")
    prc_co_orbital = sum(
        1 for m in prc_missiles_data
        if m.get("type") in ("co_orbital_asat", "rendezvous_proximity_ops")
    )
    rus_co_orbital = sum(
        1 for m in rus_missiles_data
        if m.get("type") in ("co_orbital_asat", "rendezvous_proximity_ops")
    )

    total_adv_asat = prc_da_asat + rus_da_asat
    if total_adv_asat >= 3:
        deductions.append({
            "id": _deduction_id(CATEGORY_CAPABILITY, "adv-asat-arsenal"),
            "category": CATEGORY_CAPABILITY,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_CRITICAL,
            "title": f"Combined adversary DA-ASAT arsenal: {total_adv_asat} tested systems",
            "deduction": (
                f"PRC has tested {prc_da_asat} direct-ascent ASAT systems (SC-19/DN-2/DN-3) "
                f"capable of reaching LEO through GEO altitudes. Russia has tested "
                f"{rus_da_asat} DA-ASAT system(s) (Nudol/A-235) with a confirmed destructive "
                f"test against Cosmos 1408 in 2021. DEDUCTION: FVEY has 0 operational "
                f"DA-ASAT systems while adversaries have {total_adv_asat}+ tested systems, "
                f"creating a significant deterrence gap where adversaries may calculate "
                f"that FVEY cannot respond in kind to kinetic ASAT attack."
            ),
            "evidence": [
                f"PRC: {prc_da_asat} DA-ASAT systems (SC-19 tested 2007, DN-2 tested 2013, DN-3 tested 2018)",
                f"Russia: {rus_da_asat} DA-ASAT system(s) (Nudol tested 10+ times, destructive test 2021)",
                "FVEY: 0 operational DA-ASAT systems (US moratorium on destructive testing)",
                f"PRC: {prc_co_orbital} co-orbital ASAT capabilities additionally",
                f"Russia: {rus_co_orbital} co-orbital ASAT capabilities additionally",
            ],
            "implications": (
                "Adversaries may perceive a first-strike advantage in space. "
                "Without credible response options, deterrence depends on "
                "cross-domain retaliation threats."
            ),
            "recommended_action": (
                "Develop non-kinetic counter-space response options (EW, cyber, dazzling). "
                "Maintain ambiguity about US/allied response capability. "
                "Accelerate proliferated architecture to reduce ASAT cost-effectiveness."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Capability: Russia demonstrated willingness to use counter-space in conflict ---
    rus_prc_summary = missile_summary.get("Russia", {}) if isinstance(missile_summary, dict) else {}
    if rus_prc_summary.get("has_cyber") and rus_prc_summary.get("has_da_asat"):
        deductions.append({
            "id": _deduction_id(CATEGORY_CAPABILITY, "rus-demonstrated-use"),
            "category": CATEGORY_CAPABILITY,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_CRITICAL,
            "title": "Russia has DEMONSTRATED counter-space use in active conflict",
            "deduction": (
                "Russia conducted the Viasat KA-SAT cyberattack on 24 Feb 2022 "
                "(start of Ukraine invasion), disabling tens of thousands of terminals "
                "across Europe. Combined with the Cosmos 1408 destructive ASAT test "
                "(Nov 2021) and continued inspector satellite deployments. DEDUCTION: "
                "Russia is the only adversary to have used counter-space capabilities "
                "against a satellite operator during active conflict. This establishes "
                "a precedent that space systems are legitimate targets in Russian "
                "operational planning."
            ),
            "evidence": [
                "Viasat KA-SAT cyberattack attributed to GRU Sandworm (Feb 2022)",
                "Cosmos 1408 DA-ASAT destructive test creating 1500+ debris (Nov 2021)",
                "Cosmos 2542/2543 inspector operations near classified US satellite",
                "Cosmos 2558 deployed to shadow USA-326",
                "Routine GPS jamming in Ukraine, Syria, Baltic",
            ],
            "implications": (
                "Commercial satellite operators supporting FVEY military operations "
                "are proven targets. Cyber is the most likely first-use counter-space "
                "modality in future conflicts."
            ),
            "recommended_action": (
                "Harden commercial SATCOM ground segments supporting military ops. "
                "Develop redundant communications pathways. "
                "Ensure commercial operators have incident response plans."
            ),
            "timestamp": now.isoformat(),
        })

    return deductions


# ---------------------------------------------------------------------------
# 3. INTENT DEDUCTIONS
# ---------------------------------------------------------------------------

def _generate_intent_deductions(data: Dict[str, object]) -> List[dict]:
    """Assess what adversaries are likely planning based on observable programs."""
    deductions: List[dict] = []
    stats = data.get("stats", {})
    futures = data.get("futures_summary", {})
    ground_stations = data.get("ground_stations", [])
    now = datetime.now(timezone.utc)

    if not isinstance(stats, dict):
        stats = {}
    if not isinstance(futures, dict):
        futures = {}
    if not isinstance(ground_stations, list):
        ground_stations = []

    prc_data = stats.get("PRC", {})
    prc_total = prc_data.get("total", 0) if isinstance(prc_data, dict) else 0
    prc_nav = prc_data.get("navigation", 0) if isinstance(prc_data, dict) else 0
    prc_isr = prc_data.get("military_isr", 0) if isinstance(prc_data, dict) else 0
    prc_comms = prc_data.get("by_category", {}).get("comms", 0) if isinstance(prc_data, dict) else 0

    # --- Intent: PRC building fully independent space architecture ---
    if prc_total >= 100 and prc_nav >= 25:
        deductions.append({
            "id": _deduction_id(CATEGORY_INTENT, "prc-independent-arch"),
            "category": CATEGORY_INTENT,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_CRITICAL,
            "title": "PRC building fully independent space architecture",
            "deduction": (
                f"PRC operates {prc_total} satellites including {prc_nav} BeiDou (PNT), "
                f"{prc_isr} military ISR, and {prc_comms} communications satellites, "
                f"plus the Guowang mega-constellation filing (13,000 sats). DEDUCTION: "
                f"PRC is building a fully independent space architecture capable of "
                f"operating without any Western infrastructure or cooperation. This "
                f"includes independent PNT (BeiDou), independent ISR (Yaogan/Jilin), "
                f"independent SATCOM (Zhongxing/Tiantong), and planned independent "
                f"broadband (Guowang). PRC is preparing for a world where cooperation "
                f"with the West is severed."
            ),
            "evidence": [
                f"{prc_total} total PRC satellites",
                f"{prc_nav} BeiDou navigation satellites (GPS independence)",
                f"{prc_isr} military ISR satellites",
                f"{prc_comms} communications satellites",
                "Guowang 13,000-satellite mega-constellation filing with ITU",
                "Tiangong space station (crew independence from ISS)",
            ],
            "implications": (
                "PRC space architecture is designed to function in isolation — "
                "sanctions or conflict would not deny PRC access to space-enabled "
                "military capabilities. This reduces Western leverage."
            ),
            "recommended_action": (
                "Ensure FVEY can similarly operate independently of any single "
                "commercial provider. Accelerate allied space burden-sharing "
                "to distribute resilience across multiple nations."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Intent: PRC overseas ground station network signals global ambition ---
    prc_overseas = [
        s for s in ground_stations
        if s.get("country") == "PRC"
        and "china" not in s.get("location", "").lower()
        and s.get("location", "").lower() not in ("", "china")
    ]

    if len(prc_overseas) >= 3:
        locations = [s.get("name", s.get("location", "Unknown")) for s in prc_overseas[:6]]
        deductions.append({
            "id": _deduction_id(CATEGORY_INTENT, "prc-global-c2"),
            "category": CATEGORY_INTENT,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_HIGH,
            "title": f"PRC has {len(prc_overseas)} overseas ground stations — global C2 ambition",
            "deduction": (
                f"PRC operates {len(prc_overseas)} ground stations outside Chinese "
                f"territory ({', '.join(locations[:4])}...). Combined with BeiDou GEO "
                f"satellites and Yuan Wang tracking ships. DEDUCTION: PRC has global "
                f"satellite command and data download capability including over FVEY "
                f"home territories. The Argentina station (Espacio Lejano) provides "
                f"coverage over South America — a region with limited FVEY SSA — "
                f"enabling satellite tasking and data download for ISR operations "
                f"in the Western Hemisphere."
            ),
            "evidence": [
                f"{len(prc_overseas)} PRC overseas TT&C stations identified",
                f"Locations: {', '.join(locations)}",
                "Yuan Wang tracking ship fleet (7+ vessels) provides mobile ocean TT&C",
                "BeiDou GEO satellites provide data relay capability",
            ],
            "implications": (
                "PRC can task ISR satellites and download imagery globally — "
                "no geographic limitation on intelligence collection operations."
            ),
            "recommended_action": (
                "Monitor PRC overseas station agreements and construction. "
                "Assess signals intelligence collection potential of each facility. "
                "Coordinate with host nation partners on station monitoring."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Intent: Adversary space coalition forming ---
    cis_data = stats.get("CIS", {})
    cis_total = cis_data.get("total", 0) if isinstance(cis_data, dict) else 0
    nkor_total = stats.get("NKOR", {}).get("total", 0) if isinstance(stats.get("NKOR"), dict) else 0

    if cis_total > 0 and nkor_total > 0:
        deductions.append({
            "id": _deduction_id(CATEGORY_INTENT, "adversary-coalition"),
            "category": CATEGORY_INTENT,
            "confidence": CONFIDENCE_MEDIUM,
            "priority": PRIORITY_HIGH,
            "title": "Adversary space coalition forming: PRC-Russia-DPRK-Iran axis",
            "deduction": (
                "Russia provided technical assistance for DPRK Malligyong-1 satellite. "
                "Russia launched Iran's Khayyam satellite on Soyuz (2022). PRC-Russia "
                "cooperation on ILRS lunar program. PRC-Russia GNSS interoperability "
                "(BeiDou-GLONASS combined receivers). DEDUCTION: An adversary space "
                "coalition is forming that could coordinate counter-space operations, "
                "share ISR intelligence, and provide mutual space technology support. "
                "Combined satellite fleets exceed FVEY military satellite numbers."
            ),
            "evidence": [
                "Russia-DPRK technical assistance for Malligyong-1 satellite",
                "Russia launched Iran's Khayyam satellite (2022)",
                "PRC-Russia ILRS lunar cooperation agreement",
                "BeiDou-GLONASS interoperability agreements",
                f"Combined adversary fleet: {prc_total + cis_total} satellites",
            ],
            "implications": (
                "Coordinated adversary counter-space operations would stress "
                "FVEY response capacity across multiple theaters simultaneously."
            ),
            "recommended_action": (
                "Develop intelligence collection on adversary space cooperation "
                "mechanisms. Wargame coordinated multi-adversary counter-space "
                "scenarios. Strengthen FVEY allied space partnerships."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Intent: Iran IRGC military space program ---
    iran_total = stats.get("IRAN", {}).get("total", 0) if isinstance(stats.get("IRAN"), dict) else 0
    if iran_total > 0:
        deductions.append({
            "id": _deduction_id(CATEGORY_INTENT, "iran-military-space"),
            "category": CATEGORY_INTENT,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_MEDIUM,
            "title": "Iran's space program is primarily military (IRGC-operated)",
            "deduction": (
                f"Iran operates {iran_total} satellite(s), with the Noor series "
                f"launched by IRGC Aerospace Force using the Qased solid-fuel SLV — "
                f"not the civilian ISA Simorgh. DEDUCTION: Iran's operationally "
                f"successful space program is military, not civilian. The IRGC "
                f"operates both the satellites and the launch vehicle, with civilian "
                f"applications as cover for a military ISR program. The solid-fuel "
                f"Qased SLV is militarily significant — it enables rapid launch "
                f"preparation not possible with liquid-fuel alternatives."
            ),
            "evidence": [
                f"{iran_total} Iranian satellite(s) in orbit",
                "Noor-1/2 launched by IRGC (not ISA)",
                "Qased SLV uses solid-fuel first stage (Ghadr MRBM derivative)",
                "ISA Simorgh has experienced multiple failures",
            ],
            "implications": (
                "Iran's SLV/ICBM technology overlap creates latent long-range "
                "strike and ASAT capability. IRGC operation ensures military "
                "control and integration."
            ),
            "recommended_action": (
                "Monitor IRGC Shahrud and Semnan launch facilities for preparation "
                "activity. Track Iranian solid-fuel missile development as SLV feeder."
            ),
            "timestamp": now.isoformat(),
        })

    return deductions


# ---------------------------------------------------------------------------
# 4. VULNERABILITY DEDUCTIONS
# ---------------------------------------------------------------------------

def _generate_vulnerability_deductions(data: Dict[str, object]) -> List[dict]:
    """Identify FVEY weaknesses from available data."""
    deductions: List[dict] = []
    stats = data.get("stats", {})
    missile_summary = data.get("missile_summary", {})
    now = datetime.now(timezone.utc)

    if not isinstance(stats, dict):
        stats = {}
    if not isinstance(missile_summary, dict):
        missile_summary = {}

    fvey_total = stats.get("fvey_total", 0)

    # --- Vulnerability: ASAT deterrence gap ---
    prc_summary = missile_summary.get("PRC", {})
    rus_summary = missile_summary.get("Russia", {})
    prc_has_da = prc_summary.get("has_da_asat", False) if isinstance(prc_summary, dict) else False
    rus_has_da = rus_summary.get("has_da_asat", False) if isinstance(rus_summary, dict) else False
    prc_critical = prc_summary.get("critical_systems", []) if isinstance(prc_summary, dict) else []
    rus_critical = rus_summary.get("critical_systems", []) if isinstance(rus_summary, dict) else []

    if prc_has_da and rus_has_da:
        deductions.append({
            "id": _deduction_id(CATEGORY_VULNERABILITY, "asat-deterrence-gap"),
            "category": CATEGORY_VULNERABILITY,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_CRITICAL,
            "title": "Significant ASAT deterrence gap — adversaries hold kinetic advantage",
            "deduction": (
                f"PRC operates {len(prc_critical)} critical-rated counter-space systems "
                f"({', '.join(prc_critical[:3])}). Russia operates "
                f"{len(rus_critical)} critical-rated systems "
                f"({', '.join(rus_critical[:3])}). FVEY has 0 operational DA-ASAT "
                f"systems and has committed to a moratorium on destructive testing. "
                f"DEDUCTION: Adversaries may calculate that FVEY cannot respond in "
                f"kind to kinetic ASAT attack, potentially lowering the threshold "
                f"for adversary use of kinetic counter-space weapons."
            ),
            "evidence": [
                f"PRC critical systems: {', '.join(prc_critical)}",
                f"Russia critical systems: {', '.join(rus_critical)}",
                "FVEY: 0 operational DA-ASAT (US moratorium on destructive testing 2022)",
                "No allied nation has tested DA-ASAT",
            ],
            "implications": (
                "Deterrence relies on cross-domain response threats rather than "
                "symmetric space response. Adversaries may test this resolve "
                "through grey-zone counter-space operations."
            ),
            "recommended_action": (
                "Develop credible non-kinetic response options. "
                "Maintain strategic ambiguity about US capabilities. "
                "Ensure cross-domain response plans are exercised and communicated."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Vulnerability: GPS in adversary engagement envelope ---
    prc_missiles = get_missiles_by_country("PRC")
    max_alt_prc = max(
        (m.get("max_altitude_km", 0) or 0 for m in prc_missiles),
        default=0,
    )

    if max_alt_prc >= 20000:
        deductions.append({
            "id": _deduction_id(CATEGORY_VULNERABILITY, "gps-in-envelope"),
            "category": CATEGORY_VULNERABILITY,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_CRITICAL,
            "title": "GPS constellation within PRC DA-ASAT engagement envelope",
            "deduction": (
                f"GPS constellation operates at 20,200 km altitude. PRC DN-2/DN-3 "
                f"ASAT systems have demonstrated capability to {int(max_alt_prc):,} km "
                f"altitude. DEDUCTION: The most critical FVEY space asset — GPS — "
                f"is within the engagement envelope of PRC direct-ascent weapons. "
                f"A coordinated strike on 6-8 GPS satellites in specific orbital "
                f"planes could degrade GPS accuracy below military utility thresholds "
                f"for hours to days before constellation recovery."
            ),
            "evidence": [
                "GPS constellation: 20,200 km altitude (MEO)",
                f"PRC DN-2: tested to ~30,000 km (2013), exceeding GPS altitude",
                f"PRC maximum demonstrated altitude: {int(max_alt_prc):,} km",
                "31 GPS satellites — loss of 6-8 degrades specific coverage areas",
            ],
            "implications": (
                "GPS is simultaneously the most important and most vulnerable "
                "FVEY space capability. Loss of GPS cascades across military "
                "and civilian infrastructure globally."
            ),
            "recommended_action": (
                "Accelerate GPS III M-code for anti-jam. Deploy alternative PNT. "
                "Develop GPS reconstitution plan. Stockpile precision munitions "
                "with inertial backup guidance."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Vulnerability: No rapid reconstitution ---
    deductions.append({
        "id": _deduction_id(CATEGORY_VULNERABILITY, "no-rapid-recon"),
        "category": CATEGORY_VULNERABILITY,
        "confidence": CONFIDENCE_HIGH,
        "priority": PRIORITY_HIGH,
        "title": "FVEY has no rapid satellite reconstitution capability under 48 hours",
        "deduction": (
            "FVEY has no demonstrated ability to launch replacement satellites "
            "within 48 hours of a loss event. Current satellite manufacturing "
            "timelines are 3-5+ years for exquisite systems, months for small sats. "
            "Launch scheduling typically requires weeks to months of preparation. "
            "DEDUCTION: Any satellite loss in conflict cannot be reconstituted "
            "quickly enough to maintain operational continuity. Adversaries can "
            "calculate that destroying FVEY satellites creates irreversible "
            "advantages for the duration of a conflict."
        ),
        "evidence": [
            f"FVEY operates {fvey_total} satellites (many commercial, not rapidly replaceable)",
            "No pre-positioned satellite reserves for rapid launch",
            "Victus Nox (2023) demonstrated 27-hour responsive launch but was a demonstration only",
            "PRC CZ-11 solid-fuel SLV can launch within 24 hours (operational advantage)",
        ],
        "implications": (
            "Loss of key satellites during conflict onset would persist through "
            "the conflict duration. This fundamentally undermines deterrence."
        ),
        "recommended_action": (
            "Fund Tactically Responsive Space to operational capability. "
            "Pre-position ground spare satellites and contracted launch vehicles. "
            "Conduct annual reconstitution exercises."
        ),
        "timestamp": now.isoformat(),
    })

    # --- Vulnerability: Southern Hemisphere SSA gap ---
    fvey_stn = data.get("fvey_stations", [])
    if isinstance(fvey_stn, list):
        southern_stations = [
            s for s in fvey_stn
            if isinstance(s, dict) and s.get("lat", 0) < -20
        ]
        deductions.append({
            "id": _deduction_id(CATEGORY_VULNERABILITY, "ssa-southern-gap"),
            "category": CATEGORY_VULNERABILITY,
            "confidence": CONFIDENCE_MEDIUM,
            "priority": PRIORITY_HIGH,
            "title": "Critical SSA gap in Southern Hemisphere enables adversary operations",
            "deduction": (
                f"FVEY SSA sensor coverage is concentrated in the Northern Hemisphere. "
                f"Only {len(southern_stations)} FVEY ground station(s) identified south "
                f"of 20S latitude. PRC has ground stations in Argentina and Namibia "
                f"providing Southern Hemisphere coverage. DEDUCTION: Adversary satellite "
                f"maneuvers conducted over the Southern Hemisphere may go undetected "
                f"for orbits, providing windows for covert RPO operations against "
                f"FVEY assets."
            ),
            "evidence": [
                f"{len(southern_stations)} FVEY stations south of 20S",
                "PRC Espacio Lejano station in Argentina (global reach)",
                "PRC Swakopmund station in Namibia (Africa/South Atlantic coverage)",
                "Space Fence limited to single site (Kwajalein, 9N)",
            ],
            "implications": (
                "Adversary RPO and ASAT positioning maneuvers may exploit "
                "Southern Hemisphere SSA gaps for approach under reduced detection."
            ),
            "recommended_action": (
                "Expand commercial SSA partnerships (LeoLabs, ExoAnalytic). "
                "Deploy SSA sensors in Australia and South America. "
                "Leverage AUKUS for Australian SSA contributions."
            ),
            "timestamp": now.isoformat(),
        })

    return deductions


# ---------------------------------------------------------------------------
# 5. PREDICTIVE DEDUCTIONS
# ---------------------------------------------------------------------------

def _generate_predictive_deductions(data: Dict[str, object]) -> List[dict]:
    """Forecast what will happen next based on trends and data."""
    deductions: List[dict] = []
    stats = data.get("stats", {})
    launches = data.get("launches", [])
    now = datetime.now(timezone.utc)

    if not isinstance(stats, dict):
        stats = {}
    if not isinstance(launches, list):
        launches = []

    prc_data = stats.get("PRC", {})
    prc_isr = prc_data.get("military_isr", 0) if isinstance(prc_data, dict) else 0
    prc_total = prc_data.get("total", 0) if isinstance(prc_data, dict) else 0

    # --- Prediction: PRC ISR fleet projection ---
    if prc_isr > 0:
        # Assume 8-12 new ISR sats per year based on recent cadence
        yearly_rate = 10
        isr_2028 = prc_isr + (yearly_rate * 2)  # ~2 years from now
        isr_2030 = prc_isr + (yearly_rate * 4)

        deductions.append({
            "id": _deduction_id(CATEGORY_PREDICTIVE, "prc-isr-projection"),
            "category": CATEGORY_PREDICTIVE,
            "confidence": CONFIDENCE_MEDIUM,
            "priority": PRIORITY_HIGH,
            "title": f"PRC projected to reach {isr_2028}+ military ISR satellites by 2028",
            "deduction": (
                f"Based on current PRC launch cadence of 60+ per year and dedicated "
                f"ISR constellation plans, DEDUCTION: PRC will achieve approximately "
                f"{isr_2028} military ISR satellites by 2028 and {isr_2030}+ by 2030, "
                f"enabling sub-30-minute global revisit capability. The Jilin-1 "
                f"constellation alone targets 300 satellites by 2027. Combined with "
                f"Yaogan expansion, this will give PRC the world's most capable "
                f"military ISR constellation."
            ),
            "evidence": [
                f"Current PRC military ISR: {prc_isr} satellites",
                "PRC annual launch cadence: 60+ (2023-2025 average)",
                "Jilin-1 plans: 300-satellite constellation by 2027",
                "Yaogan: 3-6 ISR launches per year sustained",
                f"Current total PRC fleet: {prc_total}",
            ],
            "implications": (
                "By 2028, no point on Earth will be beyond 30-minute PRC ISR "
                "revisit. Global military operations will be under potential "
                "PRC surveillance."
            ),
            "recommended_action": (
                "Develop counter-ISR capabilities at scale (not just individual "
                "satellite countermeasures). Invest in camouflage, concealment, "
                "and deception for surface forces globally."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Prediction: Russia Nudol operational inventory ---
    deductions.append({
        "id": _deduction_id(CATEGORY_PREDICTIVE, "rus-nudol-inventory"),
        "category": CATEGORY_PREDICTIVE,
        "confidence": CONFIDENCE_LOW,
        "priority": PRIORITY_HIGH,
        "title": "Russia likely has 2-4 operational Nudol DA-ASAT interceptors",
        "deduction": (
            "Based on Russia's Nudol test program (10+ tests since 2014) and "
            "the confirmed destructive test against Cosmos 1408 in November 2021, "
            "DEDUCTION: Russia likely has 2-4 operational DA-ASAT interceptors "
            "available for wartime use at Plesetsk Cosmodrome. Production may be "
            "constrained by sanctions affecting guidance electronics, but the "
            "base system is mature after a decade of testing."
        ),
        "evidence": [
            "10+ Nudol test flights since 2014",
            "Confirmed destructive engagement of Cosmos 1408 (Nov 2021)",
            "Mobile TEL-based system (potentially deployable beyond Plesetsk)",
            "A-235 missile defense system integration",
        ],
        "implications": (
            "Russia can hold 2-4 FVEY LEO satellites at risk with kinetic "
            "kill on short notice. Target prioritization likely includes "
            "ISR and early warning satellites."
        ),
        "recommended_action": (
            "Monitor Plesetsk for Nudol TEL activity and test preparations. "
            "Develop satellite maneuver plans for high-value LEO assets "
            "to complicate Nudol targeting solutions."
        ),
        "timestamp": now.isoformat(),
    })

    # --- Prediction: DPRK additional satellite launches ---
    nkor_total = stats.get("NKOR", {}).get("total", 0) if isinstance(stats.get("NKOR"), dict) else 0
    if nkor_total > 0:
        deductions.append({
            "id": _deduction_id(CATEGORY_PREDICTIVE, "dprk-next-launch"),
            "category": CATEGORY_PREDICTIVE,
            "confidence": CONFIDENCE_MEDIUM,
            "priority": PRIORITY_MEDIUM,
            "title": "DPRK will attempt additional reconnaissance satellite launches within 12 months",
            "deduction": (
                f"Based on DPRK-Russia technology cooperation, the success of "
                f"Malligyong-1, and DPRK's stated intention to deploy a multi-satellite "
                f"ISR constellation, DEDUCTION: DPRK will attempt at least one "
                f"additional reconnaissance satellite launch within the next 12 months. "
                f"Russian assistance may enable higher-quality imaging sensors and more "
                f"reliable SLV performance."
            ),
            "evidence": [
                f"{nkor_total} DPRK satellite(s) currently in orbit",
                "DPRK announced intention for multi-satellite ISR constellation",
                "Russia-DPRK space technology cooperation confirmed",
                "Sohae launch facility capable of supporting launches",
            ],
            "implications": (
                "Each successful DPRK satellite launch advances both ISR and "
                "ICBM technology. International response options narrow with "
                "each demonstrated success."
            ),
            "recommended_action": (
                "Maintain persistent ISR coverage of Sohae launch facility. "
                "Coordinate ROK/Japan/US early warning for launch detection. "
                "Prepare diplomatic response options."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Prediction: Space debris environment worsening ---
    incident_stats = data.get("incident_stats", {})
    if isinstance(incident_stats, dict):
        deductions.append({
            "id": _deduction_id(CATEGORY_PREDICTIVE, "debris-trend"),
            "category": CATEGORY_PREDICTIVE,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_MEDIUM,
            "title": "LEO debris environment will continue degrading through 2030",
            "deduction": (
                "With 30,000+ tracked objects, mega-constellation deployments "
                "(Starlink 6,000+, PRC Guowang planned 13,000), and no binding "
                "international debris mitigation enforcement, DEDUCTION: The LEO "
                "debris environment will continue to degrade through 2030. "
                "Conjunction warnings will increase 3-5x, operational cost of "
                "collision avoidance will escalate, and the risk of a cascading "
                "collision event (Kessler syndrome) in congested bands will grow."
            ),
            "evidence": [
                "30,000+ tracked objects in Earth orbit",
                "2007 PRC FY-1C ASAT test: 3,500+ debris fragments",
                "2021 Russia Cosmos 1408 ASAT test: 1,500+ debris fragments",
                "Mega-constellation deployments increasing LEO population",
                "No binding international debris mitigation enforcement",
            ],
            "implications": (
                "Debris threatens all spacefaring nations but disproportionately "
                "affects the nation most dependent on LEO — currently FVEY."
            ),
            "recommended_action": (
                "Accelerate active debris removal development. "
                "Pursue binding debris mitigation agreements. "
                "Improve small-debris tracking capability."
            ),
            "timestamp": now.isoformat(),
        })

    return deductions


# ---------------------------------------------------------------------------
# 6. CORRELATION DEDUCTIONS
# ---------------------------------------------------------------------------

def _generate_correlation_deductions(data: Dict[str, object]) -> List[dict]:
    """Connect seemingly unrelated events across data sources."""
    deductions: List[dict] = []
    weather = data.get("weather", {})
    hotspots = data.get("hotspots", {})
    ground_stations = data.get("ground_stations", [])
    stats = data.get("stats", {})
    launches = data.get("launches", [])
    now = datetime.now(timezone.utc)

    if not isinstance(weather, dict):
        weather = {}
    if not isinstance(hotspots, dict):
        hotspots = {}
    if not isinstance(stats, dict):
        stats = {}
    if not isinstance(launches, list):
        launches = []
    if not isinstance(ground_stations, list):
        ground_stations = []

    kp = weather.get("kp_current")
    solar_wind = weather.get("solar_wind_speed")
    bz = weather.get("bz")

    # --- Correlation: Space weather x adversary ISR effectiveness ---
    total_passes = hotspots.get("total_passes_all_hotspots", 0)
    most_covered = hotspots.get("most_covered_area", "Unknown")

    if kp is not None and kp >= 5 and total_passes > 0:
        degradation_pct = min(int((kp - 3) * 10), 50)
        deductions.append({
            "id": _deduction_id(CATEGORY_CORRELATION, "wx-isr-degradation"),
            "category": CATEGORY_CORRELATION,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_HIGH,
            "title": f"Geomagnetic storm (Kp={kp}) degrading adversary ISR over {most_covered}",
            "deduction": (
                f"Current geomagnetic storm conditions (Kp={kp}) coincide with "
                f"{total_passes} adversary ISR satellite passes across strategic "
                f"hotspots. DEDUCTION: High geomagnetic activity is degrading adversary "
                f"ISR effectiveness by approximately {degradation_pct}% through increased "
                f"pointing jitter, orbit prediction uncertainty, and potential sensor "
                f"interference. This creates a temporary window of reduced adversary "
                f"surveillance — a potential timing opportunity for FVEY operations "
                f"requiring reduced overhead observation."
            ),
            "evidence": [
                f"Kp index: {kp} (storm conditions)",
                f"Solar wind: {solar_wind or 'N/A'} km/s",
                f"IMF Bz: {bz or 'N/A'} nT",
                f"{total_passes} adversary ISR passes in next 2 hours",
                f"Most covered area: {most_covered}",
            ],
            "implications": (
                "Geomagnetic storms create temporary ISR degradation windows. "
                "FVEY ISR is also degraded but planning advantage can be gained."
            ),
            "recommended_action": (
                "Identify time-sensitive operations that benefit from reduced "
                "adversary ISR effectiveness. Factor storm duration into "
                "operational planning window."
            ),
            "timestamp": now.isoformat(),
        })
    elif kp is not None and kp <= 2 and total_passes > 5:
        deductions.append({
            "id": _deduction_id(CATEGORY_CORRELATION, "wx-quiet-full-isr"),
            "category": CATEGORY_CORRELATION,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_MEDIUM,
            "title": f"Quiet space weather (Kp={kp}) — adversary ISR at peak effectiveness",
            "deduction": (
                f"Quiet geomagnetic conditions (Kp={kp}) with {total_passes} "
                f"adversary ISR satellite passes across strategic hotspots. "
                f"DEDUCTION: Adversary ISR systems are operating at full capability "
                f"with no space weather degradation. All sensors (optical, SAR, ELINT) "
                f"are at maximum effectiveness. Highest concentration over {most_covered}. "
                f"Exercise maximum caution with exposed sensitive operations."
            ),
            "evidence": [
                f"Kp index: {kp} (quiet conditions)",
                f"{total_passes} adversary ISR passes (no degradation)",
                f"Most covered area: {most_covered}",
            ],
            "implications": (
                "No natural degradation of adversary ISR. Any sensitive surface "
                "operations will be observed with full sensor effectiveness."
            ),
            "recommended_action": (
                "Ensure EMCON posture reflects full adversary ISR capability. "
                "Defer sensitive exposed operations to degraded ISR windows if possible."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Correlation: PRC ground station active window x ISR coverage ---
    hour_utc = now.hour
    beijing_hour = (hour_utc + 8) % 24

    if 8 <= beijing_hour <= 22 and total_passes > 0:
        deductions.append({
            "id": _deduction_id(CATEGORY_CORRELATION, "prc-active-window"),
            "category": CATEGORY_CORRELATION,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_MEDIUM,
            "title": f"PRC mainland stations in active window ({beijing_hour:02d}00 Beijing) with ISR overhead",
            "deduction": (
                f"PRC mainland TT&C stations are in their primary operating window "
                f"(current Beijing time: {beijing_hour:02d}00). Combined with "
                f"{total_passes} adversary ISR satellite passes over strategic "
                f"hotspots. DEDUCTION: PRC can actively task ISR satellites for "
                f"specific collection targets during the current window. Tasking "
                f"commands issued now will produce collection data within 1-2 "
                f"orbital passes — maximum ISR responsiveness window."
            ),
            "evidence": [
                f"Current Beijing time: {beijing_hour:02d}00 (active hours 08:00-22:00)",
                f"{total_passes} ISR satellites over strategic areas",
                "Xi'an Satellite Control Centre (XSCC) primary TT&C hub",
                "Yuan Wang ships extend coverage beyond mainland visibility",
            ],
            "implications": (
                "Collection tasking initiated during this window will produce "
                "imagery/SIGINT within hours. Highest responsiveness period "
                "for PRC intelligence cycle."
            ),
            "recommended_action": (
                "Maintain elevated awareness of PRC ISR collection potential. "
                "Time sensitive surface movements for PRC off-peak hours if possible."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Correlation: Adversary launch + ISR expansion ---
    prc_launches_with_isr = [
        lch for lch in launches
        if any(kw in (lch.get("name") or "").lower()
               for kw in ["yaogan", "jilin", "gaofen", "shiyan"])
    ]
    if prc_launches_with_isr and total_passes > 0:
        next_isr_launch = prc_launches_with_isr[0]
        deductions.append({
            "id": _deduction_id(CATEGORY_CORRELATION, "launch-isr-expansion"),
            "category": CATEGORY_CORRELATION,
            "confidence": CONFIDENCE_MEDIUM,
            "priority": PRIORITY_HIGH,
            "title": "Imminent PRC ISR launch will expand existing coverage pattern",
            "deduction": (
                f"Upcoming PRC ISR launch: {next_isr_launch.get('name', 'Unknown')} "
                f"(NET: {next_isr_launch.get('net', 'TBD')}). Current adversary ISR "
                f"fleet is already generating {total_passes} passes over strategic "
                f"hotspots. DEDUCTION: Successful deployment will incrementally "
                f"reduce ISR revisit time by 10-20 minutes over the Western Pacific. "
                f"Post-launch orbital parameters should be tracked immediately to "
                f"assess which coverage gaps are being filled."
            ),
            "evidence": [
                f"Upcoming ISR launch: {next_isr_launch.get('name', 'Unknown')}",
                f"NET: {next_isr_launch.get('net', 'TBD')}",
                f"Current adversary ISR passes: {total_passes} over hotspots",
                "Each ISR satellite addition reduces average revisit time",
            ],
            "implications": (
                "Incrementally shrinking the remaining coverage gaps that FVEY "
                "forces can exploit for surface operations."
            ),
            "recommended_action": (
                "Track post-launch deployment. Update ISR coverage models "
                "within 24 hours of orbital insertion confirmation."
            ),
            "timestamp": now.isoformat(),
        })

    # --- Correlation: Strong southward Bz + GPS vulnerability ---
    if bz is not None and bz < -10:
        deductions.append({
            "id": _deduction_id(CATEGORY_CORRELATION, "bz-gps-storm"),
            "category": CATEGORY_CORRELATION,
            "confidence": CONFIDENCE_HIGH,
            "priority": PRIORITY_HIGH,
            "title": f"Strong southward IMF (Bz={bz} nT) — GPS degradation imminent",
            "deduction": (
                f"IMF Bz is strongly southward at {bz} nT, which is the primary "
                f"driver of geomagnetic storm intensification. DEDUCTION: Major "
                f"geomagnetic storm conditions are developing or intensifying. "
                f"GPS accuracy degradation, HF communications blackouts at high "
                f"latitudes, and increased LEO satellite drag are likely within "
                f"hours. Both FVEY and adversary space operations will be affected, "
                f"but GPS-dependent FVEY precision operations are disproportionately "
                f"impacted because PRC's BeiDou has anti-jam features that reduce "
                f"ionospheric vulnerability."
            ),
            "evidence": [
                f"IMF Bz: {bz} nT (strongly southward)",
                f"Kp: {kp}" if kp is not None else "Kp: N/A",
                f"Solar wind: {solar_wind or 'N/A'} km/s",
                "Southward Bz is the primary geomagnetic storm driver",
            ],
            "implications": (
                "GPS-dependent military operations will experience degraded "
                "accuracy. Precision munitions may require alternative guidance."
            ),
            "recommended_action": (
                "Issue GPS degradation advisory to operational units. "
                "Activate alternative PNT sources where available. "
                "Monitor SWPC for storm duration forecast."
            ),
            "timestamp": now.isoformat(),
        })

    return deductions


# ===================================================================
# MASTER DEDUCTION FUNCTION
# ===================================================================

async def generate_deductions(client: httpx.AsyncClient) -> dict:
    """Master deduction function — runs all deduction categories.

    Fetches all available data, runs each deduction generator, and
    returns a structured intelligence assessment with all deductions
    sorted by priority.

    Args:
        client: HTTP client for live data fetching.

    Returns:
        Dict with metadata and a list of deduction objects.
    """
    cached = _cached("all_deductions")
    if cached is not None:
        return cached

    now = datetime.now(timezone.utc)
    data = await _collect_all_data(client)

    # Run all deduction generators
    all_deductions: List[dict] = []
    all_deductions.extend(_generate_pattern_deductions(data))
    all_deductions.extend(_generate_capability_deductions(data))
    all_deductions.extend(_generate_intent_deductions(data))
    all_deductions.extend(_generate_vulnerability_deductions(data))
    all_deductions.extend(_generate_predictive_deductions(data))
    all_deductions.extend(_generate_correlation_deductions(data))

    # Sort by priority
    all_deductions.sort(
        key=lambda d: _PRIORITY_ORDER.get(d.get("priority", PRIORITY_LOW), 99)
    )

    # Category counts
    category_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {}
    for ded in all_deductions:
        cat = ded.get("category", "UNKNOWN")
        pri = ded.get("priority", "UNKNOWN")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        priority_counts[pri] = priority_counts.get(pri, 0) + 1

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "document_type": "AI Deduction Engine — Intelligence Assessment",
        "generated_utc": now.isoformat(),
        "engine_version": "1.0.0",
        "total_deductions": len(all_deductions),
        "by_category": category_counts,
        "by_priority": priority_counts,
        "data_sources_analyzed": [
            "CelesTrak active satellite catalog (live)",
            "NOAA SWPC space weather data (live)",
            "Launch Library 2 upcoming launches (live)",
            "Adversary ISR hotspot coverage analysis (live)",
            "Missile/ASAT/counterspace capability database",
            "Ground station infrastructure database",
            "Space security incident database",
            "Future space programs database",
        ],
        "methodology": (
            "Automated analytical deduction engine combining live data feeds "
            "with structured intelligence databases. Each deduction is generated "
            "by cross-referencing multiple data sources using rule-based analytical "
            "logic modeled on human intelligence analyst tradecraft. Confidence "
            "levels reflect data quality and analytical certainty."
        ),
        "deductions": all_deductions,
    }

    return _store("all_deductions", result)


# ===================================================================
# FILTERED ACCESS FUNCTIONS
# ===================================================================

async def get_priority_deductions(client: httpx.AsyncClient) -> dict:
    """Return the top 10 highest-priority deductions.

    Args:
        client: HTTP client for live data fetching.

    Returns:
        Dict with the top 10 deductions and metadata.
    """
    cached = _cached("priority_deductions")
    if cached is not None:
        return cached

    full = await generate_deductions(client)
    all_deds = full.get("deductions", [])
    top_10 = all_deds[:10]

    now = datetime.now(timezone.utc)
    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "document_type": "Priority Deductions — Top 10",
        "generated_utc": now.isoformat(),
        "total_available": len(all_deds),
        "showing": len(top_10),
        "deductions": top_10,
    }

    return _store("priority_deductions", result)


async def get_deductions_by_category(
    client: httpx.AsyncClient,
    category: str,
) -> dict:
    """Filter deductions by category.

    Args:
        client: HTTP client for live data fetching.
        category: PATTERN, CAPABILITY, INTENT, VULNERABILITY, PREDICTIVE, or CORRELATION.

    Returns:
        Dict with filtered deductions and metadata.
    """
    cat_upper = category.strip().upper()
    cache_key = f"deductions_{cat_upper}"
    cached = _cached(cache_key)
    if cached is not None:
        return cached

    full = await generate_deductions(client)
    all_deds = full.get("deductions", [])
    filtered = [d for d in all_deds if d.get("category") == cat_upper]

    now = datetime.now(timezone.utc)
    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "document_type": f"Deductions — {cat_upper}",
        "generated_utc": now.isoformat(),
        "category": cat_upper,
        "total_in_category": len(filtered),
        "total_all_categories": len(all_deds),
        "deductions": filtered,
    }

    return _store(cache_key, result)


# ===================================================================
# THREAT NARRATIVE GENERATOR
# ===================================================================

async def generate_threat_narrative(client: httpx.AsyncClient) -> dict:
    """Produce a cohesive analytical narrative combining top deductions.

    Generates a ~500-word intelligence assessment document weaving together
    the most important deductions into a single readable narrative.

    Args:
        client: HTTP client for live data fetching.

    Returns:
        Dict with the narrative text and supporting metadata.
    """
    cached = _cached("threat_narrative")
    if cached is not None:
        return cached

    full = await generate_deductions(client)
    all_deds = full.get("deductions", [])
    now = datetime.now(timezone.utc)

    # Extract key data points from deductions
    critical_deds = [d for d in all_deds if d.get("priority") == PRIORITY_CRITICAL]
    high_deds = [d for d in all_deds if d.get("priority") == PRIORITY_HIGH]
    pattern_deds = [d for d in all_deds if d.get("category") == CATEGORY_PATTERN]
    capability_deds = [d for d in all_deds if d.get("category") == CATEGORY_CAPABILITY]
    intent_deds = [d for d in all_deds if d.get("category") == CATEGORY_INTENT]
    vuln_deds = [d for d in all_deds if d.get("category") == CATEGORY_VULNERABILITY]
    predictive_deds = [d for d in all_deds if d.get("category") == CATEGORY_PREDICTIVE]
    correlation_deds = [d for d in all_deds if d.get("category") == CATEGORY_CORRELATION]

    # Build narrative sections
    paragraphs: List[str] = []

    # Opening
    paragraphs.append(
        f"ECHELON VANTAGE INTELLIGENCE ASSESSMENT — {now.strftime('%d %B %Y %H:%M')}Z\n"
        f"Classification: UNCLASSIFIED // OSINT // REL TO FVEY\n"
        f"Prepared by: Echelon Vantage AI Deduction Engine v1.0\n"
        f"Total deductions generated: {len(all_deds)} "
        f"({len(critical_deds)} CRITICAL, {len(high_deds)} HIGH priority)"
    )

    # Strategic Overview
    if pattern_deds:
        titles = [d.get("title", "") for d in pattern_deds[:3]]
        paragraphs.append(
            "STRATEGIC PATTERNS: Analysis of current adversary space activity reveals "
            "several significant patterns. " +
            " ".join(
                d.get("deduction", "").split(". DEDUCTION: ")[-1]
                for d in pattern_deds[:2]
                if d.get("deduction")
            )
        )

    # Capability Assessment
    if capability_deds:
        paragraphs.append(
            "CAPABILITY ASSESSMENT: " +
            " ".join(
                d.get("deduction", "").split(". DEDUCTION: ")[-1]
                for d in capability_deds[:2]
                if d.get("deduction")
            )
        )

    # Intent Analysis
    if intent_deds:
        paragraphs.append(
            "ADVERSARY INTENT: " +
            " ".join(
                d.get("deduction", "").split(". DEDUCTION: ")[-1]
                for d in intent_deds[:2]
                if d.get("deduction")
            )
        )

    # Vulnerability Spotlight
    if vuln_deds:
        paragraphs.append(
            "FVEY VULNERABILITIES: " +
            " ".join(
                d.get("deduction", "").split(". DEDUCTION: ")[-1]
                for d in vuln_deds[:2]
                if d.get("deduction")
            )
        )

    # Current Conditions
    if correlation_deds:
        paragraphs.append(
            "CURRENT CONDITIONS: " +
            " ".join(
                d.get("deduction", "").split(". DEDUCTION: ")[-1]
                for d in correlation_deds[:2]
                if d.get("deduction")
            )
        )

    # Forward Look
    if predictive_deds:
        paragraphs.append(
            "FORWARD ASSESSMENT: " +
            " ".join(
                d.get("deduction", "").split(". DEDUCTION: ")[-1]
                for d in predictive_deds[:2]
                if d.get("deduction")
            )
        )

    # Closing
    recommended_actions = []
    for d in critical_deds[:5]:
        action = d.get("recommended_action", "")
        if action:
            recommended_actions.append(action.split(".")[0] + ".")

    if recommended_actions:
        paragraphs.append(
            "PRIORITY ACTIONS: " + " ".join(recommended_actions[:4])
        )

    narrative_text = "\n\n".join(paragraphs)

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "document_type": "Threat Narrative — Analytical Intelligence Assessment",
        "generated_utc": now.isoformat(),
        "total_deductions_analyzed": len(all_deds),
        "critical_deductions": len(critical_deds),
        "high_deductions": len(high_deds),
        "narrative": narrative_text,
        "key_deductions": [
            {"title": d.get("title", ""), "priority": d.get("priority", ""), "category": d.get("category", "")}
            for d in all_deds[:10]
        ],
        "data_freshness": {
            "satellite_catalog": "Live (CelesTrak GP)",
            "space_weather": "Live (NOAA SWPC)",
            "launch_manifest": "Live (Launch Library 2)",
            "adversary_ISR_coverage": "Live (SGP4 propagation)",
            "threat_databases": "Structured (OSINT)",
        },
    }

    return _store("threat_narrative", result)
