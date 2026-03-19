"""
Space Conflict Wargame Simulator
Models adversary counter-space attack scenarios and assesses impact on FVEY capabilities.

Scenarios model real weapon systems against real satellite constellations using
open-source data on constellation sizes, ASAT capabilities, and reconstitution
timelines.

All analysis based on publicly available open-source intelligence:
- NASIC "Competing in Space" / "Ballistic and Cruise Missile Threat"
- Secure World Foundation "Global Counterspace Capabilities" (2023/2024)
- DIA "Challenges to Security in Space" (2022)
- CSIS Space Threat Assessment (annual)
- Congressional Research Service reports
- Todd Harrison / CSIS resilience analysis
- Published wargame findings (CSIS Taiwan, RAND escalation studies)

Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx

from data_sources.adversary_sats import (
    get_adversary_stats,
    get_fvey_satellites,
)
from data_sources.missile_intel import (
    get_by_country as get_missiles_by_country,
    get_missile_asat_data,
    get_threat_summary,
    TYPE_DA_ASAT,
    TYPE_CO_ORBITAL,
    TYPE_RPO,
    TYPE_EW,
    TYPE_DEW,
    TYPE_CYBER,
    STATUS_OPERATIONAL,
    STATUS_TESTED,
)

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache: Dict[str, dict] = {}
_WARGAME_TTL = 120  # 2 minutes


def _cached(key: str) -> Optional[dict]:
    cached = _cache.get(key)
    if cached and (time.time() - cached["ts"]) < _WARGAME_TTL:
        return cached["data"]
    return None


def _store(key: str, data: dict) -> dict:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# ---------------------------------------------------------------------------
# FVEY constellation reference data (open-source known sizes)
# Updated from USSF, SMAD, CRS, and public satellite databases
# ---------------------------------------------------------------------------

_FVEY_CONSTELLATIONS = {
    "GPS": {
        "full_name": "Global Positioning System (Block II/IIF/III)",
        "operator": "US Space Force / 2nd SOPS",
        "orbit": "MEO (~20,200 km)",
        "active_satellites": 31,
        "minimum_operational": 24,
        "spares_on_orbit": 4,
        "replacement_cost_per_sat_usd": "500M",
        "manufacturing_time_months": 36,
        "launch_to_operational_months": 3,
        "mission": "Position, Navigation, Timing for military and civilian users worldwide",
        "criticality": "CRITICAL — Foundation of modern warfare and civilian infrastructure",
    },
    "SBIRS": {
        "full_name": "Space Based Infrared System",
        "operator": "US Space Force / SBIRS Operations",
        "orbit": "GEO + HEO",
        "active_satellites": 6,
        "minimum_operational": 4,
        "spares_on_orbit": 0,
        "replacement_cost_per_sat_usd": "2.5B",
        "manufacturing_time_months": 60,
        "launch_to_operational_months": 6,
        "mission": "Missile launch detection and tracking; nuclear detonation detection",
        "criticality": "CRITICAL — Strategic early warning; loss could create nuclear escalation ambiguity",
    },
    "WGS": {
        "full_name": "Wideband Global SATCOM",
        "operator": "US Space Force / 4th SOPS",
        "orbit": "GEO (~35,786 km)",
        "active_satellites": 10,
        "minimum_operational": 6,
        "spares_on_orbit": 1,
        "replacement_cost_per_sat_usd": "500M",
        "manufacturing_time_months": 36,
        "launch_to_operational_months": 4,
        "mission": "High-capacity wideband communications for deployed forces",
        "criticality": "HIGH — Primary MILSATCOM for broadband military communications",
    },
    "AEHF": {
        "full_name": "Advanced Extremely High Frequency",
        "operator": "US Space Force / 4th SOPS",
        "orbit": "GEO (~35,786 km)",
        "active_satellites": 6,
        "minimum_operational": 4,
        "spares_on_orbit": 0,
        "replacement_cost_per_sat_usd": "3.5B",
        "manufacturing_time_months": 60,
        "launch_to_operational_months": 6,
        "mission": "Protected nuclear command and control communications (NC3)",
        "criticality": "CRITICAL — NC3 backbone; loss threatens nuclear C2 continuity",
    },
    "MUOS": {
        "full_name": "Mobile User Objective System",
        "operator": "US Navy / SPAWAR",
        "orbit": "GEO (~35,786 km)",
        "active_satellites": 5,
        "minimum_operational": 4,
        "spares_on_orbit": 1,
        "replacement_cost_per_sat_usd": "1.7B",
        "manufacturing_time_months": 48,
        "launch_to_operational_months": 4,
        "mission": "Narrowband tactical SATCOM for mobile users",
        "criticality": "HIGH — Tactical communications for deployed forces",
    },
    "GSSAP": {
        "full_name": "Geosynchronous Space Situational Awareness Program",
        "operator": "US Space Force",
        "orbit": "Near-GEO",
        "active_satellites": 6,
        "minimum_operational": 2,
        "spares_on_orbit": 0,
        "replacement_cost_per_sat_usd": "500M",
        "manufacturing_time_months": 24,
        "launch_to_operational_months": 2,
        "mission": "GEO belt surveillance and RPO characterization",
        "criticality": "HIGH — Only persistent GEO SSA capability",
    },
    "SKYNET": {
        "full_name": "Skynet Military SATCOM (UK)",
        "operator": "UK MOD / Airbus Defence",
        "orbit": "GEO",
        "active_satellites": 4,
        "minimum_operational": 3,
        "spares_on_orbit": 0,
        "replacement_cost_per_sat_usd": "400M",
        "manufacturing_time_months": 48,
        "launch_to_operational_months": 4,
        "mission": "UK military beyond-line-of-sight communications",
        "criticality": "HIGH — UK sovereign MILSATCOM; critical for deployed UK forces",
    },
    "NRO_ISR": {
        "full_name": "National Reconnaissance Office ISR Constellation",
        "operator": "NRO / US Intelligence Community",
        "orbit": "LEO (various)",
        "active_satellites": 15,
        "minimum_operational": 8,
        "spares_on_orbit": 0,
        "replacement_cost_per_sat_usd": "5B",
        "manufacturing_time_months": 72,
        "launch_to_operational_months": 6,
        "mission": "Strategic imagery and signals intelligence",
        "criticality": "CRITICAL — Primary strategic ISR for national decision-making",
    },
    "STARLINK_MIL": {
        "full_name": "Starlink (Starshield Military Variant)",
        "operator": "SpaceX / US DoD",
        "orbit": "LEO (~550 km)",
        "active_satellites": 6000,
        "minimum_operational": 2000,
        "spares_on_orbit": 0,
        "replacement_cost_per_sat_usd": "0.5M",
        "manufacturing_time_months": 1,
        "launch_to_operational_months": 1,
        "mission": "Resilient broadband communications augmentation",
        "criticality": "MEDIUM — Augmentation; not primary but increasingly relied upon",
    },
}


# ---------------------------------------------------------------------------
# Scenario definitions — the seven wargames
# ---------------------------------------------------------------------------

def _scenario_prc_asat_vs_gps() -> dict:
    """Scenario 1: PRC DA-ASAT strike on GPS constellation."""
    prc_asat = get_missiles_by_country("PRC")
    da_asat_systems = [
        s for s in prc_asat
        if s["type"] == TYPE_DA_ASAT and s.get("status") in (STATUS_OPERATIONAL, STATUS_TESTED)
    ]

    # Only DN-2 and DN-3 can reach MEO (~20,200 km)
    meo_capable = [s for s in da_asat_systems if (s.get("max_altitude_km") or 0) >= 20000]
    leo_only = [s for s in da_asat_systems if (s.get("max_altitude_km") or 0) < 20000]

    gps = _FVEY_CONSTELLATIONS["GPS"]

    # Engagement capacity: each system = ~1-2 simultaneous engagements
    # (limited by KKV production, fire control, and launch pads)
    engagement_capacity = len(meo_capable) * 2  # 2 engagements per system assessed

    # PRC would need to expend its limited MEO-capable ASAT inventory
    sats_at_risk = min(engagement_capacity + 2, 8)  # Assume some operational margin

    degradation = round((sats_at_risk / gps["active_satellites"]) * 100, 0)

    # Debris from MEO ASAT — devastating long-term
    fragments = sats_at_risk * 2500  # Each GPS sat is large, high-energy intercept

    return {
        "scenario_id": "prc_asat_vs_gps",
        "title": "PRC DA-ASAT Strike on GPS Constellation",
        "classification": "UNCLASSIFIED // OSINT",
        "attacker": "PRC",
        "target": "US GPS Block IIF/III",
        "target_constellation": gps,
        "weapon_systems": [s["name"] for s in meo_capable],
        "weapon_details": (
            f"PRC has {len(meo_capable)} tested/operational DA-ASAT systems assessed capable "
            f"of reaching MEO altitudes: {', '.join(s['name'] for s in meo_capable)}. "
            f"Additionally, {len(leo_only)} LEO-only systems ({', '.join(s['name'] for s in leo_only)}) "
            f"cannot reach GPS orbit but could threaten LEO PNT augmentation."
        ),
        "engagement_capacity": engagement_capacity,
        "current_gps_constellation": gps["active_satellites"],
        "minimum_operational": gps["minimum_operational"],
        "satellites_at_risk": sats_at_risk,
        "impact": {
            "pnt_degradation_percent": degradation,
            "coverage_gaps": [
                "Western Pacific (worst affected — closest to PRC engagement window)",
                "Indian Ocean (secondary gap from orbital geometry)",
                "Global timing accuracy degraded across all regions",
            ],
            "military_impact": (
                f"Loss of {sats_at_risk} GPS satellites would degrade constellation from "
                f"{gps['active_satellites']} to {gps['active_satellites'] - sats_at_risk} — "
                f"below minimum operational of {gps['minimum_operational']} if maximum engagement "
                f"achieved. Precision-guided munitions lose accuracy (JDAM CEP increases from "
                f"~5m to ~30m+). Network-centric warfare degrades. Blue-force tracking unreliable. "
                f"Time-sensitive targeting cycles lengthen. Special operations navigation compromised."
            ),
            "civilian_impact": (
                "GPS outages across Indo-Pacific affecting commercial aviation (WAAS/SBAS degraded), "
                "maritime shipping navigation, cellular network timing synchronization, financial "
                "transaction timestamping (NYSE, CME require GPS timing), power grid frequency "
                "synchronization, emergency services positioning. Economic impact estimated "
                "USD 1B+ per day of GPS degradation."
            ),
        },
        "debris": {
            "fragments_estimated": fragments,
            "orbits_affected": ["MEO (20,200 km band)"],
            "orbital_lifetime": "Centuries to millennia (MEO debris does not deorbit naturally)",
            "kessler_risk": (
                "MODERATE — MEO is less congested than LEO but debris would persist for "
                "centuries. GPS, GLONASS, BeiDou, and Galileo all share the MEO band. "
                "PRC's own BeiDou constellation would be threatened by debris from its own attack."
            ),
            "collateral_damage": (
                f"An estimated {fragments} fragments would threaten all MEO assets: "
                f"BeiDou (PRC's own navigation — 35 sats), GLONASS (24 sats), "
                f"Galileo (EU — 28 sats). Adversary's own PNT constellation at equal risk."
            ),
        },
        "fvey_response_options": [
            "Activate backup PNT: eLoran (if operational), Iridium STL, UK eLoran",
            "Shift to LEO PNT augmentation (Xona Space, TrustPoint — if deployed)",
            "Increase reliance on inertial navigation systems for precision strike",
            "Responsive launch of GPS III replacement satellites (12-24 month timeline)",
            "Activate GPS ground spares for accelerated integration and launch",
            "Diplomatic/deterrence: declare attack on GPS as attack on critical infrastructure of all nations",
            "Retaliatory counter-space operations (SM-3 vs BeiDou, if escalation accepted)",
            "Cyber response against PRC space ground segment",
        ],
        "reconstitution_timeline": (
            "12-24 months for partial constellation restoration (GPS III production line active). "
            "Full restoration to 31 satellites: 36-48 months. SpaceX Falcon 9 can launch GPS III "
            "but mission assurance and testing requirements limit surge rate to ~4 per year. "
            "Ground spares: 2-3 GPS satellites currently in various stages of readiness."
        ),
        "deterrence_assessment": (
            "Current deterrence posture: MODERATE. PRC calculates acceptable cost-benefit in "
            "a Taiwan scenario where GPS degradation buys operational advantage in the Western "
            "Pacific. However, PRC's own BeiDou would be threatened by MEO debris, creating "
            "mutual vulnerability. PRC may prefer EW (GPS jamming) over kinetic ASAT for "
            "PNT denial — achieving similar effect without debris and escalation."
        ),
        "historical_precedent": (
            "No kinetic attack on a navigation constellation has occurred. The 2007 PRC ASAT "
            "test (FY-1C, LEO) created 3,500+ debris fragments still in orbit. A MEO attack "
            "would be orders of magnitude worse for long-term space sustainability."
        ),
    }


def _scenario_russia_nudol_vs_isr() -> dict:
    """Scenario 2: Russia Nudol DA-ASAT vs FVEY LEO ISR satellites."""
    russia_asat = get_missiles_by_country("Russia")
    da_asat = [
        s for s in russia_asat
        if s["type"] == TYPE_DA_ASAT and s.get("status") in (STATUS_OPERATIONAL, STATUS_TESTED)
    ]
    nudol_systems = [s for s in da_asat if "nudol" in s["name"].lower() or "1408" in s["name"]]

    nro = _FVEY_CONSTELLATIONS["NRO_ISR"]

    # Nudol can reach ~800 km — most NRO LEO assets are within this range
    engagement_capacity = 3  # Estimated simultaneous from Plesetsk
    sats_at_risk = min(engagement_capacity + 1, 6)

    return {
        "scenario_id": "russia_nudol_vs_isr",
        "title": "Russia Nudol DA-ASAT Strike on FVEY LEO ISR Satellites",
        "classification": "UNCLASSIFIED // OSINT",
        "attacker": "Russia",
        "target": "FVEY LEO ISR (NRO + commercial)",
        "target_constellation": nro,
        "weapon_systems": [s["name"] for s in nudol_systems] if nudol_systems else ["Nudol (PL-19 / A-235)"],
        "weapon_details": (
            f"Russia has {len(da_asat)} DA-ASAT systems, including the Nudol which has been "
            f"tested 10+ times from Plesetsk and conducted the destructive Cosmos 1408 test "
            f"in November 2021. The system can engage targets up to ~800 km altitude, putting "
            f"most FVEY LEO ISR assets within range."
        ),
        "engagement_capacity": engagement_capacity,
        "current_isr_constellation": nro["active_satellites"],
        "satellites_at_risk": sats_at_risk,
        "impact": {
            "isr_degradation_percent": round((sats_at_risk / nro["active_satellites"]) * 100, 0),
            "coverage_gaps": [
                "European theater (primary concern for NATO)",
                "Arctic region (Russian submarine bastion monitoring lost)",
                "Global strategic ISR revisit rate severely degraded",
            ],
            "military_impact": (
                f"Loss of {sats_at_risk} NRO ISR satellites would create critical intelligence "
                f"gaps. Strategic imagery collection capacity reduced by ~{round((sats_at_risk / nro['active_satellites']) * 100)}%. "
                f"Real-time situational awareness for combatant commanders degraded. Targeting "
                f"data for precision strike becomes dependent on other sources (aircraft, UAV, "
                f"commercial imagery). SIGINT collection from space significantly reduced."
            ),
            "civilian_impact": (
                "Limited direct civilian impact but degraded national intelligence "
                "reduces strategic warning capability for all allies."
            ),
        },
        "debris": {
            "fragments_estimated": sats_at_risk * 2000,
            "orbits_affected": ["LEO (400-800 km) — the most congested orbital regime"],
            "orbital_lifetime": "5-25 years depending on altitude",
            "kessler_risk": (
                "HIGH — LEO is the most congested regime. The 2021 Cosmos 1408 test created "
                "1,500+ fragments in this band. Additional debris from ISR satellite destruction "
                "would compound the problem, threatening ISS, CSS, Starlink, and all LEO assets."
            ),
        },
        "fvey_response_options": [
            "Shift to commercial ISR augmentation (Maxar WorldView, Planet, BlackSky)",
            "Deploy airborne ISR (U-2, Global Hawk, MQ-9) to compensate for satellite loss",
            "Accelerate NRO proliferated architecture deployment",
            "Activate allied ISR sharing (UK, AU, CA satellite imagery)",
            "Retaliatory counter-space operations against Russian ISR constellation",
            "Cyber operations against Russian ground-based SSA to degrade their targeting",
        ],
        "reconstitution_timeline": (
            "NRO exquisite satellites: 48-72 months per replacement (long manufacturing). "
            "Commercial augmentation: weeks to months for tasking existing commercial sats. "
            "SDA proliferated LEO ISR: 12-18 months to deploy initial capability. "
            "NRO proliferated architecture (smaller, numerous sats): 18-24 months for first wave."
        ),
        "deterrence_assessment": (
            "Current deterrence posture: MODERATE-HIGH. Russia demonstrated willingness to "
            "conduct destructive ASAT in 2021 (Cosmos 1408) despite international condemnation. "
            "In a NATO confrontation, Russia may calculate ISR denial is worth the debris cost "
            "and escalation risk. The asymmetry is that Russia has less to lose in LEO (fewer "
            "military LEO assets) while FVEY is more dependent on LEO ISR."
        ),
    }


def _scenario_prc_ew_campaign() -> dict:
    """Scenario 3: PRC electronic warfare campaign against GPS/SATCOM."""
    prc_systems = get_missiles_by_country("PRC")
    ew_systems = [
        s for s in prc_systems
        if s["type"] == TYPE_EW and s.get("status") in (STATUS_OPERATIONAL, STATUS_TESTED)
    ]

    return {
        "scenario_id": "prc_ew_campaign",
        "title": "PRC Electronic Warfare Campaign — GPS Jamming and SATCOM Denial",
        "classification": "UNCLASSIFIED // OSINT",
        "attacker": "PRC",
        "target": "FVEY GPS signals and SATCOM links in Western Pacific",
        "weapon_systems": [s["name"] for s in ew_systems],
        "weapon_details": (
            f"PRC operates {len(ew_systems)} assessed EW systems capable of GPS jamming/spoofing "
            f"and SATCOM uplink interference. PLA Information Support Force (formerly SSF) "
            f"operates dedicated space EW units. Systems include ground-based GPS jammers, "
            f"mobile SATCOM uplink jammers, and shipborne EW platforms deployed on PLA Navy vessels. "
            f"GPS spoofing has been detected near PRC military installations in the South China Sea."
        ),
        "affected_area": {
            "primary": "Taiwan Strait, South China Sea, East China Sea",
            "secondary": "Western Pacific from Guam to Japan",
            "radius_km": 2000,
        },
        "impact": {
            "gps_effect": (
                "GPS signals jammed/spoofed across the Taiwan Strait and South China Sea. "
                "Military GPS receivers without M-code vulnerable to denial. Civilian GPS "
                "completely denied in the operational area. PNT accuracy degrades from meters "
                "to kilometers for unprotected receivers."
            ),
            "satcom_effect": (
                "Military SATCOM (WGS, MUOS UHF) uplinks jammed in the theater. Protected "
                "AEHF EHF links more resistant but may experience degradation. Commercial "
                "SATCOM (Starlink, Intelsat) disrupted for ground terminals in the affected area."
            ),
            "military_impact": (
                "Precision-guided munitions lose accuracy (JDAM, Excalibur, GMLRS affected). "
                "Blue-force tracking disrupted — fratricide risk increases. Naval navigation "
                "degrades to inertial/celestial backup. Time-sensitive targeting cycles lengthened. "
                "UAV operations disrupted (GPS-dependent navigation). Submarine communication "
                "windows disrupted."
            ),
            "civilian_impact": (
                "Commercial aviation GPS navigation denied — aircraft in Taiwan Strait must "
                "use backup navigation. Maritime shipping GPS denied — risk of collision in "
                "congested waterways. Cellular network timing disrupted. Financial transactions "
                "requiring GPS timestamps affected."
            ),
            "pnt_degradation_percent": 85,
            "duration": "Days to weeks (sustained campaign as long as EW assets operational)",
        },
        "debris": {
            "fragments_estimated": 0,
            "kessler_risk": "NONE — EW is non-kinetic; no debris generated",
        },
        "advantages_for_attacker": [
            "Non-kinetic: reversible effects, no debris, lower escalation threshold",
            "Deniable: attribution of jamming is more ambiguous than kinetic ASAT",
            "Cheap: EW systems cost fraction of DA-ASAT or satellite programs",
            "Persistent: can maintain jamming continuously unlike one-shot ASAT",
            "PRC maintains own PNT via BeiDou (not affected by GPS denial)",
        ],
        "fvey_response_options": [
            "Activate GPS M-code on all military receivers (anti-jam military signal)",
            "Shift to alternative PNT sources (Iridium STL, eLoran if available)",
            "Deploy anti-jam antenna systems (CRPA — Controlled Reception Pattern Antenna)",
            "Use inertial navigation systems with GPS-denied procedures",
            "Kinetic strike on PRC ground-based EW systems (if escalation acceptable)",
            "Cyber attack on PRC EW command and control networks",
            "Deploy EW counter-countermeasures (frequency hopping, spread spectrum)",
            "Relocate SATCOM ground terminals outside jammed area",
        ],
        "reconstitution_timeline": (
            "EW effects are reversible — PNT and SATCOM restore immediately when jamming "
            "ceases. However, if PRC maintains sustained EW campaign, degradation persists "
            "until FVEY can suppress or destroy the EW sources. M-code GPS III provides "
            "inherent anti-jam but is not yet fully deployed across all receivers."
        ),
        "deterrence_assessment": (
            "Current deterrence posture: LOW for EW. GPS jamming is routine in peacetime "
            "(PRC SCS, Russia Baltic/Ukraine). The low escalation threshold makes EW "
            "the most likely first-use counter-space capability in any conflict. PRC "
            "can deny GPS in the Taiwan Strait with minimal risk of kinetic retaliation. "
            "FVEY must assume GPS denial as the baseline operating condition in any "
            "Western Pacific contingency."
        ),
    }


def _scenario_co_orbital_vs_geo() -> dict:
    """Scenario 4: PRC co-orbital ASAT / towing attack on FVEY GEO assets."""
    prc_systems = get_missiles_by_country("PRC")
    co_orbital = [
        s for s in prc_systems
        if s["type"] in (TYPE_CO_ORBITAL, TYPE_RPO)
        and s.get("status") in (STATUS_OPERATIONAL, STATUS_TESTED)
    ]

    wgs = _FVEY_CONSTELLATIONS["WGS"]
    aehf = _FVEY_CONSTELLATIONS["AEHF"]

    return {
        "scenario_id": "co_orbital_vs_geo",
        "title": "PRC Co-Orbital ASAT / Towing Attack on FVEY GEO Communications",
        "classification": "UNCLASSIFIED // OSINT",
        "attacker": "PRC",
        "target": "FVEY GEO MILSATCOM (WGS, AEHF, Skynet)",
        "weapon_systems": [s["name"] for s in co_orbital],
        "weapon_details": (
            f"PRC has {len(co_orbital)} demonstrated co-orbital/RPO systems. SJ-21 (Shijian-21) "
            f"physically towed a defunct BeiDou satellite in GEO (Jan 2022) — the first confirmed "
            f"instance of one satellite relocating another in GEO. SJ-17 demonstrated robotic arm "
            f"operations in GEO. Shijian series microsatellites conducted RPO in both LEO and GEO. "
            f"These systems could approach, grapple, disable, or tow FVEY GEO satellites to "
            f"graveyard orbits."
        ),
        "engagement_capacity": len(co_orbital),
        "targets_at_risk": {
            "WGS": {"constellation": wgs["active_satellites"], "at_risk": min(len(co_orbital), 3)},
            "AEHF": {"constellation": aehf["active_satellites"], "at_risk": min(len(co_orbital), 2)},
            "Skynet": {"constellation": 4, "at_risk": 1},
        },
        "impact": {
            "comms_degradation_percent": 40,
            "military_impact": (
                f"Loss of 3 WGS satellites (from {wgs['active_satellites']}) would reduce wideband "
                f"MILSATCOM capacity by ~30%. Loss of 2 AEHF satellites would critically degrade "
                f"nuclear command and control (NC3) communications — the most strategically "
                f"dangerous consequence. Loss of Skynet would deny UK sovereign MILSATCOM. "
                f"Combined SATCOM loss would force reliance on commercial systems (Starlink, "
                f"commercial VSAT) which are unprotected and could be subsequently targeted."
            ),
            "civilian_impact": (
                "Limited direct civilian impact from military SATCOM loss. However, if attack "
                "extends to commercial GEO SATCOM (SES, Intelsat), broadband and broadcast "
                "services across the Pacific would be disrupted."
            ),
            "nuclear_c2_risk": (
                "CRITICAL: AEHF satellites provide the primary protected communications link "
                "between national command authority and nuclear forces. Loss of AEHF creates "
                "ambiguity in nuclear command and control. This could be interpreted as a "
                "precursor to nuclear first strike, triggering nuclear escalation."
            ),
        },
        "debris": {
            "fragments_estimated": 0,
            "kessler_risk": (
                "MINIMAL if towing attack — satellites relocated intact to graveyard orbit. "
                "However, a grappling failure or intentional breakup could create GEO debris "
                "with ~million-year orbital lifetime."
            ),
        },
        "unique_characteristics": [
            "No debris: towing attack is 'clean' — avoids international condemnation",
            "Slow: co-orbital approach takes days to weeks — detectable but difficult to counter",
            "Reversible in theory: towed satellite could potentially be retrieved",
            "Attribution ambiguous: 'debris removal demonstration' provides cover story",
            "Scalable: multiple SJ-21-type sats could target multiple GEO assets simultaneously",
        ],
        "fvey_response_options": [
            "Detect and track approaching co-orbital ASAT using GSSAP surveillance",
            "Maneuver target GEO satellite to evade approaching threat (limited fuel)",
            "Electronic warfare against co-orbital ASAT command links",
            "Cyber attack on PRC ground control for co-orbital ASAT",
            "Deploy defensive 'bodyguard' satellites near high-value GEO assets",
            "Kinetic response against approaching ASAT (if rules of engagement permit)",
            "Shift to commercial SATCOM and Starlink for communications continuity",
            "Diplomatic declaration that interference with GEO MILSATCOM is an act of war",
        ],
        "reconstitution_timeline": (
            f"WGS replacement: {wgs['manufacturing_time_months']} months manufacturing + "
            f"{wgs['launch_to_operational_months']} months to operational. "
            f"AEHF replacement: {aehf['manufacturing_time_months']} months — no rapid path. "
            f"Commercial augmentation: weeks (Starlink, Intelsat). "
            f"Protected Tactical SATCOM (PTS): 24-36 months to first capability."
        ),
        "deterrence_assessment": (
            "Current deterrence posture: LOW. PRC has demonstrated the capability (SJ-21) and "
            "the co-orbital approach offers an attractive escalation option — it is less "
            "provocative than kinetic ASAT (no debris), more ambiguous (could claim debris "
            "removal), and harder to defend against (no kinetic intercept option without "
            "creating debris near own GEO assets). FVEY lacks deployed counter-co-orbital "
            "defenses."
        ),
    }


def _scenario_cyber_vs_ground() -> dict:
    """Scenario 5: Cyber attack on FVEY satellite ground segment."""
    prc_cyber = [
        s for s in get_missiles_by_country("PRC")
        if s["type"] == TYPE_CYBER
    ]
    russia_cyber = [
        s for s in get_missiles_by_country("Russia")
        if s["type"] == TYPE_CYBER
    ]

    return {
        "scenario_id": "cyber_vs_ground",
        "title": "State-Sponsored Cyber Attack on FVEY Satellite Ground Infrastructure",
        "classification": "UNCLASSIFIED // OSINT",
        "attacker": "PRC/Russia (joint or independent)",
        "target": "FVEY satellite ground control and data processing infrastructure",
        "weapon_systems": (
            [s["name"] for s in prc_cyber] + [s["name"] for s in russia_cyber]
        ),
        "weapon_details": (
            "Both PRC and Russia operate world-class offensive cyber capabilities targeting "
            "space infrastructure. Russia GRU (Sandworm/Unit 74455) conducted the Viasat "
            "KA-SAT AcidRain wiper attack (Feb 2022). PRC APT groups (APT10, APT41, Thrip) "
            "have targeted satellite operators and aerospace companies. Ground segment cyber "
            "attack achieves effects equivalent to ASAT without debris or kinetic escalation."
        ),
        "attack_vectors": [
            "Wiper malware targeting satellite ground control systems (Viasat precedent)",
            "Supply chain compromise of satellite operations software",
            "Compromise of TT&C links to inject false commands",
            "Data exfiltration from satellite data processing centers",
            "DDoS against satellite operator web portals and APIs",
            "Insider threat / social engineering at ground station facilities",
        ],
        "targets_at_risk": [
            "Schriever SFB — GPS Master Control Station",
            "SBIRS ground processing — missile warning data",
            "WGS/AEHF ground control — MILSATCOM management",
            "NRO ground data processing — ISR exploitation",
            "Commercial SATCOM operators (Viasat, SES, Intelsat ground infra)",
            "Allied ground stations (UK RAF Oakhanger, AU Pine Gap data links)",
        ],
        "impact": {
            "gps_risk": (
                "Compromise of GPS Master Control at Schriever could corrupt GPS navigation "
                "messages, degrade accuracy, or deny the ability to upload corrections. "
                "GPS satellites can operate autonomously for ~14 days before accuracy degrades "
                "significantly, but corrupted uploads could cause immediate issues."
            ),
            "early_warning_risk": (
                "Compromise of SBIRS ground processing could suppress or corrupt missile "
                "warning data — the most strategically dangerous cyber target. False "
                "negatives (suppressed warnings) could mask a real attack. False positives "
                "could trigger nuclear escalation."
            ),
            "satcom_risk": (
                "Wiper attack on MILSATCOM ground control (Viasat precedent) could disable "
                "military communications globally for hours to days. Recovery from the "
                "Viasat attack took weeks for full service restoration."
            ),
            "military_impact": (
                "Simultaneous cyber attack on multiple ground segments could create a "
                "'day without space' — temporary denial of GPS, SATCOM, ISR, and early "
                "warning simultaneously. Even partial success would severely degrade C2."
            ),
            "civilian_impact": (
                "Commercial SATCOM disruption (Viasat precedent affected 5,800 German wind "
                "turbines and thousands of broadband users). GPS ground segment compromise "
                "could affect civilian GPS accuracy globally."
            ),
        },
        "debris": {
            "fragments_estimated": 0,
            "kessler_risk": "NONE — cyber attack generates no physical debris",
        },
        "advantages_for_attacker": [
            "Zero debris — no environmental consequences",
            "Deniable — attribution takes weeks to months",
            "Reversible — systems can be restored (eventually)",
            "Low cost — cyber tools vs multi-billion-dollar ASAT programs",
            "Scalable — can target one system or all simultaneously",
            "Precedent exists — Viasat attack demonstrated viability",
            "Pre-positioning possible — implants placed years before activation",
        ],
        "fvey_response_options": [
            "Zero-trust architecture for all satellite ground networks",
            "Air-gapped backup control systems for critical satellites (GPS, SBIRS)",
            "Redundant ground control at geographically dispersed locations",
            "Automated satellite autonomous operations mode if ground link lost",
            "Offensive cyber response against adversary space ground infrastructure",
            "Attribution and diplomatic/economic response",
            "Incident response and system recovery from backups",
        ],
        "reconstitution_timeline": (
            "Hours to weeks depending on attack severity. Viasat recovery took ~2 weeks "
            "for partial and months for full. If backup systems are pre-positioned and "
            "tested, core capability can be restored in hours. If backups are compromised "
            "(supply chain attack), recovery extends to weeks or months."
        ),
        "deterrence_assessment": (
            "Current deterrence posture: VERY LOW. Cyber attacks against space ground "
            "segments are the most likely counter-space action in any conflict. The Viasat "
            "precedent demonstrated viability and the relatively limited international "
            "response sets a permissive precedent. Adversaries likely have pre-positioned "
            "access in FVEY space networks. The low cost, deniability, and reversibility "
            "make this the most attractive first-move option."
        ),
    }


def _scenario_full_spectrum() -> dict:
    """Scenario 6: Full spectrum counter-space attack — worst case."""
    all_systems = get_missile_asat_data()
    prc_count = len([s for s in all_systems if s["country"] == "PRC"])
    russia_count = len([s for s in all_systems if s["country"] == "Russia"])

    total_asat = len([
        s for s in all_systems
        if s["type"] in (TYPE_DA_ASAT, TYPE_CO_ORBITAL, TYPE_RPO)
        and s.get("status") in (STATUS_OPERATIONAL, STATUS_TESTED)
    ])

    total_ew = len([
        s for s in all_systems
        if s["type"] == TYPE_EW and s.get("status") in (STATUS_OPERATIONAL, STATUS_TESTED)
    ])

    return {
        "scenario_id": "full_spectrum",
        "title": "Full Spectrum Counter-Space Attack — Combined PRC/Russia",
        "classification": "UNCLASSIFIED // OSINT",
        "attacker": "PRC + Russia (coordinated or concurrent)",
        "target": "All FVEY space capabilities",
        "description": (
            "Worst-case scenario: coordinated PRC and Russian counter-space attack across "
            "all domains simultaneously. This represents the maximum threat to FVEY space "
            "architecture and is assessed as unlikely except in a major-power conflict "
            "where space denial is considered strategically necessary."
        ),
        "attack_phases": [
            {
                "phase": "Phase 0: Pre-Conflict (Weeks to Months Before)",
                "actions": [
                    "Cyber pre-positioning: implants in FVEY satellite ground networks activated",
                    "Inspector satellite repositioning near high-value FVEY GEO assets",
                    "GPS spoofing testing in contested areas (South China Sea, Baltic)",
                    "Reconnaissance of FVEY satellite orbital parameters and maneuver patterns",
                ],
            },
            {
                "phase": "Phase 1: Opening Salvo (H-Hour)",
                "actions": [
                    "Cyber: AcidRain-type wiper against commercial SATCOM ground infrastructure",
                    "EW: GPS jamming across Western Pacific and Baltic simultaneously",
                    "DEW: Ground-based laser dazzling of ISR satellites over Taiwan Strait and Baltic",
                    "Co-orbital: SJ-21/SJ-17 begin approach to WGS and AEHF GEO satellites",
                ],
            },
            {
                "phase": "Phase 2: Kinetic Escalation (H+6 to H+24)",
                "actions": [
                    "DA-ASAT: PRC SC-19 targets 2-3 LEO ISR satellites (NROL series)",
                    "DA-ASAT: Russia Nudol targets 2-3 LEO ISR satellites from Plesetsk",
                    "Co-orbital: PRC SJ-21 grapples/tows a WGS satellite to graveyard orbit",
                    "EW: SATCOM uplink jamming against all military frequency bands",
                ],
            },
            {
                "phase": "Phase 3: Sustained Denial (Days to Weeks)",
                "actions": [
                    "Continued GPS/SATCOM jamming across contested theaters",
                    "Cyber attacks on GPS Master Control to degrade constellation accuracy",
                    "Co-orbital operations against remaining high-value GEO assets",
                    "Ground-based laser persistent harassment of surviving ISR satellites",
                    "Cyber exploitation of degraded FVEY C2 networks",
                ],
            },
        ],
        "combined_impact": {
            "satellites_destroyed_kinetic": "4-8 (DA-ASAT engagements by PRC + Russia)",
            "satellites_disabled_co_orbital": "2-4 (GEO towing/grappling attacks)",
            "satellites_blinded_dew": "3-6 (temporarily blinded ISR sensors)",
            "ground_segments_compromised": "3-5 major facilities degraded",
            "gps_degradation_percent": 60,
            "satcom_degradation_percent": 50,
            "isr_degradation_percent": 70,
            "early_warning_degradation_percent": 30,
            "overall_space_capability_loss_percent": 55,
        },
        "strategic_consequences": (
            "A full-spectrum attack would effectively create a 'day without space' for FVEY "
            "forces — severely degrading precision strike, C2, ISR, PNT, and early warning "
            "simultaneously. This would: (1) Create intelligence blackout in contested theaters, "
            "(2) Degrade precision-guided munition accuracy, (3) Disrupt nuclear command and "
            "control (SBIRS/AEHF), (4) Force reliance on pre-GPS era navigation and communications, "
            "(5) Create nuclear escalation ambiguity from loss of early warning, "
            "(6) Generate debris threatening all nations' space assets for decades."
        ),
        "debris_total": {
            "fragments_estimated": "20,000-50,000 trackable (MEO + LEO)",
            "kessler_risk": "HIGH — multiple debris events in congested LEO and MEO bands",
            "long_term": "Portions of LEO and MEO may become unusable for 50-100 years",
        },
        "total_adversary_systems_employed": {
            "PRC_systems": prc_count,
            "Russia_systems": russia_count,
            "combined_kinetic_asat": total_asat,
            "combined_ew_systems": total_ew,
        },
        "fvey_response_options": [
            "Full retaliatory counter-space campaign against adversary satellites",
            "Conventional strike on adversary ASAT launch sites and EW ground stations",
            "Cyber retaliation against adversary space ground segments",
            "Diplomatic: invoke Article 5 / AUKUS / bilateral defense treaties",
            "Economic: maximum sanctions and asset freezes",
            "Nuclear: if early warning loss creates perceived first-strike threat (extreme)",
        ],
        "reconstitution_timeline": (
            "Partial capability restoration: 6-12 months (commercial augmentation, rapid launch). "
            "Significant capability restoration: 24-48 months (new satellites manufactured/launched). "
            "Full restoration to pre-attack levels: 5-10 years. "
            "Note: debris environment from kinetic attacks may prevent full restoration of LEO assets."
        ),
        "deterrence_assessment": (
            "Current deterrence posture: MODERATE. The catastrophic consequences for all "
            "parties (including attackers' own space assets from debris) make full-spectrum "
            "attack unlikely except as part of a major-power war. However, incremental "
            "escalation (EW -> cyber -> co-orbital -> kinetic) could lead to full-spectrum "
            "conflict through escalation dynamics rather than deliberate planning. "
            "The greatest risk is not a deliberate full-spectrum attack but an escalation "
            "spiral that reaches this end state."
        ),
        "probability_assessment": "LOW (as deliberate first move) / MODERATE (as escalation endpoint)",
    }


def _scenario_fvey_resilience() -> dict:
    """Scenario 7: FVEY reconstitution capacity assessment."""
    constellations = _FVEY_CONSTELLATIONS

    # US launch capacity (open source estimates)
    launch_capacity = {
        "SpaceX_Falcon_9": {
            "cadence_per_year": 96,
            "payload_to_LEO_kg": 22800,
            "payload_to_GTO_kg": 8300,
            "availability": "HIGH — highest launch cadence globally",
        },
        "SpaceX_Falcon_Heavy": {
            "cadence_per_year": 6,
            "payload_to_LEO_kg": 63800,
            "payload_to_GTO_kg": 26700,
            "availability": "MODERATE — limited launch opportunities",
        },
        "ULA_Vulcan": {
            "cadence_per_year": 8,
            "payload_to_LEO_kg": 27200,
            "payload_to_GTO_kg": 12500,
            "availability": "MODERATE — NSSL primary vehicle",
        },
        "Rocket_Lab_Electron": {
            "cadence_per_year": 15,
            "payload_to_LEO_kg": 300,
            "payload_to_GTO_kg": 0,
            "availability": "HIGH — responsive small-lift",
        },
        "SpaceX_Starship": {
            "cadence_per_year": 12,
            "payload_to_LEO_kg": 150000,
            "payload_to_GTO_kg": 50000,
            "availability": "DEVELOPING — when operational, transforms reconstitution calculus",
        },
    }

    # Loss scenarios
    loss_scenarios = [
        {
            "scenario": "Limited Strike: 5 satellites lost (mixed LEO/GEO)",
            "satellites_lost": 5,
            "types_lost": ["2x NRO ISR (LEO)", "2x WGS (GEO)", "1x GSSAP (GEO)"],
            "capability_impact": "15-20% degradation across ISR, COMMS, SDA",
            "reconstitution_timeline": "18-36 months for full restoration",
            "commercial_augmentation_timeline": "Days to weeks (Starlink, Maxar, Planet)",
            "launch_requirements": "5 dedicated launches or 3 launches with rideshare",
        },
        {
            "scenario": "Major Strike: 15 satellites lost (focused on ISR + COMMS)",
            "satellites_lost": 15,
            "types_lost": [
                "6x NRO ISR (LEO)", "4x WGS (GEO)", "2x AEHF (GEO)",
                "2x SBIRS (GEO)", "1x MUOS (GEO)",
            ],
            "capability_impact": "50-60% degradation; NC3 at risk; ISR severely degraded",
            "reconstitution_timeline": "36-60 months for significant restoration",
            "commercial_augmentation_timeline": "Weeks (partial capability via commercial)",
            "launch_requirements": "15+ dedicated launches over 3-5 years",
        },
        {
            "scenario": "Catastrophic Strike: 30+ satellites lost (full spectrum attack)",
            "satellites_lost": 30,
            "types_lost": [
                "10x NRO ISR", "6x GPS", "4x WGS", "3x AEHF", "3x SBIRS",
                "2x MUOS", "2x GSSAP",
            ],
            "capability_impact": "70-80% degradation; near-total space capability loss",
            "reconstitution_timeline": "5-10 years for major capability restoration",
            "commercial_augmentation_timeline": "Weeks for partial (Starlink C2, commercial ISR)",
            "launch_requirements": "30+ dedicated launches over 5-10 years; manufacturing bottleneck is primary constraint",
        },
    ]

    # Manufacturing bottleneck analysis
    manufacturing = {
        "gps_iii_production_rate": "2-3 per year (Lockheed Martin)",
        "wgs_production_rate": "1 per year (Boeing, if production restarted)",
        "aehf_successor_timeline": "AEHF successor (EPS) in development; first launch 2027+",
        "nro_proliferated_rate": "Accelerating with commercial bus adoption; 6-10 per year achievable",
        "sda_transport_layer": "Mass production of small sats; 20-40 per year achievable",
        "bottleneck_assessment": (
            "The primary reconstitution bottleneck is NOT launch capacity (SpaceX can surge to "
            "100+ launches/year) but satellite manufacturing. Exquisite GEO satellites (AEHF, "
            "SBIRS) take 5+ years to build. Even GPS III takes 3 years. The only way to achieve "
            "rapid reconstitution is to shift to proliferated architectures with mass-producible "
            "satellite buses — which is the direction SDA is moving but is years from being "
            "the primary architecture."
        ),
    }

    return {
        "scenario_id": "fvey_resilience",
        "title": "FVEY Space Architecture Resilience and Reconstitution Assessment",
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "constellations": constellations,
        "launch_capacity": launch_capacity,
        "loss_scenarios": loss_scenarios,
        "manufacturing_assessment": manufacturing,
        "resilience_score": {
            "overall": "LOW-MODERATE",
            "leo_isr": "MODERATE — NRO proliferated architecture improving; commercial augmentation available",
            "geo_comms": "LOW — small number of irreplaceable exquisite GEO satellites",
            "pnt": "MODERATE — GPS III production active; on-orbit spares exist; M-code improving",
            "early_warning": "LOW — SBIRS has no rapid replacement path; NGG successor years away",
            "sda": "MODERATE — GSSAP and commercial SSA provide some resilience",
        },
        "key_findings": [
            "Manufacturing, not launch, is the primary reconstitution bottleneck",
            "GEO MILSATCOM and early warning satellites are the least resilient (years to replace)",
            "Commercial augmentation (Starlink, Maxar) provides partial rapid-response capability",
            "Proliferated LEO architecture (SDA) is the path to resilience but not yet primary",
            "GPS has some resilience via on-orbit spares and GPS III production line",
            "No pre-positioned ground spares exist for GEO constellations",
            "Allied FVEY nations contribute minimally to reconstitution capacity",
        ],
        "recommendations": [
            "Pre-position satellite ground spares for critical constellations (GPS, SBIRS)",
            "Accelerate SDA proliferated architecture as primary ISR/COMMS platform",
            "Contract for responsive launch capacity (dedicated launch within 48 hours)",
            "Exercise reconstitution: annual end-to-end drill from call-up to on-orbit ops",
            "Invest in modular satellite bus standards for rapid manufacturing",
            "Expand allied burden sharing: UK, AU, CA contribute satellites to shared architecture",
            "Develop on-orbit sparing: dormant satellites pre-deployed and activated when needed",
            "Starship, when operational, transforms reconstitution through massive payload capacity",
        ],
    }


# ---------------------------------------------------------------------------
# Scenario registry
# ---------------------------------------------------------------------------

_SCENARIOS = {
    "prc_asat_vs_gps": {
        "id": "prc_asat_vs_gps",
        "title": "PRC DA-ASAT Strike on GPS Constellation",
        "attacker": "PRC",
        "target": "GPS",
        "type": "kinetic",
        "severity": "critical",
        "summary": "PRC uses DN-2/DN-3 to destroy GPS MEO satellites, degrading global PNT",
        "builder": _scenario_prc_asat_vs_gps,
    },
    "russia_nudol_vs_isr": {
        "id": "russia_nudol_vs_isr",
        "title": "Russia Nudol DA-ASAT Strike on FVEY LEO ISR",
        "attacker": "Russia",
        "target": "NRO ISR constellation",
        "type": "kinetic",
        "severity": "critical",
        "summary": "Russia uses Nudol to destroy FVEY LEO ISR satellites, creating intelligence gaps",
        "builder": _scenario_russia_nudol_vs_isr,
    },
    "prc_ew_campaign": {
        "id": "prc_ew_campaign",
        "title": "PRC Electronic Warfare Campaign — GPS/SATCOM Denial",
        "attacker": "PRC",
        "target": "GPS and SATCOM signals",
        "type": "electronic_warfare",
        "severity": "high",
        "summary": "Sustained GPS jamming and SATCOM denial across the Western Pacific",
        "builder": _scenario_prc_ew_campaign,
    },
    "co_orbital_vs_geo": {
        "id": "co_orbital_vs_geo",
        "title": "PRC Co-Orbital ASAT / Towing Attack on FVEY GEO SATCOM",
        "attacker": "PRC",
        "target": "WGS, AEHF, Skynet",
        "type": "co_orbital",
        "severity": "critical",
        "summary": "SJ-21-type towing attack against FVEY GEO communications satellites",
        "builder": _scenario_co_orbital_vs_geo,
    },
    "cyber_vs_ground": {
        "id": "cyber_vs_ground",
        "title": "Cyber Attack on FVEY Satellite Ground Segment",
        "attacker": "PRC/Russia",
        "target": "Ground control and data processing",
        "type": "cyber",
        "severity": "high",
        "summary": "Viasat-type AcidRain wiper attack on FVEY satellite ground infrastructure",
        "builder": _scenario_cyber_vs_ground,
    },
    "full_spectrum": {
        "id": "full_spectrum",
        "title": "Full Spectrum Counter-Space Attack",
        "attacker": "PRC + Russia",
        "target": "All FVEY space capabilities",
        "type": "combined",
        "severity": "critical",
        "summary": "Combined kinetic + EW + cyber + co-orbital attack across all domains simultaneously",
        "builder": _scenario_full_spectrum,
    },
    "fvey_resilience": {
        "id": "fvey_resilience",
        "title": "FVEY Resilience and Reconstitution Assessment",
        "attacker": "N/A (defensive assessment)",
        "target": "All FVEY constellations",
        "type": "assessment",
        "severity": "info",
        "summary": "How quickly can FVEY reconstitute if N satellites are lost? Launch and manufacturing capacity analysis",
        "builder": _scenario_fvey_resilience,
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_all_scenarios() -> dict:
    """List all available wargame scenarios with summaries."""
    now = datetime.now(timezone.utc)

    scenarios = []
    for sid, meta in _SCENARIOS.items():
        scenarios.append({
            "scenario_id": meta["id"],
            "title": meta["title"],
            "attacker": meta["attacker"],
            "target": meta["target"],
            "type": meta["type"],
            "severity": meta["severity"],
            "summary": meta["summary"],
        })

    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "total_scenarios": len(scenarios),
        "scenarios": scenarios,
        "usage": "Use /api/wargame/run/{scenario_id} to execute a scenario",
    }


def run_scenario(scenario_id: str) -> Optional[dict]:
    """Execute a specific wargame scenario.

    Args:
        scenario_id: one of the registered scenario IDs

    Returns:
        Full scenario analysis dict, or None if scenario not found.
    """
    cache_key = f"wargame_{scenario_id}"
    cached = _cached(cache_key)
    if cached is not None:
        return cached

    meta = _SCENARIOS.get(scenario_id)
    if meta is None:
        return None

    builder = meta["builder"]
    result = builder()
    result["generated_utc"] = datetime.now(timezone.utc).isoformat()

    return _store(cache_key, result)


def run_full_spectrum_assessment() -> dict:
    """Run the worst-case combined attack scenario."""
    result = run_scenario("full_spectrum")
    if result is None:
        return {
            "error": "Full spectrum scenario unavailable",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
        }
    return result


def assess_fvey_resilience() -> dict:
    """Run the FVEY reconstitution assessment."""
    result = run_scenario("fvey_resilience")
    if result is None:
        return {
            "error": "Resilience assessment unavailable",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
        }
    return result
