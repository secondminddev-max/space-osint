"""
Final Features Module — Echelon Vantage Space OSINT Platform
=============================================================

The definitive competitive-edge capabilities that place Echelon Vantage
beyond any commercial space domain awareness platform (LeoLabs, Slingshot
Serene, ExoAnalytic, COMSPOC, Kratos, L3Harris, Parsons, Raytheon).

Competitive gap analysis (as of March 2026):

**LeoLabs** — Radar-based tracking (Kiwi, Costa Rica, Midland, Azores).
  Strengths: High-cadence LEO tracking, debris monitoring, conjunction screening.
  Their gap vs us: No adversary intent analysis, no IPOE, no alliance tracking,
  no SIGINT constellation mapping, no wargaming/overmatch, no cislunar.

**Slingshot Aerospace (Serene)** — ML-driven catalog augmentation.
  Strengths: Maneuver detection, pattern-of-life analysis, operator intent.
  Their gap vs us: No FVEY-specific threat assessment, no alliance tracker,
  no IPOE framework, no electromagnetic spectrum assessment, no wargaming.

**ExoAnalytic Solutions** — Commercial telescope network (300+ sensors).
  Strengths: GEO belt coverage, RPO detection, optical characterization.
  Their gap vs us: Optical-only (no radar), no integrated threat assessment,
  no FVEY vulnerability analysis, no cislunar, no policy/treaty tracking.

**Kayhan Space / COMSPOC** — AGI-owned, precision orbit determination.
  Strengths: High-accuracy conjunction assessment, commercial SSA-as-service.
  Their gap vs us: Commercial focus only, no military threat assessment,
  no adversary capability analysis, no FVEY-tailored products.

**Kratos Space** — Ground system automation, SATCOM monitoring.
  Strengths: Ground segment automation, signal monitoring, anomaly detection.
  Their gap vs us: Ground-focused, no space order of battle, no IPOE,
  no adversary constellation analysis, no wargaming.

**L3Harris** — Military-grade SSA sensors (Space Fence, GEODSS).
  Strengths: Space Fence radar (Marshall Islands), GEODSS telescope network.
  Their gap vs us: Sensor-focused (no analysis layer), classified outputs,
  no open-source threat assessment, no allied coordination tracker.

**Parsons** — Defense C2 integration, space ground systems.
  Strengths: C2 system integration, mission planning.
  Their gap vs us: Integration-focused, no independent analysis capability,
  no OSINT aggregation, no adversary intent assessment.

**Raytheon (RTX)** — Missile warning, early warning radars.
  Strengths: SBIRS ground processing, missile defense integration.
  Their gap vs us: Classified/proprietary, sensor-processing only,
  no open threat assessment, no FVEY coordination view.

**18th Space Defense Squadron (Space-Track.org)** — Authoritative catalog.
  Strengths: Official US catalog, TLE/GP element distribution, conjunction messages.
  Their gap vs us: Catalog-only — no analysis, no threat assessment, no context.

**Open source (GitHub)** — ASTRIAGraph, Keeptrack.space, SatNOGS.
  Strengths: Open data, community-driven, educational.
  Their gap vs us: No military relevance, no threat assessment, no IPOE,
  no adversary characterization, academic/hobbyist focus.

This module implements six features that NO competitor offers in combination:

1. **AUKUS/Alliance Tracker** — FVEY/AUKUS/CSpO/Quad space cooperation status
2. **Space IPOE** — Intelligence Preparation of the Operating Environment
3. **Satellite Maneuver Detection Indicators** — Behavioral watchlist
4. **SIGINT/ELINT Constellation Mapping** — Adversary signals intelligence
5. **Space Debris Environment Assessment** — Comprehensive debris statistics
6. **Cislunar Awareness** — Beyond-GEO object and mission tracking

Data provenance: Open-source intelligence compiled from DIA, NASIC, SWF,
CSIS, UNOOSA, ESA, NASA, USSPACECOM, ADF, MOD(UK), NZDF, CAF reports.

Classification: UNCLASSIFIED // OSINT // REL TO FVEY
"""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

import httpx

from data_sources.space_weather import fetch_weather_composite


# ---------------------------------------------------------------------------
# Cache infrastructure
# ---------------------------------------------------------------------------

_cache: Dict[str, dict] = {}
_FINAL_TTL = 300  # 5-minute cache

def _cached(key: str) -> Optional[dict]:
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < _FINAL_TTL:
        return entry["data"]
    return None

def _store(key: str, data: dict) -> dict:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# =========================================================================
# 1. AUKUS / ALLIANCE TRACKER
# =========================================================================
#
# Tracks the complex web of allied space cooperation frameworks that
# underpin FVEY space domain awareness. No commercial platform provides
# this view — it requires understanding the classified-to-OSINT boundary
# of multiple alliance frameworks simultaneously.
#
# Key frameworks tracked:
# - AUKUS Pillar II (Advanced Capabilities) — space & electronic warfare
# - Five Eyes SSA Sharing Agreement (2014+)
# - Combined Space Operations (CSpO) — 7-nation coalition
# - Quad (US-Japan-India-Australia) space cooperation
# - Bilateral agreements (US-Japan, US-ROK, US-France, etc.)
# - NATO Space Centre of Excellence (Toulouse, est. 2023)
# - Allied Ground Segment (Pine Gap, Woomera, Fylingdales, etc.)
#
# References:
# - AUKUS Joint Leaders Statement (2021, updated 2023)
# - CSpO Vision 2031 (USSPACECOM)
# - NATO Strategic Concept 2022 (space as operational domain)
# - ADF Space Command establishment announcement (2022)
# - UK Space Command establishment (2021)
# - Quad Joint Statement on Space (2023)
# - DIA "Challenges to Security in Space" (2022)
# =========================================================================

def get_alliance_status() -> dict:
    """Return comprehensive FVEY/allied space cooperation status.

    Covers AUKUS, Five Eyes, CSpO, NATO, Quad, and bilateral space
    cooperation frameworks. Includes allied ground segment sharing
    and combined space operations initiatives.
    """
    cached = _cached("alliance_status")
    if cached is not None:
        return cached

    now = datetime.now(timezone.utc)

    aukus = {
        "framework": "AUKUS",
        "full_name": "Australia-United Kingdom-United States Trilateral Security Partnership",
        "established": "2021-09-15",
        "members": ["Australia", "United Kingdom", "United States"],
        "pillar_1": {
            "name": "Nuclear-Powered Submarines",
            "space_relevance": "LOW — submarine program, but SSBNs rely on space-based comms/nav",
            "status": "In progress — Australia acquiring SSN-AUKUS class",
        },
        "pillar_2": {
            "name": "Advanced Capabilities",
            "space_relevance": "HIGH — directly includes space domain",
            "workstreams": [
                {
                    "name": "Space & Counter-Space",
                    "status": "ACTIVE",
                    "activities": [
                        "Deep space radar cooperation (US Space Fence data sharing with AU/UK)",
                        "Shared space situational awareness data fusion",
                        "Joint counter-space capability development",
                        "Resilient satellite communications architecture",
                        "Space domain awareness sensor integration",
                        "Combined space operations procedures",
                    ],
                    "key_milestones": [
                        "2022: AUKUS Advanced Capabilities agreement signed",
                        "2023: Space cooperation workstream formally established",
                        "2024: Joint SDA data sharing agreement operationalized",
                        "2025: Combined space C2 exercise conducted",
                        "2026 (planned): Integrated SDA architecture initial capability",
                    ],
                },
                {
                    "name": "Electronic Warfare",
                    "status": "ACTIVE",
                    "space_relevance": "Space-based EW and counter-EW capabilities",
                },
                {
                    "name": "Quantum Technologies",
                    "status": "ACTIVE",
                    "space_relevance": "Quantum key distribution via satellite, quantum sensing for SDA",
                },
                {
                    "name": "Artificial Intelligence & Autonomy",
                    "status": "ACTIVE",
                    "space_relevance": "AI for satellite anomaly detection and pattern-of-life analysis",
                },
                {
                    "name": "Hypersonic & Counter-Hypersonic",
                    "status": "ACTIVE",
                    "space_relevance": "Space-based tracking layer for hypersonic glide vehicles",
                },
                {
                    "name": "Cyber",
                    "status": "ACTIVE",
                    "space_relevance": "Defensive cyber for space ground segments",
                },
                {
                    "name": "Undersea Capabilities",
                    "status": "ACTIVE",
                    "space_relevance": "Subsea cable protection intersects with space-based maritime ISR",
                },
                {
                    "name": "Innovation / Industrial Base",
                    "status": "ACTIVE",
                    "space_relevance": "AUKUS defense industrial base for space systems",
                },
            ],
        },
        "assessment": (
            "AUKUS Pillar II space cooperation is the most significant new "
            "allied space framework since the original FVEY SSA sharing agreements. "
            "It enables trilateral development of counter-space capabilities and "
            "shared SDA infrastructure that was previously bilateral-only. "
            "Key gap: No formal AUKUS space command structure yet — coordination "
            "remains through national channels."
        ),
    }

    fvey_space = {
        "framework": "Five Eyes Space Cooperation",
        "full_name": "Five Eyes Space Domain Awareness Sharing",
        "members": ["United States", "United Kingdom", "Canada", "Australia", "New Zealand"],
        "established": "2014 (formalized SSA sharing)",
        "status": "ACTIVE — deepening",
        "agreements": [
            {
                "name": "SSA Data Sharing Agreement",
                "year": 2014,
                "status": "ACTIVE",
                "scope": "Sharing of space tracking data, conjunction assessments, and space event reports",
            },
            {
                "name": "Combined Space Operations Center (CSpOC) Access",
                "year": 2018,
                "status": "ACTIVE",
                "scope": "Allied liaison officers embedded at Vandenberg SFB CSpOC",
            },
            {
                "name": "Space Surveillance Network Data Sharing",
                "year": 2010,
                "status": "ACTIVE",
                "scope": "Authoritative space catalog data shared among FVEY nations",
            },
        ],
        "national_space_commands": [
            {
                "nation": "United States",
                "command": "United States Space Command (USSPACECOM)",
                "service": "United States Space Force (USSF)",
                "established_command": 2019,
                "established_service": 2019,
                "hq": "Peterson SFB, Colorado Springs, CO",
                "personnel": "~16,000 (Space Force) + SPACECOM staff",
                "key_units": [
                    "Space Operations Command (SpOC) — Vandenberg SFB",
                    "Space Systems Command (SSC) — Los Angeles AFB",
                    "Space Training and Readiness Command (STARCOM) — Vandenberg SFB",
                    "18th Space Defense Squadron — Space-Track.org operations",
                    "National Space Defense Center (NSDC) — Schriever SFB",
                ],
            },
            {
                "nation": "United Kingdom",
                "command": "UK Space Command",
                "established_command": 2021,
                "hq": "RAF High Wycombe, Buckinghamshire",
                "personnel": "~1,500 (growing)",
                "key_units": [
                    "Space Operations Centre — RAF High Wycombe",
                    "RAF Fylingdales — Ballistic Missile Early Warning / SSA radar",
                    "Skynet SATCOM operations",
                    "Space Surveillance & Tracking (UK-SST) programme",
                ],
            },
            {
                "nation": "Australia",
                "command": "Defence Space Command",
                "established_command": 2022,
                "hq": "RAAF Base Edinburgh, South Australia",
                "personnel": "~1,000 (growing)",
                "key_units": [
                    "Space Surveillance Telescope (SST) — Exmouth, WA (relocated from US)",
                    "Joint Defence Facility Pine Gap — DSP/SBIRS relay, SIGINT",
                    "Woomera Range Complex — space launch and tracking",
                    "C-band radar (SSA) — development",
                    "Defence Space Command Operations Centre",
                ],
            },
            {
                "nation": "Canada",
                "command": "3 Canadian Space Division (3 CSD)",
                "established_command": 2022,
                "hq": "Ottawa, Ontario",
                "personnel": "~400",
                "key_units": [
                    "Sapphire — SSA satellite (LEO optical surveillance)",
                    "NEOSSat — Near-Earth Object Surveillance Satellite",
                    "Canadian Forces Space Operations Centre",
                ],
            },
            {
                "nation": "New Zealand",
                "command": "NZDF Joint Space Activities",
                "established_command": 2023,
                "hq": "Wellington",
                "personnel": "~50 (embedded)",
                "key_units": [
                    "Rocket Lab launch site — Mahia Peninsula (commercial, FVEY-allied)",
                    "NZ contribution to CSpO via embedded personnel",
                    "Southern hemisphere tracking contributions",
                ],
            },
        ],
        "assessment": (
            "FVEY space cooperation is the deepest in the world. All five nations "
            "have established dedicated space commands/divisions since 2019. "
            "Key strength: Global sensor coverage from Arctic to Antarctic. "
            "Key gap: New Zealand has minimal organic space capability — "
            "relies on Rocket Lab (commercial) for launch access."
        ),
    }

    cspo = {
        "framework": "Combined Space Operations (CSpO)",
        "full_name": "Combined Space Operations Initiative",
        "established": 2014,
        "members": [
            {"nation": "United States", "role": "Lead nation", "joined": 2014},
            {"nation": "United Kingdom", "role": "Founding member", "joined": 2014},
            {"nation": "Canada", "role": "Founding member", "joined": 2014},
            {"nation": "Australia", "role": "Founding member", "joined": 2014},
            {"nation": "New Zealand", "role": "Member", "joined": 2018},
            {"nation": "France", "role": "Member", "joined": 2020},
            {"nation": "Germany", "role": "Member", "joined": 2021},
        ],
        "status": "ACTIVE — expanding membership",
        "vision": "CSpO Vision 2031 — unified allied space operations",
        "activities": [
            "Combined space operations planning and execution",
            "Shared SSA data and analysis",
            "Coalition space support to terrestrial operations",
            "Space order of battle development",
            "Combined space exercise program (Global Sentinel, etc.)",
            "Interoperability standards for space C2",
        ],
        "exercises": [
            {
                "name": "Global Sentinel",
                "frequency": "Annual",
                "scope": "Combined SSA exercise — multinational data sharing and conjunction response",
                "latest": "Global Sentinel 2025 — all 7 CSpO nations participated",
            },
            {
                "name": "Schriever Wargame",
                "frequency": "Biennial",
                "scope": "Strategic space wargame — conflict scenarios with allied response",
                "latest": "Schriever Wargame 2025",
            },
            {
                "name": "AsterX (France)",
                "frequency": "Annual",
                "scope": "French-led space defense exercise, CSpO nations invited",
                "latest": "AsterX 2025",
            },
            {
                "name": "Olympic Defender",
                "frequency": "Annual",
                "scope": "Protect/defend space assets exercise",
                "latest": "Olympic Defender 2025",
            },
        ],
        "assessment": (
            "CSpO is the primary operational framework for allied space cooperation. "
            "Expanding beyond FVEY to include France and Germany indicates the "
            "shift from intelligence-sharing to operational coalition building. "
            "Key gap: Japan, South Korea, and other key allies not yet members."
        ),
    }

    nato_space = {
        "framework": "NATO Space Activities",
        "status": "ACTIVE — space recognized as operational domain since 2019",
        "key_developments": [
            {
                "year": 2019,
                "event": "Space declared an operational domain by NATO",
                "significance": "Article 5 could apply to attacks on allied space assets",
            },
            {
                "year": 2020,
                "event": "NATO Space Centre established at Allied Air Command, Ramstein",
                "significance": "First NATO facility dedicated to space operations",
            },
            {
                "year": 2023,
                "event": "NATO Space Centre of Excellence (SCoE) established in Toulouse, France",
                "significance": "Doctrine development, training, lessons learned for allied space operations",
            },
            {
                "year": 2024,
                "event": "NATO Overarching Space Policy updated",
                "significance": "Enhanced framework for collective space defense",
            },
        ],
        "nato_space_centre_of_excellence": {
            "location": "Toulouse, France",
            "established": 2023,
            "sponsoring_nations": ["France", "Germany", "Italy", "United Kingdom", "United States"],
            "mission": [
                "Develop space doctrine and concepts for NATO",
                "Conduct space-related education and training",
                "Support space exercises and experimentation",
                "Lessons learned from space operations",
                "Interoperability standards for allied space forces",
            ],
        },
        "assessment": (
            "NATO space integration is accelerating but remains behind FVEY/CSpO "
            "in operational depth. The SCoE in Toulouse is building doctrine that "
            "30 NATO nations can use. Key challenge: many NATO nations have "
            "minimal organic space capability — reliance on US space architecture."
        ),
    }

    quad_space = {
        "framework": "Quad Space Cooperation",
        "full_name": "Quadrilateral Security Dialogue — Space Working Group",
        "members": ["United States", "Japan", "India", "Australia"],
        "established": "2023 (space working group)",
        "status": "ACTIVE — growing",
        "activities": [
            "Space situational awareness data sharing",
            "Debris monitoring cooperation",
            "Space weather data exchange",
            "GNSS cooperation and resilience",
            "Earth observation data sharing for HADR",
            "Commercial space industry cooperation",
        ],
        "significance_for_fvey": (
            "Extends SSA cooperation to Japan and India — two nations with "
            "significant space capabilities (JAXA/ISRO) that are not FVEY members. "
            "India's ASAT capability (Mission Shakti 2019) makes it both a partner "
            "and a stakeholder in space security norms."
        ),
        "assessment": (
            "Quad space cooperation fills the gap between FVEY (intelligence-focused) "
            "and broader multilateral frameworks (UN COPUOS). Japan's quasi-zenith "
            "QZSS constellation and India's NavIC/IRNSS provide regional PNT "
            "alternatives to GPS — strategically important for Indo-Pacific operations."
        ),
    }

    bilateral = [
        {
            "partners": "US — Japan",
            "framework": "US-Japan Space Cooperation Agreement (2023 expanded)",
            "activities": [
                "Hosted payload on Japanese quasi-zenith satellites",
                "SSA data sharing via US-Japan SSA agreement",
                "JAXA-USSF space debris cooperation",
                "Missile warning data sharing (DSP/SBIRS to Japan)",
                "Joint development of space-based hypersonic tracking",
            ],
        },
        {
            "partners": "US — South Korea",
            "framework": "US-ROK Space Cooperation",
            "activities": [
                "SSA data sharing agreement (2023)",
                "ROK Space Agency (KASA) established 2024",
                "Korean GPS augmentation cooperation",
                "Missile warning cooperation (THAAD radar data)",
            ],
        },
        {
            "partners": "US — France",
            "framework": "US-France Space SSA Agreement",
            "activities": [
                "GRAVES radar SSA data sharing",
                "GeoTracker telescope network data exchange",
                "Joint space exercises (AsterX participation)",
                "CSpO framework cooperation",
            ],
        },
        {
            "partners": "US — Norway",
            "framework": "Space Cooperation Agreement",
            "activities": [
                "Svalbard ground station access",
                "Arctic SSA cooperation",
                "SATCOM relay via Norwegian ground infrastructure",
            ],
        },
        {
            "partners": "Australia — Japan",
            "framework": "Australia-Japan Reciprocal Access Agreement (2022)",
            "activities": [
                "Space situational awareness data sharing",
                "Joint exercises including space domain",
                "Indo-Pacific space cooperation alignment",
            ],
        },
        {
            "partners": "UK — France",
            "framework": "Lancaster House Treaties (2010, space addendum)",
            "activities": [
                "Combined space operations planning",
                "SSA data sharing",
                "Skynet/Syracuse SATCOM interoperability",
            ],
        },
    ]

    allied_ground_segment = [
        {
            "name": "Joint Defence Facility Pine Gap",
            "location": "Alice Springs, Northern Territory, Australia",
            "lat": -23.799,
            "lng": 133.737,
            "operator": "US-Australia (joint)",
            "classification": "TOP SECRET (facility), UNCLASSIFIED (existence)",
            "known_capabilities": [
                "DSP/SBIRS ground relay — missile early warning",
                "SIGINT satellite ground station",
                "Geosynchronous satellite control",
                "Critical node in US nuclear command and control",
            ],
            "fvey_significance": "CRITICAL — Southern hemisphere cornerstone of US-AU alliance",
        },
        {
            "name": "RAF Fylingdales",
            "location": "North York Moors, Yorkshire, United Kingdom",
            "lat": 54.362,
            "lng": -0.670,
            "operator": "UK Royal Air Force / USSF shared",
            "known_capabilities": [
                "AN/FPS-132 Upgraded Early Warning Radar (UEWR)",
                "Ballistic missile early warning",
                "Space surveillance and tracking",
                "Part of US BMEWS/SSPARS network",
            ],
            "fvey_significance": "CRITICAL — Northern European space surveillance and missile warning",
        },
        {
            "name": "Woomera Test Range / C-Band Radar",
            "location": "Woomera, South Australia, Australia",
            "lat": -31.164,
            "lng": 136.832,
            "operator": "Royal Australian Air Force",
            "known_capabilities": [
                "Space surveillance C-band radar (development/IOC)",
                "Missile and space launch testing range",
                "Southern hemisphere SSA coverage",
            ],
            "fvey_significance": "HIGH — Expanding AU sovereign SDA capability",
        },
        {
            "name": "Space Surveillance Telescope (SST)",
            "location": "Exmouth, Western Australia, Australia",
            "lat": -21.816,
            "lng": 114.167,
            "operator": "Royal Australian Air Force (transferred from DARPA/USSF)",
            "known_capabilities": [
                "Wide-field-of-view optical telescope",
                "Deep space (GEO+) surveillance",
                "Detects faint objects in GEO belt",
                "Southern hemisphere deep-space coverage (unique FVEY asset)",
            ],
            "fvey_significance": "CRITICAL — Only southern hemisphere deep-space optical SSA sensor",
        },
        {
            "name": "Diego Garcia Ground Station",
            "location": "Diego Garcia, British Indian Ocean Territory",
            "lat": -7.316,
            "lng": 72.411,
            "operator": "USSF / UK shared",
            "known_capabilities": [
                "GEODSS optical telescope (deep space surveillance)",
                "GPS monitor station",
                "SATCOM relay ground segment",
                "Space surveillance support",
            ],
            "fvey_significance": "HIGH — Indian Ocean space surveillance and PNT monitoring",
        },
        {
            "name": "GEODSS Maui (Haleakala)",
            "location": "Maui, Hawaii, United States",
            "lat": 20.708,
            "lng": -156.258,
            "operator": "USSF 18th Space Defense Squadron",
            "known_capabilities": [
                "Ground-based Electro-Optical Deep Space Surveillance",
                "GEO belt optical surveillance",
                "Satellite characterization (photometry, spectroscopy)",
            ],
            "fvey_significance": "CRITICAL — Primary Pacific deep-space optical surveillance",
        },
        {
            "name": "Space Fence",
            "location": "Kwajalein Atoll, Marshall Islands",
            "lat": 9.395,
            "lng": 167.471,
            "operator": "USSF / Lockheed Martin",
            "known_capabilities": [
                "S-band ground-based radar",
                "LEO/MEO tracking — 200,000+ objects detectable",
                "Uncued detection of small debris (>10 cm)",
                "Revolutionary improvement over legacy VHF fence",
            ],
            "fvey_significance": "CRITICAL — Most capable ground-based SSA radar in the world",
        },
        {
            "name": "Canadian Sapphire Satellite Operations",
            "location": "Ottawa, Ontario, Canada (operations centre)",
            "lat": 45.424,
            "lng": -75.695,
            "operator": "3 Canadian Space Division",
            "known_capabilities": [
                "Sapphire SSA satellite — LEO optical surveillance of deep space",
                "NEOSSat — near-Earth object surveillance",
                "Canadian SSA data contribution to FVEY",
            ],
            "fvey_significance": "MODERATE — Space-based SSA contribution from Canada",
        },
        {
            "name": "Svalbard Satellite Station (SvalSat)",
            "location": "Svalbard, Norway (allied, not FVEY)",
            "lat": 78.231,
            "lng": 15.408,
            "operator": "KSAT (Kongsberg Satellite Services)",
            "known_capabilities": [
                "Polar satellite ground station — all polar orbiting sats pass overhead",
                "Critical for LEO satellite command/data downlink",
                "Used by FVEY nations for military satellite support",
            ],
            "fvey_significance": "HIGH — Arctic coverage critical for polar-orbiting military sats",
        },
    ]

    # Aggregate summary
    total_frameworks = 6  # AUKUS, FVEY, CSpO, NATO, Quad, bilaterals
    total_nations_cooperating = len({
        "US", "UK", "CA", "AU", "NZ",  # FVEY
        "FR", "DE",  # CSpO
        "JP", "IN",  # Quad
        "KR", "NO",  # Bilateral
    })

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Allied Space Cooperation Status — AUKUS/FVEY/CSpO/NATO/Quad",
        "generated_utc": now.isoformat(),
        "summary": {
            "total_frameworks_tracked": total_frameworks,
            "total_allied_nations_in_space_cooperation": total_nations_cooperating,
            "deepest_cooperation": "Five Eyes (intelligence) + AUKUS (capabilities)",
            "broadest_cooperation": "CSpO (7 nations) + NATO (30 nations)",
            "newest_framework": "Quad Space Working Group (2023)",
            "key_assessment": (
                "Allied space cooperation is expanding rapidly in both depth and breadth. "
                "AUKUS Pillar II adds capability development to existing FVEY intelligence sharing. "
                "CSpO expanding beyond FVEY to include France and Germany. Quad extends to "
                "Indo-Pacific partners Japan and India. NATO provides broadest framework but "
                "shallowest depth. Strategic bifurcation emerging: Artemis Accords bloc vs "
                "PRC-Russia ILRS bloc."
            ),
            "critical_gaps": [
                "No unified allied space command — national commands coordinate bilaterally",
                "Combined space C2 interoperability still immature",
                "Japan and South Korea not in CSpO despite Indo-Pacific significance",
                "New Zealand has minimal organic space capability",
                "Cislunar domain cooperation framework does not yet exist",
                "No allied agreement on offensive counter-space operations rules of engagement",
            ],
        },
        "aukus": aukus,
        "five_eyes_space": fvey_space,
        "combined_space_operations": cspo,
        "nato_space": nato_space,
        "quad_space": quad_space,
        "bilateral_agreements": bilateral,
        "allied_ground_segment": allied_ground_segment,
    }

    return _store("alliance_status", result)


# =========================================================================
# 2. SPACE INTELLIGENCE PREPARATION OF THE OPERATING ENVIRONMENT (IPOE)
# =========================================================================
#
# A formal IPOE for the space domain — the product format military
# planners actually use. No commercial SDA platform generates this;
# it requires combining all intelligence sources into a structured
# military planning document.
#
# IPOE is a systematic, continuous process of analyzing the threat
# and environment in a specific area of interest (JP 2-01.3).
#
# Steps:
# 1. Define the operational environment (Area of Interest + Area of Operations)
# 2. Describe the environment's effects on operations (terrain, weather)
# 3. Evaluate the threat (capabilities, organizations, doctrine)
# 4. Determine threat COAs (Most Dangerous, Most Likely)
#
# References:
# - JP 2-01.3 Joint Intelligence Preparation of the Operational Environment
# - ATP 2-01.3 Intelligence Preparation of the Battlefield (Army)
# - AFDP 2-0 Intelligence (Air Force)
# - ADF Publication 3.0.3 Intelligence Preparation of the Battlespace
# - DIA "Challenges to Security in Space" (2022)
# - NASIC "Competing in Space" (2018, updated)
# - SWF "Global Counterspace Capabilities" (annual)
# =========================================================================

async def generate_space_ipoe(client: httpx.AsyncClient) -> dict:
    """Generate a formal Space IPOE document.

    Integrates space weather, adversary capabilities, allied posture,
    and environmental factors into a structured military intelligence
    product that follows JP 2-01.3 / ADF IPB doctrine.

    Args:
        client: httpx.AsyncClient for live data fetches

    Returns:
        Structured IPOE document with all four analytical steps.
    """
    cached = _cached("space_ipoe")
    if cached is not None:
        return cached

    now = datetime.now(timezone.utc)

    # Fetch live space weather for environmental assessment
    try:
        weather = await fetch_weather_composite(client)
    except Exception:
        weather = {}

    kp = weather.get("kp_current") or 0
    bz = weather.get("bz") or 0
    sw_speed = weather.get("solar_wind_speed") or 400

    # ---- STEP 1: DEFINE THE OPERATIONAL ENVIRONMENT ----
    step_1 = {
        "step": "Step 1: Define the Operational Environment",
        "area_of_interest": {
            "description": "All orbital regimes from LEO through cislunar space",
            "orbital_regimes": [
                {
                    "regime": "Low Earth Orbit (LEO)",
                    "altitude_range_km": "160-2,000",
                    "period_range_min": "87-127",
                    "key_characteristics": [
                        "Highest satellite density — >10,000 active satellites",
                        "ISR, communications, scientific, and crewed operations",
                        "Most contested regime — ASAT-reachable by all spacefaring adversaries",
                        "Atmospheric drag provides natural debris cleansing below ~600 km",
                        "Space Fence provides uncued tracking of objects >10 cm",
                    ],
                    "fvey_assets_at_risk": [
                        "ISS and crew",
                        "Starlink/OneWeb communications constellations",
                        "NRO/classified ISR satellites",
                        "Iridium NEXT military (EMSS)",
                        "Planet/BlackSky/Maxar commercial ISR",
                    ],
                },
                {
                    "regime": "Medium Earth Orbit (MEO)",
                    "altitude_range_km": "2,000-35,786",
                    "period_range_hours": "2-24",
                    "key_characteristics": [
                        "Navigation satellite domain — GPS, Galileo, BeiDou, GLONASS",
                        "Van Allen radiation belts (inner: 1,000-6,000 km; outer: 13,000-60,000 km)",
                        "High radiation environment limits satellite electronics",
                        "Fewer active satellites than LEO but each is high-value",
                    ],
                    "fvey_assets_at_risk": [
                        "GPS III constellation (31 satellites, ~20,200 km)",
                        "Galileo (allied, 23,222 km)",
                        "Nuclear detonation detection (NUDET) on GPS",
                    ],
                },
                {
                    "regime": "Geostationary Orbit (GEO)",
                    "altitude_km": "35,786",
                    "period_hours": "24 (geosynchronous)",
                    "key_characteristics": [
                        "Highest-value orbital real estate — fixed Earth coverage",
                        "~560 active GEO satellites in a single orbital ring",
                        "Station-keeping required — all GEO satellites maneuver regularly",
                        "RPO difficult to detect — targets appear stationary",
                        "GEODSS and SST provide optical surveillance",
                    ],
                    "fvey_assets_at_risk": [
                        "SBIRS GEO (missile early warning)",
                        "WGS (wideband military SATCOM)",
                        "AEHF/EPS (protected SATCOM)",
                        "MUOS (UHF SATCOM)",
                        "Skynet 5/6 (UK military SATCOM)",
                        "Optus Defence (AU military SATCOM)",
                        "GSSAP (US space surveillance)",
                    ],
                },
                {
                    "regime": "Highly Elliptical Orbit (HEO)",
                    "altitude_range_km": "500-40,000 (apogee)",
                    "period_hours": "12 (Molniya), 24 (Tundra)",
                    "key_characteristics": [
                        "Extended dwell over high-latitude regions",
                        "Critical for Russian and Chinese communications/EW",
                        "Molniya orbit (63.4 deg inc) exploits critical inclination",
                        "Difficult to track — passes through multiple surveillance gaps",
                    ],
                    "fvey_assets_at_risk": [
                        "SBIRS HEO payloads (hosted on classified platforms)",
                        "Planned Next-Gen OPIR HEO",
                    ],
                },
                {
                    "regime": "Cislunar Space",
                    "altitude_range_km": ">35,786 to lunar distance (~384,400)",
                    "key_characteristics": [
                        "Emerging domain — minimal surveillance capability exists",
                        "Earth-Moon Lagrange points (L1, L2) are gravitationally stable",
                        "PRC Chang'e program has active hardware (orbiter + lander)",
                        "NASA Artemis/Gateway planned for L2 halo orbit",
                        "MAJOR SURVEILLANCE GAP — no persistent tracking beyond GEO",
                    ],
                    "fvey_assets_at_risk": [
                        "Planned Gateway station (L2 halo orbit)",
                        "Artemis crewed missions (translunar)",
                        "CAPSTONE pathfinder (L2 NRHO)",
                    ],
                },
            ],
        },
        "area_of_operations": {
            "primary": "LEO and GEO regimes where FVEY assets are concentrated",
            "secondary": "MEO (GPS/GNSS) and HEO (missile warning)",
            "emerging": "Cislunar (Artemis/Gateway era)",
            "geographic_focus_below": [
                "Indo-Pacific (21N-35N, 100E-145E) — Taiwan contingency",
                "Eastern Europe (45N-60N, 20E-45E) — NATO eastern flank",
                "Middle East (20N-40N, 30E-65E) — CENTCOM AOR",
                "Korean Peninsula (33N-43N, 124E-132E) — DPRK threat",
                "Arctic (>66N) — emerging great power competition",
            ],
        },
    }

    # ---- STEP 2: DESCRIBE ENVIRONMENTAL EFFECTS ----
    # Space weather / orbital mechanics / terrain analysis
    space_weather_status = "BENIGN"
    if kp >= 7:
        space_weather_status = "SEVERE"
    elif kp >= 5:
        space_weather_status = "ACTIVE"
    elif kp >= 3:
        space_weather_status = "UNSETTLED"

    step_2 = {
        "step": "Step 2: Describe the Environment's Effects on Operations",
        "space_terrain_analysis": {
            "description": (
                "Unlike terrestrial terrain, space 'terrain' is defined by "
                "orbital mechanics, radiation environments, and electromagnetic "
                "propagation conditions. Terrain analysis identifies areas that "
                "constrain or enable military operations."
            ),
            "key_terrain": [
                {
                    "feature": "GEO Belt (35,786 km equatorial ring)",
                    "military_significance": "CRITICAL — controls global communications, EW, ISR",
                    "control": "Contested — FVEY, PRC, and Russia all have major assets",
                    "vulnerability": "RPO, co-orbital ASAT, ground-based dazzling",
                },
                {
                    "feature": "Sun-Synchronous Orbit corridor (600-900 km, 97-98 deg inc)",
                    "military_significance": "HIGH — optimal for Earth observation and ISR",
                    "control": "FVEY advantage in commercial ISR; PRC rapidly closing gap",
                    "vulnerability": "DA-ASAT, debris (FY-1C cloud at 865 km)",
                },
                {
                    "feature": "GPS orbital shell (20,200 km, 55 deg inc)",
                    "military_significance": "CRITICAL — PNT backbone for all FVEY military ops",
                    "control": "FVEY-controlled (GPS) but contested by BeiDou/GLONASS",
                    "vulnerability": "Ground-based jamming/spoofing, radiation belt effects",
                },
                {
                    "feature": "Debris density bands (750-850 km, 450-550 km)",
                    "military_significance": "DENIED TERRAIN — highest collision risk",
                    "control": "Uncontrolled — legacy debris from FY-1C and Cosmos 1408",
                    "vulnerability": "Operational satellites transiting these bands face elevated risk",
                },
                {
                    "feature": "Van Allen Radiation Belts (1,000-60,000 km)",
                    "military_significance": "OBSTACLE — limits satellite electronics/orbits",
                    "control": "Natural feature — not controllable",
                    "vulnerability": "Solar storm enhancement can expand belts, damage MEO sats",
                },
                {
                    "feature": "Earth-Moon L1/L2 Lagrange Points",
                    "military_significance": "EMERGING — potential for cislunar surveillance/C2",
                    "control": "UNCLAIMED — first-mover advantage available",
                    "vulnerability": "No persistent surveillance capability exists",
                },
            ],
        },
        "space_weather_assessment": {
            "current_status": space_weather_status,
            "kp_index": kp,
            "imf_bz_nT": bz,
            "solar_wind_speed_kms": sw_speed,
            "operational_impacts": {
                "satellite_drag": "ELEVATED" if kp >= 5 else "NOMINAL",
                "gps_accuracy": "DEGRADED" if kp >= 5 else "NOMINAL",
                "hf_propagation": "DISRUPTED" if kp >= 5 else "NORMAL",
                "radiation_environment": "ELEVATED" if kp >= 7 else "NOMINAL",
                "satellite_charging_risk": "HIGH" if kp >= 7 else "LOW",
            },
            "forecast_note": (
                "Space weather can change rapidly. A single X-class flare can "
                "degrade GPS/HF within 8 minutes (radio blackout) and cause "
                "geomagnetic storm within 1-3 days (CME arrival)."
            ),
        },
        "electromagnetic_environment": {
            "gps_jamming_threat": "PERSISTENT — Russia active in Europe, PRC in South China Sea",
            "satcom_interference": "MODERATE — Russian Tirada-2 deployed, PRC developing",
            "natural_rf_environment": "DEGRADED" if kp >= 5 else "NOMINAL",
        },
    }

    # ---- STEP 3: EVALUATE THE THREAT ----
    step_3 = {
        "step": "Step 3: Evaluate the Threat",
        "threat_actors": [
            {
                "actor": "People's Republic of China (PRC)",
                "organization": "PLA Strategic Support Force (SSF) — Space Systems Department",
                "restructured": "PLA Information Support Force (2024 reorganization)",
                "threat_level": "CRITICAL — peer competitor",
                "space_order_of_battle": {
                    "total_military_satellites": "200+ (estimated, rapid growth)",
                    "isr_eo_ir": "Yaogan/Gaofen series — 100+ operational",
                    "isr_sar": "Yaogan SAR series — 30+ operational",
                    "sigint_elint": "Shijian/Chuangxin/TJS/TJSW — 20+ operational",
                    "early_warning": "In development — no operational GEO EW yet",
                    "navigation": "BeiDou-3 (30 MEO + 3 GEO + 3 IGSO = 36 total)",
                    "communications": "Zhongxing military SATCOM, Tiantong mobile",
                    "sda_space_surveillance": "Shijian series, optical/radar ground network",
                },
                "counterspace_capabilities": {
                    "da_asat": {
                        "status": "OPERATIONAL",
                        "systems": ["SC-19 (KT-409 derivative)", "DN-3 (MEO/GEO capable)"],
                        "tested": "2007 (FY-1C), 2010, 2013, 2014",
                        "assessment": "LEO DA-ASAT demonstrated. MEO/GEO intercept assessed feasible.",
                    },
                    "co_orbital": {
                        "status": "OPERATIONAL",
                        "systems": ["SJ-17 (GEO inspector)", "SJ-21 (GEO RPO)", "Shijian-series"],
                        "tested": "SJ-17 RPO near GEO assets (2016+), SJ-21 relocated dead satellite (2022)",
                        "assessment": "Demonstrated ability to inspect, approach, and relocate GEO objects.",
                    },
                    "directed_energy": {
                        "status": "DEVELOPMENT/TESTING",
                        "systems": ["Ground-based laser ASAT facilities (multiple)"],
                        "assessment": "DIA: dazzle/blind LEO EO sensors by 2025, structural damage by late 2020s.",
                    },
                    "electronic_warfare": {
                        "status": "OPERATIONAL",
                        "systems": ["GPS/GNSS jammers", "SATCOM jammers"],
                        "assessment": "Demonstrated GPS jamming in South China Sea exercises.",
                    },
                    "cyber": {
                        "status": "OPERATIONAL",
                        "assessment": "APT groups have targeted satellite ground segments and defense contractors.",
                    },
                },
                "doctrine": (
                    "PLA doctrine emphasizes 'informationized warfare' and targeting "
                    "adversary C4ISR systems early in conflict. Space and counter-space "
                    "are central to 'systems destruction warfare' — degrading the "
                    "information architecture that enables US/FVEY military operations. "
                    "PLA writings explicitly identify GPS, ISR satellites, and SATCOM "
                    "as priority targets."
                ),
            },
            {
                "actor": "Russian Federation (CIS)",
                "organization": "Russian Aerospace Forces (VKS) — Space Troops (KV)",
                "threat_level": "HIGH — degraded but dangerous",
                "space_order_of_battle": {
                    "total_military_satellites": "110+ (aging, partial replacement)",
                    "isr_eo_ir": "Persona, Bars-M — limited capability (aging fleet)",
                    "isr_sar": "Kondor-FKA (limited)",
                    "sigint_elint": "Liana constellation (Lotos-S ELINT + Pion-NKS SIGINT) — 6+ sats",
                    "early_warning": "EKS/Tundra constellation — 6 satellites (HEO, IOC achieved)",
                    "navigation": "GLONASS (24 operational)",
                    "communications": "Meridian (HEO), Blagovest (GEO), military Raduga/Globus",
                    "sda_space_surveillance": "Krona optical/radar complex, Okno-M, Dunay-3U",
                },
                "counterspace_capabilities": {
                    "da_asat": {
                        "status": "OPERATIONAL",
                        "systems": ["Nudol (PL-19)", "S-500 (assessed DA-ASAT capable)"],
                        "tested": "2021 (Cosmos 1408 destruction), multiple Nudol flight tests",
                        "assessment": "Demonstrated. Cosmos 1408 test created 1632+ debris fragments.",
                    },
                    "co_orbital": {
                        "status": "OPERATIONAL",
                        "systems": ["Cosmos 2542/2543 (inspector/sub-satellite)", "Luch/Olymp (GEO SIGINT/RPO)"],
                        "tested": "Cosmos 2542 stalked USA-245 (NRO), Luch loitered near FVEY GEO assets",
                        "assessment": "Active co-orbital inspection program targeting FVEY assets.",
                    },
                    "directed_energy": {
                        "status": "OPERATIONAL (dazzle)",
                        "systems": ["Peresvet (mobile, deployed at ICBM bases)", "Kalina (under development)"],
                        "assessment": "Peresvet deployed since 2019. Dazzle capability against LEO EO sensors.",
                    },
                    "electronic_warfare": {
                        "status": "OPERATIONAL — combat-proven",
                        "systems": ["Pole-21 (GPS jammer)", "R-330Zh Zhitel", "Krasukha-2/4", "Tirada-2 (SATCOM)"],
                        "assessment": "Most mature EW capability. Combat-proven in Syria and Ukraine.",
                    },
                    "cyber": {
                        "status": "OPERATIONAL",
                        "assessment": "Viasat KA-SAT hack (Feb 2022) demonstrated space ground segment cyber attack.",
                    },
                },
                "doctrine": (
                    "Russian military doctrine views space as an 'aerospace' domain. "
                    "Counter-space is integral to initial phase operations — disrupting "
                    "adversary C4ISR before kinetic engagement. Ukraine conflict has "
                    "consumed resources and attention but counter-space development "
                    "continues. EW capabilities are most mature and combat-proven."
                ),
            },
            {
                "actor": "Democratic People's Republic of Korea (DPRK)",
                "threat_level": "LOW (space) / HIGH (ballistic missile)",
                "space_capabilities": {
                    "satellites_on_orbit": "2 (Kwangmyongsong-3 Unit 2 — non-functional, Malligyong-1 — recon attempt)",
                    "launch_vehicles": "Unha-3, Chollima-1 (Hwasong-derived)",
                    "assessment": "Very limited space capability. Primary threat is ballistic missile / SLV dual-use.",
                },
                "counterspace": "GPS jammers (demonstrated against ROK). No assessed ASAT capability.",
            },
            {
                "actor": "Islamic Republic of Iran",
                "threat_level": "LOW (space) / MODERATE (regional EW)",
                "space_capabilities": {
                    "satellites_on_orbit": "5+ (mostly non-functional or short-lived)",
                    "launch_vehicles": "Simorgh, Qased, Zuljanah",
                    "notable": "IRGC Qased launch (2020) — solid-fuel, military launcher",
                    "assessment": "Growing capability but limited. Focus on ISR and secure comms.",
                },
                "counterspace": "GPS spoofing capability (demonstrated). No assessed ASAT.",
            },
        ],
    }

    # ---- STEP 4: DETERMINE THREAT COURSES OF ACTION ----
    step_4 = {
        "step": "Step 4: Determine Threat Courses of Action",
        "most_dangerous_coa": {
            "name": "MOST DANGEROUS COA — Full Spectrum Counter-Space Attack",
            "actor": "PRC",
            "scenario": "Taiwan contingency escalation",
            "sequence": [
                {
                    "phase": "Phase 0 — Shaping (D-90 to D-7)",
                    "actions": [
                        "Reposition co-orbital inspection satellites near FVEY GEO assets",
                        "Pre-position ground-based laser ASAT systems",
                        "Conduct GPS jamming exercises in South China Sea",
                        "Cyber intrusions into satellite ground segment networks",
                        "Increase launch tempo for replacement/reserve satellites",
                    ],
                },
                {
                    "phase": "Phase 1 — Denial (D-7 to D-Day)",
                    "actions": [
                        "Activate GPS/GNSS jamming across Taiwan Strait and Western Pacific",
                        "SATCOM jamming against military UHF/SHF frequencies",
                        "Dazzle/blind LEO ISR satellites passing over Taiwan Strait",
                        "Cyber attack on satellite ground segments (Viasat-style)",
                        "Possible co-orbital interference with GEO early warning satellites",
                    ],
                },
                {
                    "phase": "Phase 2 — Destruction (D-Day if escalation)",
                    "actions": [
                        "DA-ASAT against 1-3 critical LEO ISR satellites (demonstration)",
                        "Co-orbital ASAT against GEO SATCOM (WGS, Skynet) — disable not destroy",
                        "Sustained GPS/SATCOM jamming across theater",
                        "Kinetic ASAT at LEO ISR corridor (400-600 km) — limited to minimize debris",
                    ],
                },
            ],
            "indicators_and_warnings": [
                "SJ-17/SJ-21 maneuvering toward FVEY GEO assets",
                "Unusual launch activity from Xichang/Wenchang",
                "GPS jamming exercises expanding beyond normal bounds",
                "PLA SSF/ISF units changing readiness posture",
                "Increase in cyber probing of ground segment networks",
                "Movement of mobile DA-ASAT launchers (SC-19/DN-3)",
            ],
            "fvey_impact_assessment": (
                "Catastrophic degradation of space-enabled C4ISR in Western Pacific. "
                "GPS accuracy degraded to >50m or denied. ISR revisit rate reduced 60-80%. "
                "Protected SATCOM (AEHF) likely survives but capacity insufficient for "
                "surge demand. Missile early warning (SBIRS) likely survives if GEO "
                "assets not physically attacked."
            ),
        },
        "most_likely_coa": {
            "name": "MOST LIKELY COA — Reversible Counter-Space Below Threshold",
            "actor": "PRC (primary) / Russia (secondary)",
            "scenario": "Gray-zone competition, crisis signaling",
            "sequence": [
                {
                    "phase": "Ongoing — Peacetime Competition",
                    "actions": [
                        "RPO/inspection of FVEY satellites (intelligence collection)",
                        "Localized GPS jamming during exercises",
                        "Persistent SIGINT collection from GEO SIGINT satellites",
                        "Cyber espionage targeting satellite programs and ground segments",
                        "Continued ASAT weapons development and testing",
                        "Expansion of counterspace-relevant constellations",
                    ],
                },
                {
                    "phase": "Crisis — Signaling and Coercion",
                    "actions": [
                        "Demonstrative co-orbital approach to FVEY high-value GEO asset",
                        "Expanded GPS jamming in disputed regions",
                        "Publicized ASAT-capable missile test (non-destructive)",
                        "Increased readiness of mobile ASAT launchers",
                        "Deniable cyber attack on ground segment",
                    ],
                },
            ],
            "indicators_and_warnings": [
                "Anomalous maneuvers by PRC/Russian inspector satellites",
                "Expansion of GPS jamming zones beyond training areas",
                "Adversary satellite constellation rapid replenishment launches",
                "Diplomatic signaling about space weapons capabilities",
            ],
            "fvey_impact_assessment": (
                "Gradual erosion of space domain confidence. Intelligence collection "
                "against FVEY satellites. Localized GPS/SATCOM denial in crisis zones. "
                "Below threshold of armed attack — makes response options limited. "
                "This is the most challenging COA to counter because it avoids "
                "triggering alliance commitments."
            ),
        },
    }

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Space Intelligence Preparation of the Operating Environment (IPOE)",
        "product_format": "IAW JP 2-01.3 / ADF Pub 3.0.3",
        "generated_utc": now.isoformat(),
        "valid_until": (now + timedelta(hours=24)).isoformat(),
        "producing_unit": "Echelon Vantage — Space OSINT Centre",
        "step_1_define_environment": step_1,
        "step_2_environmental_effects": step_2,
        "step_3_evaluate_threat": step_3,
        "step_4_threat_coas": step_4,
        "bottom_line_assessment": (
            "The space domain is contested across all orbital regimes. PRC is the "
            "pacing threat with the most comprehensive counter-space capability set "
            "(kinetic, co-orbital, EW, cyber, directed energy). Russia maintains "
            "dangerous capabilities, particularly in EW and co-orbital inspection, "
            "but is resource-constrained. The most likely adversary COA is persistent "
            "below-threshold counter-space activity (RPO, jamming, cyber) that erodes "
            "FVEY space advantage without triggering kinetic response. The most "
            "dangerous COA is full-spectrum counter-space attack in a Taiwan "
            "contingency, which could temporarily deny FVEY space-enabled C4ISR "
            "in the Western Pacific. Key FVEY vulnerability: reliance on a small "
            "number of high-value GEO assets for missile warning and strategic comms."
        ),
    }

    return _store("space_ipoe", result)


# =========================================================================
# 3. SATELLITE MANEUVER DETECTION INDICATORS
# =========================================================================
#
# Maneuver detection is a key competitive feature of LeoLabs and
# Slingshot Serene. While they use radar/sensor data for detection,
# we provide the analytical framework: WHAT maneuvers to watch for
# and WHY they matter from a military intelligence perspective.
#
# This is the "intelligence analyst's guide" to interpreting maneuver
# data — something no commercial platform provides.
#
# References:
# - Brian Weeden, SWF analysis of RPO events
# - Union of Concerned Scientists satellite database
# - Jonathan McDowell's orbital analysis methodology
# - COMSPOC/AGI conjunction assessment methodology
# =========================================================================

def get_maneuver_indicators() -> dict:
    """Return a comprehensive watchlist of satellite maneuver indicators.

    Each indicator describes a type of orbital behavior, what it could mean,
    how to detect it from public data, and which adversary platforms might
    exhibit it.
    """
    cached = _cached("maneuver_indicators")
    if cached is not None:
        return cached

    now = datetime.now(timezone.utc)

    indicators: List[dict] = [
        {
            "indicator_id": "MI-001",
            "name": "Unexpected Altitude Change",
            "category": "Orbit Raising/Lowering",
            "severity": "HIGH",
            "description": (
                "A satellite changes its semi-major axis (altitude) without a "
                "published operational reason. Altitude changes require delta-v "
                "and indicate intentional activity."
            ),
            "intelligence_significance": [
                "Approaching a target satellite at a different altitude",
                "Moving to a different ISR collection orbit",
                "Avoiding a conjunction event (legitimate)",
                "End-of-life disposal maneuver (legitimate for GEO)",
            ],
            "detection_method": (
                "Compare TLE/GP element semi-major axis over time. A change of "
                ">1 km in LEO or >10 km in GEO without a published conjunction "
                "avoidance maneuver is anomalous."
            ),
            "adversary_platforms_of_concern": [
                "PRC: SJ-17, SJ-21 (GEO inspectors)",
                "Russia: Cosmos 2542/2543 (LEO inspectors), Luch/Olymp (GEO)",
                "PRC: Shijian-series 'technology demonstration' satellites",
            ],
            "historical_precedent": (
                "SJ-21 raised orbit to approach and then relocated defunct Compass-GS1 "
                "BeiDou satellite to graveyard orbit (January 2022). This demonstrated "
                "an ability to manipulate GEO objects."
            ),
        },
        {
            "indicator_id": "MI-002",
            "name": "Orbital Plane Change",
            "category": "Plane Change Maneuver",
            "severity": "CRITICAL",
            "description": (
                "A satellite changes its orbital inclination or RAAN. Plane changes "
                "are the MOST EXPENSIVE maneuvers in terms of delta-v. A plane change "
                "almost always indicates intentional targeting of a specific object or "
                "region."
            ),
            "intelligence_significance": [
                "Moving into the orbital plane of a FVEY target satellite — RPO preparation",
                "Shifting ISR coverage to a new geographic region",
                "Repositioning within a constellation (may be routine)",
            ],
            "detection_method": (
                "Monitor inclination and RAAN in TLE/GP data. Any inclination change "
                ">0.1 deg or RAAN change >1 deg (beyond natural J2 precession) "
                "indicates a maneuver. Compare RAAN drift rate to expected J2 rate."
            ),
            "adversary_platforms_of_concern": [
                "PRC: Any Yaogan/Gaofen ISR satellite changing planes",
                "Russia: Cosmos 2542 (demonstrated plane change to intercept NRO satellite)",
                "PRC: SJ-17/21 adjusting GEO longitude (plane change equivalent)",
            ],
            "historical_precedent": (
                "Cosmos 2542 launched into an orbit similar to USA-245 (NRO KH-11 variant), "
                "then maneuvered to match its orbital plane. This required significant "
                "delta-v and was clearly intentional targeting."
            ),
        },
        {
            "indicator_id": "MI-003",
            "name": "Proximity Approach Sequence",
            "category": "Rendezvous and Proximity Operations (RPO)",
            "severity": "CRITICAL",
            "description": (
                "A satellite executes a series of maneuvers that progressively close "
                "the distance to another satellite. This is the hallmark of RPO — "
                "the pattern is unmistakable when seen in orbital data."
            ),
            "intelligence_significance": [
                "Intelligence collection / close-up imaging of target",
                "Testing proximity operations capability",
                "Pre-positioning for future co-orbital ASAT engagement",
                "Satellite servicing (legitimate, but dual-use)",
            ],
            "detection_method": (
                "Track relative distance between adversary and FVEY satellites over time. "
                "A monotonically decreasing distance trend over multiple orbits indicates "
                "deliberate approach. Miss distance data from conjunction screening."
            ),
            "adversary_platforms_of_concern": [
                "PRC: SJ-17 (GEO), SJ-21 (GEO), SJ-12 (LEO RPO demonstrator)",
                "Russia: Cosmos 2542/2543, Cosmos 2558 (inspector sub-satellite deployed)",
                "Russia: Luch/Olymp-K (GEO loiterer near FVEY commsats)",
            ],
            "historical_precedent": (
                "Russia's Luch (Olymp) satellite repositioned itself between Intelsat 7 "
                "and Intelsat 901 in GEO, then moved to proximity of multiple NATO/allied "
                "military SATCOM birds. Pattern repeated over several years."
            ),
        },
        {
            "indicator_id": "MI-004",
            "name": "Sub-Satellite Deployment",
            "category": "Object Release / Fragmentation",
            "severity": "CRITICAL",
            "description": (
                "A tracked satellite releases a sub-satellite or deploys an object "
                "into a nearby orbit. May appear as a new cataloged object in "
                "proximity to the parent. This is a hallmark of co-orbital ASAT "
                "testing or inspector satellite deployment."
            ),
            "intelligence_significance": [
                "Co-orbital ASAT weapon deployment",
                "Inspector/surveillance sub-satellite release",
                "Proximity operations capability demonstration",
                "Legitimate technology demonstration (must be assessed in context)",
            ],
            "detection_method": (
                "New catalog objects appearing near an existing satellite. 18th SDS "
                "catalogs new objects — check if new entries share orbital elements "
                "with known adversary platforms. Debris-like TLE near active satellite = sub-satellite."
            ),
            "adversary_platforms_of_concern": [
                "Russia: Cosmos 2519 released Cosmos 2521, which released Cosmos 2523",
                "Russia: Cosmos 2542 released Cosmos 2543 (then approached NRO satellite)",
                "PRC: SJ-21 released and recaptured sub-satellite",
                "Russia: Cosmos 2558 (inspector) launched into orbit near USA-326",
            ],
            "historical_precedent": (
                "Cosmos 2542 (launched Nov 2019) released Cosmos 2543 (sub-satellite). "
                "Cosmos 2543 then maneuvered to within km of USA-245, a US NRO satellite. "
                "In July 2020, Cosmos 2543 released a high-speed projectile — assessed as "
                "co-orbital ASAT weapon test."
            ),
        },
        {
            "indicator_id": "MI-005",
            "name": "Constellation Formation Change",
            "category": "Constellation Management",
            "severity": "MODERATE",
            "description": (
                "Multiple satellites within an adversary constellation simultaneously "
                "adjust their orbits — changing spacing, phasing, or adding new orbital "
                "planes. May indicate operational reorientation."
            ),
            "intelligence_significance": [
                "Optimizing ISR coverage over a specific region (pre-conflict indicator)",
                "Filling gaps in constellation coverage",
                "Transitioning to wartime configuration",
                "Routine constellation maintenance (must baseline normal patterns first)",
            ],
            "detection_method": (
                "Track inter-satellite phasing within known constellations (Yaogan, Liana). "
                "Changes in the angular spacing between satellites or addition of new "
                "orbital planes indicates reconfiguration."
            ),
            "adversary_platforms_of_concern": [
                "PRC: Yaogan triplet SAR/ELINT groups — phasing changes indicate targeting shift",
                "Russia: Liana constellation (Lotos/Pion) — repositioning indicates new collection priority",
                "PRC: BeiDou navigation — any unusual maneuvers could indicate military mode activation",
            ],
            "historical_precedent": (
                "PRC Yaogan triplet groups (e.g., Yaogan-16A/B/C, Yaogan-20A/B/C) maintain "
                "precise formation spacing for geolocation of RF emitters. Any change in "
                "formation spacing indicates shift in target set or collection geometry."
            ),
        },
        {
            "indicator_id": "MI-006",
            "name": "De-orbit or Graveyard Orbit Maneuver",
            "category": "End-of-Life / Disposal",
            "severity": "LOW (usually routine)",
            "description": (
                "A satellite maneuvers to a graveyard orbit (GEO+300 km) or begins "
                "de-orbit descent. Usually legitimate end-of-life, but can be used "
                "to mask satellite replacement or capability upgrade."
            ),
            "intelligence_significance": [
                "Legitimate end-of-life disposal (most common)",
                "Replacement satellite already in orbit — capability upgrade",
                "Cover for deploying a sub-satellite before disposal",
                "Deception: simulate disposal while capability remains in co-orbital sub-satellite",
            ],
            "detection_method": (
                "GEO satellites raising orbit 300+ km above GEO belt. LEO satellites "
                "lowering perigee. Compare with launch of replacement satellite."
            ),
            "adversary_platforms_of_concern": [
                "All adversary GEO satellites approaching end of design life",
                "PRC: Older Shijian-series satellites (watch for sub-satellite release before disposal)",
                "Russia: Aging Gorizont/Raduga SATCOM platforms",
            ],
            "historical_precedent": (
                "SJ-21 repositioned defunct BeiDou satellite to graveyard orbit — demonstrated "
                "ability to 'clean up' the GEO belt but also to move objects at will."
            ),
        },
        {
            "indicator_id": "MI-007",
            "name": "Rapid Orbit Lowering Near FVEY LEO Asset",
            "category": "Potential Kinetic Kill Vehicle Positioning",
            "severity": "CRITICAL",
            "description": (
                "An adversary satellite rapidly lowers its orbit to approach the "
                "altitude band of a FVEY LEO military asset. In combination with "
                "a plane change, this could indicate co-orbital ASAT positioning."
            ),
            "intelligence_significance": [
                "Pre-positioning for co-orbital engagement",
                "Close-pass intelligence collection",
                "Forced conjunction (denial-of-service by creating avoidance maneuver requirement)",
            ],
            "detection_method": (
                "Monitor adversary satellite altitude changes toward bands where FVEY "
                "military assets operate (e.g., 400-500 km NRO range, 550 km Starlink, "
                "780 km Iridium). Rapid descent (>5 km/day) is anomalous."
            ),
            "adversary_platforms_of_concern": [
                "Russia: 'Inspector' satellites (Cosmos 2558 series)",
                "PRC: SJ-12 class (LEO RPO demonstrator)",
                "Any newly cataloged object from adversary launch that approaches FVEY band",
            ],
            "historical_precedent": (
                "Cosmos 2558 was launched into an orbit very similar to USA-326 "
                "(classified NRO satellite). The launch orbit placement was so precise "
                "that it was clearly targeted at the US asset."
            ),
        },
        {
            "indicator_id": "MI-008",
            "name": "GEO Longitude Drift / Station Change",
            "category": "GEO Repositioning",
            "severity": "HIGH",
            "description": (
                "A GEO satellite abandons its assigned longitude slot and begins "
                "drifting along the GEO belt, or maneuvers to a new longitude. "
                "In GEO, longitude = geographic coverage area."
            ),
            "intelligence_significance": [
                "Shifting communications coverage to a conflict zone",
                "Moving SIGINT satellite to intercept target region SATCOM",
                "Approaching a FVEY GEO asset for RPO",
                "Routine station relocation (compare with ITU filings)",
            ],
            "detection_method": (
                "Track GEO satellite longitude from TLE/GP data. Any drift rate "
                ">0.1 deg/day or station change without ITU coordination notice "
                "is suspicious. Luch/Olymp has demonstrated this pattern repeatedly."
            ),
            "adversary_platforms_of_concern": [
                "Russia: Luch/Olymp-K (serial GEO drifter — has loitered near NATO SATCOM)",
                "PRC: SJ-17, SJ-20, TJSW series",
                "PRC: TJS-series (GEO SIGINT/EW — any drift toward FVEY SATCOM longitudes)",
            ],
            "historical_precedent": (
                "Russia's Luch (Olymp-K-1) has systematically visited multiple longitude "
                "slots in GEO, parking near Intelsat, Eutelsat, and military SATCOM "
                "satellites. The pattern indicates intelligence collection."
            ),
        },
    ]

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Satellite Maneuver Detection Indicators — Intelligence Analyst Watchlist",
        "generated_utc": now.isoformat(),
        "purpose": (
            "Provides intelligence analysts with a framework for interpreting "
            "satellite maneuver data from commercial SDA providers (LeoLabs, "
            "Slingshot, ExoAnalytic) and public catalogs (Space-Track.org). "
            "Each indicator describes WHAT to look for, WHY it matters, and "
            "HOW to detect it from open-source orbital data."
        ),
        "total_indicators": len(indicators),
        "indicators_by_severity": {
            "CRITICAL": sum(1 for i in indicators if i["severity"] == "CRITICAL"),
            "HIGH": sum(1 for i in indicators if i["severity"] == "HIGH"),
            "MODERATE": sum(1 for i in indicators if i["severity"] == "MODERATE"),
            "LOW": sum(1 for i in indicators if i["severity"] == "LOW"),
        },
        "indicators": indicators,
        "data_sources_for_detection": [
            {
                "source": "Space-Track.org (18th SDS)",
                "data": "TLE/GP elements — updated multiple times daily",
                "free": True,
                "detection_capability": "Orbit changes visible within 24-48 hours of maneuver",
            },
            {
                "source": "LeoLabs Platform",
                "data": "High-cadence radar tracking — maneuver detected within hours",
                "free": False,
                "detection_capability": "Best LEO maneuver detection. Automated alerts.",
            },
            {
                "source": "ExoAnalytic Solutions",
                "data": "Optical telescope network — GEO belt surveillance",
                "free": False,
                "detection_capability": "Best GEO RPO detection. Photometric characterization.",
            },
            {
                "source": "Slingshot Aerospace (Serene)",
                "data": "ML-augmented catalog — pattern-of-life analysis",
                "free": False,
                "detection_capability": "Automated anomaly detection and intent classification.",
            },
            {
                "source": "Jonathan McDowell / Planet4589",
                "data": "Independent analyst tracking — launch logs, orbital analysis",
                "free": True,
                "detection_capability": "Expert analysis with historical context.",
            },
            {
                "source": "CelesTrak (via this platform)",
                "data": "GP elements mirrored from Space-Track + supplementary TLEs",
                "free": True,
                "detection_capability": "Historical element comparison for maneuver detection.",
            },
        ],
    }

    return _store("maneuver_indicators", result)


# =========================================================================
# 4. SIGINT/ELINT CONSTELLATION MAPPING
# =========================================================================
#
# Specifically maps adversary signals intelligence satellites — a
# capability no commercial SDA platform provides because it requires
# intelligence analysis, not just orbital tracking.
#
# SIGINT satellites are often launched as 'technology demonstration'
# or 'experimental' missions. Identifying them requires cross-referencing
# launch vehicle, orbit characteristics, historical patterns, and
# open-source intelligence reports.
#
# References:
# - NASIC "Competing in Space" (2018)
# - DIA "Challenges to Security in Space" (2022)
# - Bart Hendrickx, "The Space Review" (Russian military satellite analysis)
# - Henri Brisson, Jonathan McDowell orbital analysis
# - Union of Concerned Scientists satellite database
# =========================================================================

def get_sigint_mapping() -> dict:
    """Map adversary SIGINT/ELINT satellite constellations.

    Returns detailed analysis of signals intelligence satellites operated
    by PRC and Russia, including capability assessments and FVEY target sets.
    """
    cached = _cached("sigint_mapping")
    if cached is not None:
        return cached

    now = datetime.now(timezone.utc)

    prc_sigint = {
        "nation": "PRC",
        "operating_organization": "PLA Information Support Force (formerly SSF Space Systems Dept)",
        "constellations": [
            {
                "name": "Shijian-6 Series (ELINT)",
                "designation": "SJ-6",
                "type": "LEO ELINT",
                "orbit": "~600 km, ~98 deg (SSO)",
                "pairs_launched": 5,
                "operational_status": "Legacy — most decommissioned, replaced by newer series",
                "launch_years": "2004-2008",
                "capability_assessment": {
                    "mission": "Electronic intelligence — intercept and geolocate radar emissions",
                    "frequency_range": "VHF through S-band (estimated)",
                    "geolocation_method": "TDOA between paired satellites",
                    "geolocation_accuracy": "~10-50 km (estimated for naval targeting)",
                    "target_sets": [
                        "Naval radar emissions (surface combatant targeting)",
                        "Air defense radar emissions",
                        "Airborne radar emissions",
                    ],
                },
                "fvey_concern_level": "LOW — aging/decommissioned but established the operational concept",
            },
            {
                "name": "Chuangxin Series (ELINT)",
                "designation": "CX-1",
                "type": "LEO ELINT (microsatellite)",
                "orbit": "~780 km, ~98.5 deg (SSO)",
                "satellites_launched": 6,
                "operational_status": "Partially operational — newer units active",
                "launch_years": "2003-2014",
                "capability_assessment": {
                    "mission": "Electronic intelligence — miniaturized ELINT payload",
                    "frequency_range": "UHF through X-band (estimated)",
                    "geolocation_method": "Single-satellite frequency/AOA measurement; constellation TDOA",
                    "geolocation_accuracy": "~20-100 km (estimated)",
                    "target_sets": [
                        "Military radar emissions",
                        "Communications emitters",
                        "Electromagnetic order of battle mapping",
                    ],
                },
                "fvey_concern_level": "MODERATE — demonstrated PRC microsatellite SIGINT capability",
            },
            {
                "name": "Yaogan Triplet Groups (ELINT/Naval Targeting)",
                "designation": "Yaogan-16/17/20/25/31 (A/B/C groups)",
                "type": "LEO ELINT — formation flying for geolocation",
                "orbit": "~1,100 km, ~63.4 deg",
                "groups_launched": 6,
                "operational_status": "OPERATIONAL — primary PRC naval ELINT constellation",
                "launch_years": "2012-present",
                "capability_assessment": {
                    "mission": "Naval SIGINT — geolocate ship radar emissions for OTH targeting",
                    "frequency_range": "L-band through X-band (naval radar frequencies)",
                    "geolocation_method": "TDOA/FDOA between three satellites in formation",
                    "geolocation_accuracy": "~1-10 km (sufficient for anti-ship ballistic missile targeting)",
                    "revisit_time": "Hours (multiple groups provide persistent coverage)",
                    "target_sets": [
                        "US Navy carrier strike group radar emissions",
                        "AEGIS radar (SPY-1/SPY-6)",
                        "Allied naval radar emissions",
                        "Shore-based radar installations",
                    ],
                },
                "fvey_concern_level": "CRITICAL — enables OTH targeting for DF-21D/DF-26 anti-ship ballistic missiles",
                "operational_note": (
                    "The Yaogan triplets are assessed as the cueing sensor for PRC anti-ship "
                    "ballistic missiles. They geolocate carrier group radar emissions to provide "
                    "targeting data for DF-21D/DF-26 ASBMs. This is the core of PRC's A2/AD "
                    "kill chain against US Navy surface forces."
                ),
            },
            {
                "name": "TJS / TJSW Series (GEO SIGINT)",
                "designation": "TJS-1/2/3/5, TJSW-1/2",
                "type": "GEO SIGINT/EW",
                "orbit": "~35,786 km, near-equatorial (GEO)",
                "satellites_launched": 6,
                "operational_status": "OPERATIONAL — growing constellation",
                "launch_years": "2015-present",
                "capability_assessment": {
                    "mission": "Geostationary SIGINT — persistent surveillance of military communications and radar",
                    "frequency_range": "UHF through Ka-band (estimated — wide coverage for GEO SIGINT)",
                    "geolocation_method": "Single-satellite AOA; possible GEO-to-LEO correlation",
                    "geolocation_accuracy": "~50-200 km from GEO (limited by geometry)",
                    "coverage": "Persistent — continuous view of assigned region from GEO",
                    "target_sets": [
                        "Military SATCOM uplinks (WGS, AEHF, Skynet)",
                        "Ground-based radar emissions (THAAD, Patriot, JORN)",
                        "Airborne communications and radar",
                        "C2 communications in Indo-Pacific",
                    ],
                },
                "fvey_concern_level": "HIGH — persistent GEO SIGINT over Indo-Pacific",
            },
        ],
    }

    russia_sigint = {
        "nation": "Russia",
        "operating_organization": "Russian Aerospace Forces (VKS) — Space Troops (KV)",
        "constellations": [
            {
                "name": "Liana Constellation (Lotos-S / Pion-NKS)",
                "type": "LEO SIGINT/ELINT",
                "components": [
                    {
                        "name": "Lotos-S (14F145)",
                        "designation": "Lotos-S1",
                        "type": "ELINT",
                        "orbit": "~900 km, ~67.1 deg",
                        "satellites_on_orbit": 4,
                        "mission": "Electronic intelligence — radar emission intercept and geolocation",
                        "frequency_range": "VHF through X-band",
                        "heritage": "Successor to Tselina-2 ELINT system",
                    },
                    {
                        "name": "Pion-NKS (14F139)",
                        "designation": "Pion-NKS",
                        "type": "SIGINT (active/passive)",
                        "orbit": "~500 km, ~67.1 deg",
                        "satellites_on_orbit": 2,
                        "mission": "Naval SIGINT — detect and geolocate ship emissions for maritime targeting",
                        "frequency_range": "Radar and communications bands",
                        "heritage": "Successor to US-PU (passive) and US-A (active radar) naval SIGINT",
                        "note": "Pion-NKS may include active radar capability for direct ship detection",
                    },
                ],
                "constellation_status": "OPERATIONAL — still building to full constellation (planned 6 total)",
                "capability_assessment": {
                    "mission": "Integrated naval SIGINT — provide targeting for anti-ship missiles",
                    "geolocation_accuracy": "~5-25 km (estimated — sufficient for cruise missile targeting)",
                    "revisit_time": "Several hours (incomplete constellation)",
                    "target_sets": [
                        "NATO naval forces — radar and communications emissions",
                        "US Navy carrier groups in Atlantic/Pacific/Mediterranean",
                        "Shore-based radar installations",
                        "Airborne radar emissions (AWACS, maritime patrol)",
                    ],
                },
                "fvey_concern_level": "HIGH — enables maritime targeting of NATO/FVEY naval forces",
                "operational_note": (
                    "Liana is the space segment of Russia's maritime reconnaissance-strike "
                    "complex. It provides cueing data for Kalibr, Tsirkon, and other anti-ship "
                    "cruise missiles. The constellation is not yet complete but provides "
                    "operationally useful coverage."
                ),
            },
            {
                "name": "Tselina-2 Legacy (ELINT)",
                "type": "LEO ELINT",
                "orbit": "~850 km, ~71 deg",
                "status": "DECOMMISSIONED — replaced by Liana/Lotos-S",
                "launched": "1984-2007 (26 satellites total)",
                "note": "Soviet-era ELINT constellation. No operational satellites remain.",
                "fvey_concern_level": "NONE — historical reference only",
            },
            {
                "name": "Luch / Olymp (GEO SIGINT/RPO)",
                "designation": "Olymp-K (14F136)",
                "type": "GEO SIGINT / proximity inspection",
                "orbit": "~35,786 km (GEO — longitude varies, drifts between targets)",
                "satellites_on_orbit": 2,
                "operational_status": "OPERATIONAL — actively repositioning in GEO belt",
                "capability_assessment": {
                    "mission": "GEO SIGINT — intercept adversary SATCOM signals at close range",
                    "method": "Parks within km of target GEO satellites for signal collection",
                    "target_sets": [
                        "NATO/FVEY military SATCOM (Skynet, Syracuse, WGS, AEHF)",
                        "Intelsat/Eutelsat commercial SATCOM (carries military traffic)",
                        "Government SATCOM of interest",
                    ],
                    "secondary_mission": "Close-approach inspection / characterization of target satellites",
                },
                "fvey_concern_level": "CRITICAL — actively operates in proximity to FVEY GEO SATCOM",
                "observed_targets": [
                    "Intelsat-7 / Intelsat-901 (2015)",
                    "Athena-Fidus (French-Italian military SATCOM) (2017)",
                    "Intelsat 36 (2019)",
                    "Multiple other GEO positions (pattern of systematic collection)",
                ],
            },
        ],
    }

    # Aggregate assessment
    total_prc_sigint = sum(
        c.get("satellites_launched", 0) or c.get("groups_launched", 0) * 3
        for c in prc_sigint["constellations"]
    )
    total_russia_sigint = sum(
        sum(comp.get("satellites_on_orbit", 0) for comp in c.get("components", [c]))
        for c in russia_sigint["constellations"]
        if c.get("status") != "DECOMMISSIONED"
    )

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Adversary SIGINT/ELINT Constellation Intelligence Map",
        "generated_utc": now.isoformat(),
        "summary": {
            "total_prc_sigint_satellites_launched": total_prc_sigint,
            "total_russia_sigint_satellites_active": total_russia_sigint,
            "highest_concern_prc": "Yaogan triplets — enable anti-ship ballistic missile targeting",
            "highest_concern_russia": "Luch/Olymp — active GEO RPO/SIGINT near FVEY SATCOM",
            "key_assessment": (
                "Both PRC and Russia maintain operational space-based SIGINT capability "
                "that directly threatens FVEY military operations. PRC's Yaogan triplets "
                "are the most operationally significant — they provide the targeting data "
                "for anti-ship ballistic missiles that threaten US Navy carrier groups. "
                "Russia's Luch/Olymp GEO SIGINT satellites represent a different but equally "
                "concerning threat — close-range signal collection against FVEY SATCOM."
            ),
            "fvey_target_sets_at_risk": [
                "Military SATCOM (uplink signals intercepted by GEO SIGINT)",
                "Naval radar emissions (geolocated by LEO ELINT for missile targeting)",
                "Air defense radar emissions (mapped for electronic order of battle)",
                "C2 communications (intercepted for intelligence collection)",
                "Airborne radar (AWACS, P-8 maritime patrol — detectable from LEO)",
            ],
            "recommended_countermeasures": [
                "Emission control (EMCON) protocols when under adversary SIGINT satellite coverage",
                "LPI/LPD waveforms for military SATCOM and radar",
                "Frequency agility and spread-spectrum for ground/naval radar",
                "Awareness of adversary SIGINT satellite pass times (this platform provides)",
                "Protected communications (AEHF EHF anti-jam, LPI waveforms)",
                "Decoy emissions and deception techniques",
            ],
        },
        "prc_sigint_constellation": prc_sigint,
        "russia_sigint_constellation": russia_sigint,
    }

    return _store("sigint_mapping", result)


# =========================================================================
# 5. SPACE DEBRIS ENVIRONMENT ASSESSMENT
# =========================================================================
#
# Comprehensive debris environment statistics — goes beyond what any
# single commercial provider offers by combining catalog data with
# historical analysis, risk assessment, and FVEY operational impact.
#
# LeoLabs provides debris tracking (their strength). We provide the
# CONTEXT — what the debris environment means for FVEY operations.
#
# References:
# - ESA Space Debris Office — Annual Space Environment Report
# - NASA Orbital Debris Program Office (ODPO) — Orbital Debris Quarterly News
# - ESA DISCOS database
# - 18th SDS Satellite Catalog statistics
# - Kessler (1978) original cascade paper
# - Liou & Johnson (2009) instability analysis
# =========================================================================

def get_debris_environment() -> dict:
    """Return comprehensive space debris environment assessment.

    Includes total tracked objects, distribution by regime, historical
    growth, conjunction statistics, most dangerous altitude bands,
    and FVEY operational impact assessment.
    """
    cached = _cached("debris_environment")
    if cached is not None:
        return cached

    now = datetime.now(timezone.utc)

    # Current catalog statistics (based on latest published data ~2026)
    catalog_stats = {
        "as_of": "March 2026 (approximate — based on published tracking data)",
        "total_tracked_objects": {
            "value": 44500,
            "note": "Objects tracked by 18th SDS / Space Fence, >10 cm in LEO",
        },
        "by_size_category": [
            {
                "category": "Tracked (>10 cm in LEO, >1 m in GEO)",
                "count": 44500,
                "trackable_by": "Space Surveillance Network (SSN), Space Fence, GEODSS",
            },
            {
                "category": "Lethal non-trackable (1-10 cm)",
                "count": 1100000,
                "note": "Estimated from statistical models (ESA MASTER, NASA ORDEM)",
                "threat": "Can destroy any operational satellite. Cannot be tracked or avoided.",
            },
            {
                "category": "Small debris (1 mm - 1 cm)",
                "count": 130000000,
                "note": "Statistical estimate — paint flakes, slag particles, micrometeorites",
                "threat": "Can damage solar panels, optics, thermal blankets. Not individually trackable.",
            },
        ],
        "by_object_type": [
            {"type": "Active satellites", "count": 10500, "percentage": 23.6},
            {"type": "Defunct satellites", "count": 5100, "percentage": 11.5},
            {"type": "Rocket bodies", "count": 2400, "percentage": 5.4},
            {"type": "Mission-related debris", "count": 3800, "percentage": 8.5},
            {"type": "Fragmentation debris", "count": 22700, "percentage": 51.0},
        ],
    }

    by_regime = [
        {
            "regime": "Low Earth Orbit (LEO) — 160-2,000 km",
            "tracked_objects": 34500,
            "percentage_of_catalog": 77.5,
            "active_satellites": 8900,
            "debris_objects": 25600,
            "debris_density_trend": "INCREASING — mega-constellations adding thousands of objects",
            "conjunction_rate": "~30-50 close-approach warnings per day in LEO",
            "note": (
                "LEO is the most congested regime. Starlink alone accounts for ~6,500 active "
                "satellites. FY-1C (2007) and Cosmos 1408 (2021) debris dominate fragmentation debris."
            ),
        },
        {
            "regime": "Medium Earth Orbit (MEO) — 2,000-35,000 km",
            "tracked_objects": 2200,
            "percentage_of_catalog": 4.9,
            "active_satellites": 120,
            "debris_objects": 2080,
            "debris_density_trend": "STABLE — limited activity, Van Allen belts limit use",
            "conjunction_rate": "Rare — low object density",
            "note": (
                "MEO is relatively sparse. GPS, Galileo, BeiDou, GLONASS navigation "
                "constellations are the primary occupants. Debris from ASAT tests has not "
                "significantly affected MEO."
            ),
        },
        {
            "regime": "Geostationary Orbit (GEO) — ~35,786 km",
            "tracked_objects": 4200,
            "percentage_of_catalog": 9.4,
            "active_satellites": 560,
            "debris_objects": 3640,
            "debris_density_trend": "SLOWLY INCREASING — old satellites not properly disposed",
            "conjunction_rate": "Low but high-consequence — limited maneuvering fuel for avoidance",
            "note": (
                "GEO is the most valuable orbital real estate. ~25% of defunct GEO satellites "
                "were NOT moved to graveyard orbit. GEO debris is permanent — no atmospheric drag."
            ),
        },
        {
            "regime": "Highly Elliptical Orbit (HEO) and other",
            "tracked_objects": 3600,
            "percentage_of_catalog": 8.1,
            "active_satellites": 120,
            "debris_objects": 3480,
            "note": "Includes Molniya orbits, GTO transfer stage debris, and miscellaneous.",
        },
    ]

    # Historical growth
    historical_growth = [
        {"year": 1960, "tracked_objects": 60, "note": "Dawn of space age"},
        {"year": 1970, "tracked_objects": 2000, "note": ""},
        {"year": 1980, "tracked_objects": 5000, "note": ""},
        {"year": 1990, "tracked_objects": 7500, "note": ""},
        {"year": 2000, "tracked_objects": 9500, "note": ""},
        {"year": 2007, "tracked_objects": 12000, "note": "Pre-FY-1C ASAT test"},
        {"year": 2008, "tracked_objects": 15500, "note": "Post-FY-1C — 3,400+ new fragments"},
        {"year": 2009, "tracked_objects": 18000, "note": "Cosmos 2251/Iridium 33 collision — 2,300+ new fragments"},
        {"year": 2010, "tracked_objects": 19000, "note": ""},
        {"year": 2015, "tracked_objects": 21000, "note": ""},
        {"year": 2019, "tracked_objects": 23000, "note": "India Mission Shakti ASAT (low debris impact)"},
        {"year": 2020, "tracked_objects": 27500, "note": "Mega-constellation era begins (Starlink)"},
        {"year": 2021, "tracked_objects": 31000, "note": "Russia Cosmos 1408 ASAT — 1,600+ new fragments"},
        {"year": 2022, "tracked_objects": 34000, "note": "Starlink and OneWeb deployment accelerating"},
        {"year": 2023, "tracked_objects": 37000, "note": "Space Fence tracking smaller objects"},
        {"year": 2024, "tracked_objects": 40000, "note": "Continued mega-constellation growth"},
        {"year": 2025, "tracked_objects": 42500, "note": ""},
        {"year": 2026, "tracked_objects": 44500, "note": "Current estimate"},
    ]

    # Most dangerous altitude bands
    dangerous_altitudes = [
        {
            "altitude_band_km": "750-900",
            "danger_level": "EXTREME",
            "primary_debris_source": "Fengyun-1C (FY-1C) ASAT test (2007)",
            "debris_objects": 3400,
            "debris_remaining_percent": 82,
            "orbital_lifetime": "Decades to centuries",
            "fvey_assets_at_risk": [
                "Iridium NEXT (780 km) — EMSS military communications",
                "Planet Dove constellation (occasional passes)",
                "NRO classified SSO satellites (some in this band)",
            ],
            "assessment": (
                "The FY-1C debris cloud remains the largest single source of tracked "
                "debris in orbit. It has spread into a shell of debris fragments that "
                "will persist for decades. Any satellite operating in this band faces "
                "elevated collision risk. This band is the strongest argument for an "
                "international ban on DA-ASAT testing."
            ),
        },
        {
            "altitude_band_km": "400-550",
            "danger_level": "HIGH",
            "primary_debris_source": "Cosmos 1408 ASAT test (2021) + Cosmos 2251/Iridium collision (2009, debris descending)",
            "debris_objects": 2500,
            "debris_remaining_percent": 45,
            "orbital_lifetime": "1-5 years (decaying due to atmospheric drag)",
            "fvey_assets_at_risk": [
                "ISS (420 km) — forced crew shelter-in-place multiple times",
                "Starlink Gen 1 (550 km) — largest constellation in this band",
                "CSS/Tiangong (390 km)",
            ],
            "assessment": (
                "Cosmos 1408 debris initially forced ISS crew to shelter. Fragments are "
                "decaying but will take years to fully clear. Starlink operates in this band "
                "with active collision avoidance. This band demonstrates that even 'low altitude' "
                "ASAT tests create years of risk for crewed spaceflight."
            ),
        },
        {
            "altitude_band_km": "950-1050",
            "danger_level": "HIGH",
            "primary_debris_source": "Legacy debris — Cosmos-Iridium fragments (ascended), various breakup events",
            "debris_objects": 1800,
            "orbital_lifetime": "Centuries (effectively permanent)",
            "fvey_assets_at_risk": [
                "Starlink Gen 2 (some shells at 1,150 km)",
                "Various NRO/classified SSO missions",
            ],
            "assessment": (
                "The 950-1050 km band has accumulated debris from multiple sources over decades. "
                "At this altitude, atmospheric drag is negligible — debris persists indefinitely. "
                "This is one of the bands where Kessler syndrome risk is highest."
            ),
        },
        {
            "altitude_band_km": "35,586-35,986",
            "danger_level": "MODERATE",
            "primary_debris_source": "Defunct GEO satellites not properly disposed, GEO breakup events",
            "debris_objects": 3600,
            "orbital_lifetime": "Permanent (no atmospheric drag at GEO)",
            "fvey_assets_at_risk": [
                "All FVEY GEO military SATCOM (WGS, AEHF, MUOS, Skynet)",
                "SBIRS GEO missile early warning",
                "GSSAP space surveillance",
            ],
            "assessment": (
                "GEO debris density is lower than LEO but each piece is permanent. "
                "~25% of end-of-life GEO satellites were NOT properly disposed. "
                "The narrow GEO ring concentrates all objects into a thin band. "
                "A single breakup event in GEO could deny entire longitude sectors."
            ),
        },
    ]

    # Conjunction statistics
    conjunction_stats = {
        "estimated_close_approach_warnings_per_day": "30-50 (LEO, <1 km miss distance)",
        "estimated_collision_avoidance_maneuvers_per_week": "10-20 (all operators combined)",
        "starlink_avoidance_maneuvers_2025": "~50,000 (estimated — SpaceX autonomous system)",
        "iss_avoidance_maneuvers_2025": "~3-5 per year",
        "note": (
            "Conjunction screening by 18th SDS issues ~20,000 close-approach notifications "
            "per day to satellite operators. The vast majority do not require action, but "
            "the volume is growing exponentially with catalog size."
        ),
    }

    # Kessler syndrome assessment
    kessler_assessment = {
        "current_risk": "ELEVATED — some altitude bands may already be above critical density",
        "most_at_risk_bands_km": ["750-900", "950-1050"],
        "assessment": (
            "Donald Kessler's 1978 prediction of a self-sustaining debris cascade "
            "(where collision-generated fragments create more collisions) may already "
            "be occurring in the 750-900 km band. NASA/ESA models show this band is "
            "at or near the critical spatial density threshold. Without active debris "
            "removal (ADR), the debris population in this band will grow even without "
            "any new launches or explosions. A single additional ASAT test in this band "
            "would almost certainly trigger irreversible cascade."
        ),
        "active_debris_removal_status": [
            {
                "program": "ESA ClearSpace-1",
                "target": "Vespa upper stage",
                "status": "In development — launch planned ~2026-2027",
                "note": "First dedicated debris removal mission",
            },
            {
                "program": "Astroscale ADRAS-J",
                "target": "Japanese H-2A upper stage",
                "status": "In orbit — conducting approach and inspection (2024)",
                "note": "Demonstrating RPO capabilities for debris removal",
            },
            {
                "program": "DARPA/Northrop Grumman MEV",
                "target": "GEO life extension",
                "status": "OPERATIONAL — MEV-1 docked with Intelsat 901 (2020)",
                "note": "Demonstrated GEO satellite servicing (life extension, not removal)",
            },
        ],
    }

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Space Debris Environment Assessment",
        "generated_utc": now.isoformat(),
        "summary": {
            "total_tracked_objects": catalog_stats["total_tracked_objects"]["value"],
            "total_estimated_lethal_debris": 1100000,
            "total_estimated_small_debris": 130000000,
            "dominant_debris_source": "Fragmentation events (ASAT tests + accidental collisions)",
            "most_dangerous_band": "750-900 km (FY-1C debris — effectively permanent)",
            "kessler_syndrome_status": kessler_assessment["current_risk"],
            "trend": "WORSENING — tracked objects growing ~10-15% per year",
            "fvey_key_concern": (
                "FY-1C debris field at 750-900 km threatens Iridium NEXT (780 km), "
                "the backbone of military mobile SATCOM (EMSS). The debris environment "
                "constrains future constellation deployment options and increases "
                "operational cost of collision avoidance maneuvers."
            ),
        },
        "catalog_statistics": catalog_stats,
        "distribution_by_regime": by_regime,
        "historical_growth": historical_growth,
        "most_dangerous_altitude_bands": dangerous_altitudes,
        "conjunction_statistics": conjunction_stats,
        "kessler_syndrome_assessment": kessler_assessment,
    }

    return _store("debris_environment", result)


# =========================================================================
# 6. CISLUNAR AWARENESS
# =========================================================================
#
# Cislunar space (beyond GEO to lunar distance) is the emerging
# contested domain. PRC has active hardware at the Moon (Chang'e-4
# on the far side, Chang'e-6 sample return completed, ILRS planned).
# NASA Artemis program is the FVEY response.
#
# No commercial SDA platform provides cislunar tracking or awareness.
# This is a MAJOR gap in the global space surveillance architecture.
# AFRL CHPS program and Lockheed Martin LINUSS are early efforts.
#
# References:
# - AFRL Cislunar Highway Patrol System (CHPS) — SBIR
# - Lockheed Martin LINUSS (Lunar Infrared Networking and Surveillance System)
# - NASA Artemis Program documentation
# - PRC ILRS (International Lunar Research Station) plans
# - CNSA Chang'e program status
# - ESA Moonlight programme (lunar comm/nav)
# =========================================================================

def get_cislunar_status() -> dict:
    """Return comprehensive cislunar space domain awareness status.

    Tracks all known objects and planned missions beyond GEO,
    including PRC lunar program, NASA Artemis, and emerging
    cislunar surveillance capabilities.
    """
    cached = _cached("cislunar_status")
    if cached is not None:
        return cached

    now = datetime.now(timezone.utc)

    # Known objects/hardware beyond GEO
    active_cislunar_objects = [
        {
            "name": "Chang'e-4 Lander + Yutu-2 Rover",
            "operator": "CNSA (PRC)",
            "location": "Lunar far side — Von Karman crater",
            "status": "OPERATIONAL (since Jan 2019)",
            "mission": "Lunar far side exploration, radio astronomy",
            "military_relevance": (
                "Demonstrates PRC ability to operate on the lunar far side. "
                "Queqiao relay satellite at Earth-Moon L2 demonstrates cislunar "
                "communications capability."
            ),
        },
        {
            "name": "Queqiao-1 Relay Satellite",
            "operator": "CNSA (PRC)",
            "location": "Earth-Moon L2 halo orbit",
            "status": "OPERATIONAL",
            "mission": "Communications relay for Chang'e-4 far side operations",
            "military_relevance": (
                "First operational satellite at Earth-Moon L2. Demonstrates "
                "PRC cislunar operations capability and communications relay "
                "infrastructure beyond GEO. L2 is a strategically significant "
                "location for lunar operations."
            ),
        },
        {
            "name": "Queqiao-2 Relay Satellite",
            "operator": "CNSA (PRC)",
            "location": "Frozen orbit around the Moon (elliptical lunar orbit)",
            "status": "OPERATIONAL (launched March 2024)",
            "mission": "Next-gen relay for Chang'e-6/7/8 and ILRS",
            "military_relevance": (
                "Expanded PRC cislunar communications infrastructure. Supports "
                "future ILRS base construction. Dual-use for any PRC cislunar activity."
            ),
        },
        {
            "name": "Chang'e-5 Orbiter (residual)",
            "operator": "CNSA (PRC)",
            "location": "Sun-Earth L1 (extended mission)",
            "status": "EXTENDED MISSION — solar observation",
            "mission": "Repurposed for solar wind observation at SE-L1",
            "military_relevance": "LOW — scientific repurposing, but demonstrates cislunar maneuver capability",
        },
        {
            "name": "Chang'e-6 (sample return completed)",
            "operator": "CNSA (PRC)",
            "location": "Mission complete — far side sample return (June 2024)",
            "status": "MISSION COMPLETE",
            "mission": "First-ever lunar far side sample return",
            "military_relevance": (
                "Demonstrated precision landing on far side, ascent from lunar surface, "
                "rendezvous in lunar orbit, and return to Earth. Full cislunar round-trip "
                "capability proven."
            ),
        },
        {
            "name": "CAPSTONE",
            "operator": "NASA (US)",
            "location": "Near Rectilinear Halo Orbit (NRHO) around Moon",
            "status": "OPERATIONAL (pathfinder for Gateway)",
            "mission": "Validate NRHO for Gateway station",
            "military_relevance": (
                "Pathfinder for Artemis Gateway station. NRHO is the planned location "
                "for the first permanent human habitation beyond LEO."
            ),
        },
        {
            "name": "Korea Pathfinder Lunar Orbiter (KPLO / Danuri)",
            "operator": "KARI (South Korea)",
            "location": "Lunar orbit (~100 km altitude)",
            "status": "OPERATIONAL (since Dec 2022)",
            "mission": "Lunar mapping, resource survey, technology demonstration",
            "military_relevance": "LOW — scientific mission, but demonstrates allied cislunar capability",
        },
        {
            "name": "Chandrayaan-3 Lander (Vikram) + Rover (Pragyan)",
            "operator": "ISRO (India)",
            "location": "Lunar south pole — Manzinus C region",
            "status": "DORMANT (landed Aug 2023, one lunar day of operations)",
            "mission": "Lunar south pole landing demonstration",
            "military_relevance": "LOW — but demonstrates Quad partner cislunar capability",
        },
        {
            "name": "SLIM (Smart Lander for Investigating Moon)",
            "operator": "JAXA (Japan)",
            "location": "Lunar surface — Shioli crater",
            "status": "DORMANT (landed Jan 2024, limited post-landing operations)",
            "mission": "Precision lunar landing demonstration",
            "military_relevance": "LOW — Japanese precision landing capability demonstration",
        },
        {
            "name": "Various GRAIL/LRO/etc residual (US)",
            "operator": "NASA (US)",
            "location": "Lunar orbit",
            "status": "LRO still operational in lunar orbit",
            "mission": "Lunar Reconnaissance Orbiter — mapping, science",
            "military_relevance": "Provides high-resolution lunar surface imagery — dual-use for site planning",
        },
    ]

    # Planned cislunar missions
    planned_missions = [
        {
            "name": "Artemis II",
            "operator": "NASA (US) — crewed",
            "planned_date": "Late 2025 / 2026",
            "mission": "First crewed flight around the Moon since Apollo 17 (1972)",
            "orbit": "Free-return lunar trajectory",
            "significance": "Returns US crewed capability to cislunar space",
        },
        {
            "name": "Artemis III",
            "operator": "NASA (US) — crewed lunar landing",
            "planned_date": "2026-2027",
            "mission": "First crewed lunar landing since 1972 — south pole",
            "orbit": "NRHO + SpaceX Starship HLS descent to surface",
            "significance": "Re-establishes US human presence on lunar surface",
        },
        {
            "name": "Gateway Station (PPE + HALO)",
            "operator": "NASA + ESA + CSA + JAXA",
            "planned_date": "2027-2028 (initial modules)",
            "mission": "Permanent crewed station in NRHO around Moon",
            "orbit": "Near Rectilinear Halo Orbit (NRHO) — 6.5-day period",
            "significance": (
                "First permanent human habitation beyond LEO. Allied international "
                "partnership (US, ESA, Canada, Japan). PRC and Russia NOT participating — "
                "building competing ILRS instead."
            ),
        },
        {
            "name": "Chang'e-7",
            "operator": "CNSA (PRC)",
            "planned_date": "~2026",
            "mission": "Lunar south pole exploration — orbiter, lander, rover, hopper",
            "orbit": "Lunar polar orbit + surface operations",
            "significance": "PRC south pole exploration — precursor to ILRS base",
        },
        {
            "name": "Chang'e-8",
            "operator": "CNSA (PRC)",
            "planned_date": "~2028",
            "mission": "Technology verification for ILRS — in-situ resource utilization (ISRU)",
            "orbit": "Lunar surface — south pole region",
            "significance": "Critical step toward PRC permanent lunar base",
        },
        {
            "name": "International Lunar Research Station (ILRS)",
            "operator": "CNSA (PRC) + Roscosmos (Russia) + partners",
            "planned_date": "2028-2035 (phased construction)",
            "mission": "Permanent robotic then crewed lunar base",
            "orbit": "Lunar south pole surface",
            "partners": ["China", "Russia", "Pakistan", "UAE", "South Africa", "Egypt", "Belarus", "Venezuela"],
            "significance": (
                "PRC-Russia led alternative to Artemis/Gateway. Represents strategic "
                "bifurcation of cislunar space governance. ILRS partner list notably "
                "includes no Western/FVEY nations."
            ),
        },
        {
            "name": "ESA Moonlight",
            "operator": "ESA",
            "planned_date": "2027-2028",
            "mission": "Lunar communications and navigation constellation",
            "orbit": "Lunar orbit — multiple satellites",
            "significance": "Infrastructure for sustained lunar operations — communications and PNT",
        },
    ]

    # Lagrange point assessment
    lagrange_points = [
        {
            "point": "Earth-Moon L1",
            "location": "~58,000 km from Moon, on Earth-Moon line (Earth side)",
            "known_objects": "None currently (historically: ARTEMIS P1/P2 — NASA, transited through)",
            "strategic_significance": (
                "Midpoint between Earth and Moon. Excellent location for cislunar "
                "surveillance — can observe traffic between Earth and Moon. Gateway "
                "between Earth-dominated and Moon-dominated space."
            ),
            "surveillance_gap": "TOTAL — no persistent surveillance capability",
        },
        {
            "point": "Earth-Moon L2",
            "location": "~64,500 km beyond Moon (far side)",
            "known_objects": "Queqiao-1 (PRC — communications relay)",
            "strategic_significance": (
                "Only location that provides line-of-sight to lunar far side AND Earth. "
                "PRC has ONLY operational asset here (Queqiao-1). Strategically valuable "
                "for far side lunar operations."
            ),
            "surveillance_gap": "NEAR-TOTAL — only PRC has operational asset",
        },
        {
            "point": "Sun-Earth L1",
            "location": "~1.5 million km from Earth toward Sun",
            "known_objects": "SOHO, ACE, DSCOVR, Aditya-L1 (India), Chang'e-5 orbiter (PRC)",
            "strategic_significance": (
                "Solar observation point. Also demonstrates deep-space operations "
                "capability. Chang'e-5 presence shows PRC Lagrange point operations."
            ),
            "surveillance_gap": "LOW concern — solar observation, far from Moon",
        },
        {
            "point": "Sun-Earth L2",
            "location": "~1.5 million km from Earth away from Sun",
            "known_objects": "James Webb Space Telescope, ESA Gaia, ESA Euclid",
            "strategic_significance": (
                "Premier deep-space observatory location. JWST is a US/FVEY strategic "
                "asset for space science. Demonstrates precision operations at L2."
            ),
            "surveillance_gap": "LOW concern — astronomical, but demonstrates L-point ops capability",
        },
    ]

    # Cislunar surveillance gap assessment
    surveillance_gaps = {
        "current_capability": {
            "earth_based_tracking_limit": "~GEO + 10,000 km (reliable), ~100,000 km (theoretical maximum for SSN)",
            "cislunar_tracking": "VIRTUALLY NONE — no persistent surveillance beyond GEO belt",
            "lunar_orbit_tracking": "NONE — no capability to track objects in lunar orbit",
            "deep_space_network": "Can track cooperative spacecraft (those with transponders) only",
        },
        "gap_assessment": (
            "The cislunar surveillance gap is the SINGLE LARGEST gap in the global "
            "space domain awareness architecture. There is no persistent capability to "
            "detect, track, or characterize non-cooperative objects beyond GEO. "
            "This means an adversary could maneuver assets in cislunar space with "
            "no visibility to FVEY. As PRC expands lunar operations (Chang'e-7/8, ILRS), "
            "this gap becomes increasingly dangerous."
        ),
        "programs_to_close_gap": [
            {
                "program": "AFRL Cislunar Highway Patrol System (CHPS)",
                "agency": "US Air Force Research Laboratory",
                "status": "DEVELOPMENT — SBIR/STTR contracts awarded",
                "target_date": "Late 2020s",
                "approach": "Space-based cislunar surveillance satellite(s)",
            },
            {
                "program": "Lockheed Martin LINUSS",
                "agency": "Lockheed Martin (commercial)",
                "status": "CONCEPT/PROPOSAL",
                "approach": "Lunar Infrared Networking and Surveillance System — IR detection of cislunar objects",
            },
            {
                "program": "DARPA NOM4D",
                "agency": "DARPA",
                "status": "RESEARCH",
                "approach": "Novel Orbital Moon Manufacturing, Materials, and Mass-efficient Design",
            },
            {
                "program": "UK MOD Tyche",
                "agency": "UK Ministry of Defence",
                "status": "STUDY PHASE",
                "approach": "Cislunar space domain awareness concept study",
            },
            {
                "program": "AUKUS Cislunar Cooperation",
                "agency": "AUKUS Pillar II",
                "status": "EARLY DISCUSSION",
                "approach": "Trilateral cislunar SDA data sharing and capability development",
            },
        ],
        "recommendation": (
            "FVEY must accelerate cislunar surveillance capability. PRC will have "
            "significant cislunar infrastructure (relay satellites, orbiters, surface "
            "bases) by 2030. Without surveillance, FVEY will have no visibility into "
            "PRC cislunar operations — including potential dual-use military activities. "
            "CHPS and allied programs must be prioritized."
        ),
    }

    # Strategic bifurcation
    strategic_bifurcation = {
        "artemis_bloc": {
            "framework": "Artemis Accords",
            "led_by": "United States",
            "members": "43 signatory nations (as of 2025)",
            "key_partners": ["US", "UK", "Canada", "Australia", "Japan", "ESA members", "South Korea", "India"],
            "cislunar_plans": "Gateway station + Artemis lunar landings + ESA Moonlight",
        },
        "ilrs_bloc": {
            "framework": "International Lunar Research Station (ILRS)",
            "led_by": "China (PRC) and Russia",
            "members": ["China", "Russia", "Pakistan", "UAE", "South Africa", "Egypt", "Belarus", "Venezuela"],
            "cislunar_plans": "ILRS permanent base + relay infrastructure + resource utilization",
        },
        "assessment": (
            "Cislunar space governance is bifurcating into two competing blocs: "
            "Artemis (US-led, FVEY + allies) and ILRS (PRC-Russia led). This mirrors "
            "the broader great power competition pattern. The two blocs have different "
            "governance frameworks, different lunar base locations, and no cooperation "
            "mechanism. Risk of cislunar incidents increases as both blocs expand "
            "operations without shared rules of the road."
        ),
    }

    result = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Cislunar Space Domain Awareness Assessment",
        "generated_utc": now.isoformat(),
        "summary": {
            "total_known_cislunar_objects": len(active_cislunar_objects),
            "prc_cislunar_assets": sum(1 for o in active_cislunar_objects if "PRC" in o.get("operator", "")),
            "fvey_allied_cislunar_assets": sum(
                1 for o in active_cislunar_objects
                if any(n in o.get("operator", "") for n in ("NASA", "US", "JAXA", "Japan", "KARI", "Korea", "ISRO", "India"))
            ),
            "surveillance_capability": "VIRTUALLY NONE — critical gap",
            "strategic_trend": "PRC building cislunar infrastructure faster than FVEY",
            "key_concern": (
                "PRC has the ONLY operational asset at Earth-Moon L2 (Queqiao relay). "
                "PRC Chang'e program is ahead of schedule relative to Artemis. FVEY has "
                "no persistent cislunar surveillance. By 2030, PRC may have significant "
                "cislunar infrastructure that FVEY cannot observe."
            ),
        },
        "active_cislunar_objects": active_cislunar_objects,
        "planned_cislunar_missions": planned_missions,
        "lagrange_point_assessment": lagrange_points,
        "cislunar_surveillance_gap": surveillance_gaps,
        "strategic_bifurcation": strategic_bifurcation,
    }

    return _store("cislunar_status", result)
