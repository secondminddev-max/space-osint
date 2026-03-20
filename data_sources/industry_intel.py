"""
Space Industry Intelligence — Defense Contractors, Contracts, Supply Chain & Trends
=====================================================================================

Comprehensive structured intelligence database of the global space defense industrial
base covering US prime contractors, allied/partner nation industry, adversary state
enterprises, major contract programs, supply chain vulnerabilities, R&D funding
programs, and macroeconomic industry trends.

Compiled from open-source reporting:
- US DoD contract announcements (defense.gov)
- SAM.gov federal procurement data
- USAspending.gov obligation data
- SBIR.gov awards database
- Congressional Research Service reports (CRS)
- GAO audits and procurement assessments
- UK MOD Defence Equipment Plan / DSIS
- Australian Integrated Investment Program / DSR 2024
- NATO procurement bulletins
- CSIS Aerospace Security Project reports
- Bryce Tech / SpaceWorks small satellite surveys
- Euroconsult market reports
- SpaceNews / Defense One / Breaking Defense reporting
- Company 10-K/10-Q filings (Lockheed Martin, Northrop Grumman, RTX, L3Harris, Boeing)
- AUKUS Pillar II Advanced Capabilities announcements
- Space Foundation "The Space Report" (2024, 2025)
- DARPA / DIU program announcements
- AFRL technology roadmaps

Classification: UNCLASSIFIED // OSINT // REL TO FVEY
"""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

# ---------------------------------------------------------------------------
# Cache infrastructure — 3600-second (1-hour) TTL
# ---------------------------------------------------------------------------
_cache: Dict[str, dict] = {}
_INDUSTRY_TTL = 3600


def _cached(key: str) -> Optional[dict]:
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < _INDUSTRY_TTL:
        return entry["data"]
    return None


def _store(key: str, data: dict) -> dict:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# ---------------------------------------------------------------------------
# Classification & metadata helpers
# ---------------------------------------------------------------------------
_CLASSIFICATION = "UNCLASSIFIED // OSINT // REL TO FVEY"
_GENERATED_AT = lambda: datetime.now(timezone.utc).isoformat()


def _wrap(section: str, data: Any) -> dict:
    return {
        "classification": _CLASSIFICATION,
        "section": section,
        "generated_at": _GENERATED_AT(),
        **({section: data} if isinstance(data, list) else data),
    }


# ===========================================================================
#  1. DEFENSE CONTRACTORS DATABASE (28+ entries)
# ===========================================================================

_US_PRIMES: List[dict] = [
    {
        "name": "Lockheed Martin Space",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Littleton, CO",
        "space_revenue_usd": "12.6B",
        "total_revenue_usd": "67.6B",
        "employees": 122000,
        "key_programs": [
            "GPS III/IIIF satellites",
            "Next-Gen OPIR (missile warning)",
            "AEHF/EPS (protected SATCOM)",
            "Orion MPCV (deep space crew vehicle)",
            "SBIRS (Space Based Infrared System)",
            "A2100 / LM2100 satellite bus",
            "Space Fence radar (Kwajalein)",
            "Fleet Ballistic Missile (Trident II D5)",
        ],
        "space_capabilities": [
            "Missile warning satellites",
            "Protected military SATCOM",
            "GPS navigation satellites",
            "Space situational awareness radars",
            "Human spaceflight vehicles",
            "Hypersonic glide vehicle integration",
        ],
        "fvey_relevance": "critical",
        "notes": (
            "Largest US defense contractor and space prime. Sole-source provider for "
            "GPS III, OPIR missile warning, and AEHF protected SATCOM. Space division "
            "headquartered at the Waterton Canyon campus near Denver. Key integrator "
            "for US nuclear command, control, and communications (NC3) space segment."
        ),
    },
    {
        "name": "Northrop Grumman Space Systems",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Dulles, VA",
        "space_revenue_usd": "11.2B",
        "total_revenue_usd": "39.3B",
        "employees": 95000,
        "key_programs": [
            "James Webb Space Telescope (prime)",
            "Ground Based Strategic Deterrent (Sentinel ICBM)",
            "SDA Tranche transport/tracking layers",
            "Cygnus ISS resupply",
            "B-21 Raider (space-adjacent ISR integration)",
            "MEV / Mission Robotic Vehicle (on-orbit servicing)",
            "Missile Defense Agency kill vehicle integration",
            "Pegasus / Minotaur launch vehicles",
        ],
        "space_capabilities": [
            "On-orbit servicing and life extension",
            "Solid rocket motors (Castor, BATES)",
            "Space launch vehicles",
            "Large space structures and optics",
            "Strategic missile systems",
            "Proliferated LEO constellation manufacturing",
        ],
        "fvey_relevance": "critical",
        "notes": (
            "Acquired Orbital ATK in 2018, gaining solid rocket motor and small launch "
            "vehicle capability. Only company operating commercial on-orbit servicing "
            "(MEV-1, MEV-2 extending Intelsat GEO satellites). Major SDA Tranche "
            "contractor for proliferated LEO missile tracking/transport layers."
        ),
    },
    {
        "name": "Boeing Defense, Space & Security",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Arlington, VA",
        "space_revenue_usd": "7.8B",
        "total_revenue_usd": "66.5B",
        "employees": 171000,
        "key_programs": [
            "WGS (Wideband Global SATCOM)",
            "SBIRs legacy constellation (GEO missile warning)",
            "CST-100 Starliner crew vehicle",
            "SLS core stage / upper stage (Artemis)",
            "X-37B Orbital Test Vehicle (OTV)",
            "GPS OCX ground control system",
            "KC-46 / P-8 (space-adjacent ISR platforms)",
            "Phantom Works advanced space R&D",
        ],
        "space_capabilities": [
            "Military SATCOM buses (702HP, 702SP)",
            "Human spaceflight capsules",
            "Heavy-lift launch vehicle stages",
            "Autonomous spaceplane operations",
            "Ground control segment integration",
            "GEO platform manufacturing",
        ],
        "fvey_relevance": "critical",
        "notes": (
            "Legacy space prime with deep GEO satellite bus heritage. GPS OCX ground "
            "control system has faced significant cost/schedule overruns (GAO). X-37B "
            "autonomous spaceplane operated by USSF for classified on-orbit experiments. "
            "Starliner crewed flight capability reached IOC in 2024."
        ),
    },
    {
        "name": "RTX (Raytheon Technologies) — Space & Airborne Systems",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Arlington, VA",
        "space_revenue_usd": "5.4B",
        "total_revenue_usd": "68.9B",
        "employees": 185000,
        "key_programs": [
            "Next-Gen OPIR (sensor payload provider)",
            "SBIRS payload (infrared sensor)",
            "SM-3 Block IIA / IIB (ballistic missile defense)",
            "SPY-6 radar (space-adjacent BMD)",
            "GPS III navigation payload",
            "Visible Infrared Imaging Radiometer Suite (VIIRS)",
            "StormBreaker (space-guided munition)",
            "Advanced EO/IR sensor suites",
        ],
        "space_capabilities": [
            "Space-based infrared sensors",
            "Missile warning/tracking payloads",
            "Precision navigation payloads",
            "Cryogenic IR focal plane arrays",
            "Directed energy research",
            "Electronic warfare / EW payloads",
        ],
        "fvey_relevance": "critical",
        "notes": (
            "Formed from 2020 merger of Raytheon and United Technologies. Dominant "
            "provider of missile warning infrared sensor payloads — SBIRS, OPIR. "
            "SM-3 interceptor program is the primary US exo-atmospheric BMD capability. "
            "Significant EW and electronic protection portfolio relevant to SATCOM "
            "anti-jam and GPS anti-spoofing."
        ),
    },
    {
        "name": "L3Harris Technologies",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Melbourne, FL",
        "space_revenue_usd": "6.1B",
        "total_revenue_usd": "21.1B",
        "employees": 50000,
        "key_programs": [
            "Responsive small satellites (SDA Tranche)",
            "Navigation Technology Satellite (NTS-3)",
            "Tracking Layer (SDA proliferated LEO)",
            "WESCAM / sensor turrets (ISR integration)",
            "Ground-based OPIR processing",
            "Environmental satellite instruments (NOAA)",
            "Tactical datalinks (Link 16, MADL)",
            "Harris GEOINT systems",
        ],
        "space_capabilities": [
            "Small/medium satellite manufacturing",
            "Space-based EO/IR imaging",
            "Protected tactical communications",
            "Ground processing and mission systems",
            "Responsive space architectures",
            "Signals intelligence payloads",
        ],
        "fvey_relevance": "critical",
        "notes": (
            "Formed from 2019 L3-Harris merger. Largest US provider of responsive "
            "small satellite buses for SDA Proliferated Warfighter Space Architecture. "
            "NTS-3 navigation technology satellite demonstrates next-gen GPS anti-jam "
            "and regional augmentation. Key provider of ground processing for OPIR "
            "and GEOINT mission data."
        ),
    },
    {
        "name": "SpaceX",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Hawthorne, CA",
        "space_revenue_usd": "13.0B",
        "total_revenue_usd": "13.0B",
        "employees": 13000,
        "key_programs": [
            "Falcon 9 / Falcon Heavy (NSSL launch)",
            "Starship / Super Heavy (next-gen heavy lift)",
            "Starlink (broadband mega-constellation)",
            "Starshield (classified government constellation)",
            "Dragon crew/cargo (ISS transport)",
            "Bandwagon rideshare program",
            "Direct-to-cell Starlink service",
            "Starlink V2 Mini / V3 satellite production",
        ],
        "space_capabilities": [
            "Reusable orbital-class launch vehicles",
            "Mega-constellation manufacturing at scale",
            "On-orbit propulsive deorbit",
            "Crewed spacecraft operations",
            "Super-heavy lift (Starship: 100-150 t to LEO)",
            "High-cadence launch operations (90+ per year)",
        ],
        "fvey_relevance": "critical",
        "notes": (
            "Dominant global launch provider with 60%+ of all orbital launches (2024). "
            "Starlink constellation exceeds 6,000 active satellites — largest constellation "
            "in history. Starshield is the classified DoD/IC variant with enhanced "
            "encryption and inter-satellite laser links. NSSL Phase 2 Lane 1 awardee. "
            "Starship promises 10x cost reduction in $/kg to orbit if fully reusable."
        ),
    },
    {
        "name": "United Launch Alliance (ULA)",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Centennial, CO",
        "space_revenue_usd": "3.2B",
        "total_revenue_usd": "3.2B",
        "employees": 3500,
        "key_programs": [
            "Vulcan Centaur (next-gen launch vehicle)",
            "Atlas V (legacy — retiring)",
            "Delta IV Heavy (retired 2024)",
            "NSSL Phase 2 Lane 1 missions",
            "USSF national security launches",
            "NASA CLPS lunar delivery",
            "Commercial GEO launches",
            "Certification missions for Vulcan",
        ],
        "space_capabilities": [
            "Assured access to space (national security missions)",
            "High-energy upper stages (Centaur V)",
            "Dual-launch-pad operations (SLC-41, SLC-3E)",
            "Vertical integration for classified payloads",
            "GTO/GEO direct injection",
            "Deep space / escape trajectory insertion",
        ],
        "fvey_relevance": "high",
        "notes": (
            "Boeing-Lockheed JV providing assured access to space since 2006. Vulcan "
            "Centaur first flew January 2024, replacing Atlas V and Delta IV Heavy. "
            "BE-4 engines sourced from Blue Origin. NSSL Phase 2 Lane 1 awardee. "
            "100% national security launch success record across 150+ missions."
        ),
    },
    {
        "name": "Rocket Lab USA",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Long Beach, CA",
        "space_revenue_usd": "0.4B",
        "total_revenue_usd": "0.4B",
        "employees": 2000,
        "key_programs": [
            "Electron (small launch vehicle)",
            "Neutron (medium-lift, in development)",
            "Photon satellite bus",
            "SDA Tranche satellite buses",
            "HASTE suborbital hypersonic testbed",
            "Globalstar constellation replenishment",
            "CAPSTONE lunar pathfinder",
            "Rutherford engine (3D-printed, electric pump-fed)",
        ],
        "space_capabilities": [
            "Responsive small launch (30-day call-up)",
            "Kick stage precision orbit insertion",
            "Solar cell manufacturing (SolAero acquisition)",
            "Reaction wheel production",
            "Satellite bus integration",
            "Launch from US (Wallops) and New Zealand (Mahia)",
        ],
        "fvey_relevance": "high",
        "notes": (
            "Founded in New Zealand, now US-headquartered. Only Western small launch "
            "vehicle provider with consistent operational cadence. Acquired multiple "
            "space component companies (SolAero solar cells, Sinclair reaction wheels, "
            "PSC separation systems). FVEY-friendly with dual launch sites enabling "
            "diverse orbit access. Neutron medium-lift vehicle targets SDA constellation "
            "deployment market."
        ),
    },
    {
        "name": "Ball Aerospace (BAE Systems Inc.)",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Broomfield, CO",
        "space_revenue_usd": "3.8B",
        "total_revenue_usd": "3.8B",
        "employees": 5800,
        "key_programs": [
            "SDA Tracking Layer satellites",
            "JWST optical telescope assembly",
            "Kepler / TESS / Nancy Grace Roman (NASA science)",
            "Weather satellite instruments (JPSS, GOES-R)",
            "Missile defense tracking systems",
            "Compact EO/IR payloads",
            "Commercial remote sensing bus platforms",
            "Starling autonomous satellite swarm (NASA)",
        ],
        "space_capabilities": [
            "Precision optical systems and mirrors",
            "Cryogenic space telescope assemblies",
            "Infrared sensor focal plane arrays",
            "Compact satellite buses for DoD",
            "Environmental monitoring instruments",
            "Autonomous swarm satellite tech",
        ],
        "fvey_relevance": "high",
        "notes": (
            "Acquired by BAE Systems Inc. in 2024 for $5.5B. Premier provider of "
            "space optical systems — built primary mirrors for Hubble, JWST, Kepler, "
            "Spitzer. Major SDA Tracking Layer contractor. Compact, high-performance "
            "EO/IR payloads ideal for proliferated LEO missile tracking."
        ),
    },
    {
        "name": "Blue Origin",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Kent, WA",
        "space_revenue_usd": "1.5B",
        "total_revenue_usd": "1.5B",
        "employees": 11000,
        "key_programs": [
            "New Glenn (heavy-lift orbital launch vehicle)",
            "BE-4 engine (ULA Vulcan, New Glenn first stage)",
            "Blue Moon lunar lander (HLS Option B — Artemis V)",
            "Orbital Reef commercial space station",
            "New Shepard suborbital vehicle",
            "Project Jarvis (reusable upper stage — R&D)",
            "Advanced Development Programs (classified)",
            "BE-3U upper stage engine",
        ],
        "space_capabilities": [
            "LOX/LNG reusable launch vehicles",
            "High-performance liquid rocket engines",
            "Lunar lander systems",
            "Commercial LEO habitation",
            "Suborbital research platform",
            "Vertical landing technology",
        ],
        "fvey_relevance": "medium",
        "notes": (
            "Jeff Bezos-funded space company. BE-4 engine is critical path for both "
            "New Glenn and ULA Vulcan. Selected for Artemis V lunar lander (HLS Option B). "
            "New Glenn first launch expected 2025. Orbital Reef space station partnership "
            "with Sierra Space. Potential NSSL Phase 3 competitor."
        ),
    },
    {
        "name": "General Atomics Electromagnetic Systems",
        "country": "US",
        "category": "us_prime",
        "headquarters": "San Diego, CA",
        "space_revenue_usd": "1.0B",
        "total_revenue_usd": "4.0B",
        "employees": 15000,
        "key_programs": [
            "Electromagnetic Aircraft Launch System (EMALS — space-adjacent)",
            "GA-EMS satellite buses (small/medium class)",
            "Orbital Test Bed (OTB) on-orbit demonstration",
            "Nuclear thermal propulsion (DRACO — DARPA/NASA)",
            "LiDAR and EO/IR payloads",
            "Electromagnetic railgun (space-adjacent directed energy)",
            "Advanced fission reactors for space power",
            "MQ-9B SkyGuardian (SATCOM-dependent ISR — space adjacent)",
        ],
        "space_capabilities": [
            "Small/medium satellite bus manufacturing",
            "Nuclear thermal propulsion development",
            "Electromagnetic launch technology",
            "Space-rated power systems",
            "On-orbit technology demonstration",
            "Directed energy systems R&D",
        ],
        "fvey_relevance": "medium",
        "notes": (
            "Expanding into space with satellite bus production and nuclear propulsion. "
            "DARPA DRACO (Demonstration Rocket for Agile Cislunar Operations) program "
            "with BWX Technologies develops nuclear thermal propulsion for rapid cislunar "
            "maneuver — launching 2027. Brings strong nuclear and electromagnetic systems "
            "heritage to the space domain."
        ),
    },
    {
        "name": "Sierra Space",
        "country": "US",
        "category": "us_prime",
        "headquarters": "Broomfield, CO",
        "space_revenue_usd": "0.5B",
        "total_revenue_usd": "0.5B",
        "employees": 1500,
        "key_programs": [
            "Dream Chaser spaceplane (ISS cargo — CRS-2)",
            "LIFE expandable habitat module",
            "Orbital Reef commercial space station (with Blue Origin)",
            "Shooting Star cargo module",
            "In-space manufacturing research",
            "ISS National Lab research management",
            "Inflatable structure technology",
            "Military spaceplane applications (conceptual)",
        ],
        "space_capabilities": [
            "Reusable lifting-body spaceplane",
            "Expandable space habitation modules",
            "Autonomous runway landing from orbit",
            "In-space manufacturing platforms",
            "Cargo return from orbit",
            "Commercial space station operations",
        ],
        "fvey_relevance": "medium",
        "notes": (
            "Spun out from Sierra Nevada Corporation in 2021. Dream Chaser is the "
            "only US winged orbital vehicle besides X-37B — runway landing capability "
            "enables flexible return of cargo and potentially sensitive payloads. "
            "LIFE habitat technology could support military space station concepts. "
            "Orbital Reef with Blue Origin selected for NASA CLD program."
        ),
    },
]

_ALLIED_CONTRACTORS: List[dict] = [
    {
        "name": "Airbus Defence and Space",
        "country": "EU (France/Germany/Spain)",
        "category": "allied",
        "headquarters": "Toulouse, France / Friedrichshafen, Germany",
        "space_revenue_usd": "8.5B",
        "total_revenue_usd": "8.5B",
        "employees": 35000,
        "key_programs": [
            "OneWeb constellation (Eutelsat OneWeb)",
            "Copernicus Sentinel satellites (ESA)",
            "Eurostar satellite bus (GEO comms)",
            "Pléiades Neo (very high-resolution EO)",
            "Syracuse IV (French military SATCOM)",
            "Skynet 6A (UK military SATCOM)",
            "FCAS remote carrier (space-adjacent)",
            "Ariane 6 upper stage (ESA)",
        ],
        "space_capabilities": [
            "GEO/LEO satellite manufacturing",
            "Earth observation constellation operation",
            "Military SATCOM buses",
            "Launch vehicle upper stages",
            "Space-based intelligence systems",
            "Optical inter-satellite links",
        ],
        "fvey_relevance": "high",
        "notes": (
            "Europe's largest space company. Prime contractor for Skynet 6A (UK MOD) — "
            "direct FVEY relevance. Operates Pléiades Neo 0.3m-class optical constellation "
            "available to allied defence customers. OneWeb merger with Eutelsat creates "
            "EU-based LEO broadband alternative to Starlink."
        ),
    },
    {
        "name": "Thales Alenia Space",
        "country": "EU (France/Italy)",
        "category": "allied",
        "headquarters": "Cannes, France / Turin, Italy",
        "space_revenue_usd": "3.2B",
        "total_revenue_usd": "3.2B",
        "employees": 8900,
        "key_programs": [
            "IRIS² (EU sovereign constellation)",
            "Copernicus Sentinel-1/3 (SAR and ocean monitoring)",
            "CSO (Composante Spatiale Optique — French military EO)",
            "Galileo 2nd generation navigation satellites",
            "Spacebus satellite buses",
            "COSMO-SkyMed 2nd gen (Italian military SAR)",
            "ExoMars Trace Gas Orbiter",
            "Hera asteroid mission",
        ],
        "space_capabilities": [
            "SAR satellite design and manufacturing",
            "Navigation satellite production",
            "Military optical reconnaissance systems",
            "Deep space missions",
            "Pressurized space modules (ISS/Lunar Gateway)",
            "Secure space communications",
        ],
        "fvey_relevance": "medium",
        "notes": (
            "Joint venture of Thales (67%) and Leonardo (33%). Prime for multiple "
            "European military space programs. IRIS² EU sovereign connectivity "
            "constellation is a strategic EU hedge against US/UK Starlink dependency. "
            "Galileo 2nd gen provides independent PNT for NATO allies."
        ),
    },
    {
        "name": "BAE Systems (UK)",
        "country": "UK",
        "category": "allied",
        "headquarters": "London, UK",
        "space_revenue_usd": "2.1B",
        "total_revenue_usd": "28.3B",
        "employees": 100500,
        "key_programs": [
            "Skynet military SATCOM (legacy operator)",
            "PHASA-35 (solar-electric HAPS)",
            "Ball Aerospace subsidiary (acquired 2024)",
            "Electronic warfare / SIGINT systems",
            "Tempest / GCAP (space-adjacent 6th gen fighter)",
            "Cyber and intelligence solutions",
            "Maritime autonomous systems",
            "Typhoon / F-35 integration (GPS/SATCOM-dependent)",
        ],
        "space_capabilities": [
            "Military SATCOM operations (Skynet heritage)",
            "High-altitude pseudo-satellites",
            "Electronic warfare payloads",
            "Space-qualified EO/IR (via Ball Aerospace)",
            "Signals intelligence systems",
            "Cyber-resilient space ground segments",
        ],
        "fvey_relevance": "critical",
        "notes": (
            "UK's largest defence company. Historically operated Skynet military "
            "SATCOM under PFI contract. Ball Aerospace acquisition (2024) gives "
            "significant US space capability. PHASA-35 HAPS provides persistent "
            "stratospheric ISR — potential space system complement."
        ),
    },
    {
        "name": "QinetiQ",
        "country": "UK",
        "category": "allied",
        "headquarters": "Farnborough, UK",
        "space_revenue_usd": "0.3B",
        "total_revenue_usd": "2.2B",
        "employees": 8000,
        "key_programs": [
            "UK Space Agency research contracts",
            "Space debris monitoring research",
            "Satellite vulnerability assessments",
            "Counter-space threat analysis",
            "Space weather monitoring instrumentation",
            "SSA sensor development",
            "DSTL space technology research",
            "Zephyr HAPS program support",
        ],
        "space_capabilities": [
            "Space domain awareness R&D",
            "Satellite test and evaluation",
            "Space environment effects analysis",
            "Orbital mechanics modeling",
            "Counter-space capability assessment",
            "Space system vulnerability testing",
        ],
        "fvey_relevance": "high",
        "notes": (
            "Spun out from UK DERA (Defence Evaluation and Research Agency). "
            "Provides critical T&E and analytical support to UK MOD space programs. "
            "Deep expertise in space domain awareness and counter-space threat "
            "analysis. Key DSTL research partner."
        ),
    },
    {
        "name": "MDA Space (formerly MDA Ltd / MacDonald Dettwiler)",
        "country": "Canada",
        "category": "allied",
        "headquarters": "Brampton, Ontario, Canada",
        "space_revenue_usd": "0.6B",
        "total_revenue_usd": "0.6B",
        "employees": 3000,
        "key_programs": [
            "RADARSAT Constellation Mission (RCM)",
            "Canadarm3 (Lunar Gateway robotic arm)",
            "Satellite servicing robotics",
            "SAR satellite bus design",
            "Ground segment operations",
            "Defence ISR solutions",
            "Telesat Lightspeed constellation support",
            "Maritime surveillance (Dark vessel detection)",
        ],
        "space_capabilities": [
            "SAR satellite constellation operations",
            "Space robotics (Canadarm heritage)",
            "On-orbit servicing manipulators",
            "Maritime domain awareness (SAR-AIS fusion)",
            "Ground station operations",
            "SAR data analytics",
        ],
        "fvey_relevance": "critical",
        "notes": (
            "Canada's premier space company. RADARSAT Constellation provides FVEY "
            "with C-band SAR coverage for Arctic surveillance, maritime domain "
            "awareness, and disaster monitoring. Canadarm3 for Lunar Gateway ensures "
            "Canadian access to US cislunar infrastructure. Key Five Eyes partner "
            "for Arctic and maritime ISR."
        ),
    },
    {
        "name": "Electro Optic Systems (EOS)",
        "country": "Australia",
        "category": "allied",
        "headquarters": "Canberra, ACT, Australia",
        "space_revenue_usd": "0.15B",
        "total_revenue_usd": "0.35B",
        "employees": 900,
        "key_programs": [
            "Space debris tracking telescopes",
            "Satellite laser ranging",
            "Counter-drone directed energy systems",
            "SSA sensor systems for ADF",
            "Space debris remediation research",
            "Fire control systems (Mk II)",
            "Defence SSA ground stations",
            "SpaceLink optical tracking network",
        ],
        "space_capabilities": [
            "Precision optical tracking (sub-arcsecond)",
            "Satellite laser ranging (SLR)",
            "Directed energy weapon systems",
            "Space situational awareness sensors",
            "Debris tracking and characterization",
            "Ground-based space surveillance",
        ],
        "fvey_relevance": "high",
        "notes": (
            "Niche Australian capability in precision optical tracking and directed "
            "energy. Space debris tracking telescopes deployed at Mt Stromlo and "
            "other sites. Potential contributor to FVEY SSA sharing network. Directed "
            "energy systems have dual-use potential for space debris remediation "
            "and counter-satellite applications."
        ),
    },
    {
        "name": "Gilmour Space Technologies",
        "country": "Australia",
        "category": "allied",
        "headquarters": "Gold Coast, Queensland, Australia",
        "space_revenue_usd": "0.02B",
        "total_revenue_usd": "0.05B",
        "employees": 200,
        "key_programs": [
            "Eris (3-stage orbital launch vehicle)",
            "Eris Block II (enhanced payload capacity)",
            "ADF sovereign launch capability studies",
            "Hybrid rocket motor development",
            "Defence rapid-launch demonstration",
            "Responsive space access for Australia",
            "Small satellite deployment services",
            "Bowen spaceport development",
        ],
        "space_capabilities": [
            "Hybrid rocket propulsion",
            "Sovereign Australian orbital launch",
            "Responsive small satellite deployment",
            "Launch vehicle design and manufacturing",
            "Ground launch infrastructure",
            "Payload integration services",
        ],
        "fvey_relevance": "medium",
        "notes": (
            "Leading Australian launch startup aiming for sovereign orbital access. "
            "Eris vehicle targets 300 kg to LEO from Bowen, Queensland. Australian "
            "sovereign launch is a priority under JP 9102 and DSR 2024 for resilient "
            "FVEY space access. First orbital attempt planned for 2025-2026."
        ),
    },
    {
        "name": "Fleet Space Technologies",
        "country": "Australia",
        "category": "allied",
        "headquarters": "Adelaide, South Australia",
        "space_revenue_usd": "0.05B",
        "total_revenue_usd": "0.08B",
        "employees": 300,
        "key_programs": [
            "Alpha constellation (LEO IoT/sensing)",
            "ExoSphere (mineral exploration via satellite)",
            "3D-printed satellite manufacturing",
            "ADF tactical SATCOM pathfinder",
            "Centauri nanosatellites (operational)",
            "Mineral exploration AI analytics",
            "Low-latency edge computing in space",
            "Australian Space Agency grants",
        ],
        "space_capabilities": [
            "Nanosatellite/smallsat manufacturing",
            "3D-printed satellite structures (first in world)",
            "LEO IoT connectivity",
            "Geophysical sensing from orbit",
            "Low-power wide-area networking",
            "Edge computing satellite payloads",
        ],
        "fvey_relevance": "medium",
        "notes": (
            "Innovative Adelaide-based smallsat manufacturer using 3D printing for "
            "rapid satellite production. ExoSphere product uses satellite-connected "
            "ground sensors for mineral exploration — potential dual-use for "
            "defence geospatial sensing. Growing ADF engagement for tactical comms."
        ),
    },
    {
        "name": "Saab AB — Space Division",
        "country": "Sweden",
        "category": "allied",
        "headquarters": "Gothenburg, Sweden",
        "space_revenue_usd": "0.3B",
        "total_revenue_usd": "5.8B",
        "employees": 22000,
        "key_programs": [
            "Gripen E avionics (SATCOM/GPS-dependent — space-adjacent)",
            "SSC ground station services (Saab subsidiary via SSC partnership)",
            "Satellite operations and ground segment",
            "Carl-Gustaf / RBS 70 (space-guided precision — adjacent)",
            "GlobalEye AEW&C (SATCOM-dependent ISR — space-adjacent)",
            "SKELETON counter-UAS radar",
            "ARTHUR weapon-locating radar",
            "Swedish Armed Forces space domain support",
        ],
        "space_capabilities": [
            "Ground station operations",
            "Space-qualified electronics and avionics",
            "Satellite data downlink and processing",
            "Radar systems adaptable to SSA",
            "Electronic warfare systems",
            "Arctic region ground infrastructure",
        ],
        "fvey_relevance": "medium",
        "notes": (
            "Sweden's premier defence company with growing space relevance. Swedish "
            "Space Corporation (SSC) operates Esrange Space Center in Kiruna — one of "
            "Europe's premier ground station locations for polar orbit satellite contact. "
            "Saab's radar and EW expertise applicable to space domain awareness. "
            "Sweden joined NATO in 2024, increasing FVEY interoperability."
        ),
    },
]

_ADVERSARY_INDUSTRY: List[dict] = [
    {
        "name": "China Aerospace Science and Technology Corporation (CASC)",
        "country": "PRC",
        "category": "adversary_state_enterprise",
        "headquarters": "Beijing, PRC",
        "space_revenue_usd": "35B (estimated)",
        "employees": 230000,
        "key_programs": [
            "Long March (CZ) launch vehicle family",
            "BeiDou-3 navigation constellation (30 MEO + GEO + IGSO)",
            "Tiangong/CSS (Chinese Space Station)",
            "Shenzhou crewed spacecraft",
            "Tianwen Mars / Lunar Chang'e missions",
            "Yaogan (remote sensing / ELINT constellation — 300+ sats)",
            "SJ (Shijian) technology demonstration / inspector satellites",
            "Gaofen high-resolution EO constellation",
        ],
        "space_capabilities": [
            "Full-spectrum launch (LEO to deep space)",
            "Crewed spaceflight and space station",
            "Military reconnaissance constellations (EO, SAR, ELINT)",
            "Navigation system operation (global)",
            "Deep space exploration",
            "On-orbit proximity operations / inspection",
        ],
        "threat_level": "critical",
        "notes": (
            "Primary PRC state space enterprise. Vertically integrated from launch "
            "vehicles through satellite manufacturing to ground segment. CASC is the "
            "backbone of PRC military space — Yaogan constellation provides persistent "
            "ISR for PLA targeting kill chain. BeiDou provides independent PNT."
        ),
    },
    {
        "name": "China Aerospace Science and Industry Corporation (CASIC)",
        "country": "PRC",
        "category": "adversary_state_enterprise",
        "headquarters": "Beijing, PRC",
        "space_revenue_usd": "15B (estimated)",
        "employees": 180000,
        "key_programs": [
            "Kuaizhou (KZ) solid-fuel rapid-launch vehicles",
            "DF-21D / DF-26 / DF-ZF (ballistic missiles — space adjacent)",
            "HQ-19 (exo-atmospheric BMD interceptor / DA-ASAT capable)",
            "Hongyun LEO broadband constellation",
            "Xingyun narrow-band IoT constellation",
            "Hypersonic glide vehicles",
            "SC-19 / DN-3 direct-ascent ASAT",
            "Tengyun spaceplane (reusable, in development)",
        ],
        "space_capabilities": [
            "Rapid-response solid-fuel launch (24-hr call-up)",
            "Direct-ascent ASAT weapons",
            "Hypersonic boost-glide vehicles",
            "Ballistic missile defense interceptors",
            "Small satellite constellations",
            "Reusable spaceplane R&D",
        ],
        "threat_level": "critical",
        "notes": (
            "PRC's missile and counter-space prime contractor. CASIC builds the "
            "direct-ascent ASAT weapons tested in 2007 (SC-19) and subsequent "
            "systems. Kuaizhou rapid-launch capability gives PRC the ability to "
            "reconstitute LEO assets within hours. DF-21D/DF-26 anti-ship ballistic "
            "missiles rely on PRC space-based ISR targeting chain."
        ),
    },
    {
        "name": "Roscosmos State Corporation",
        "country": "Russia",
        "category": "adversary_state_enterprise",
        "headquarters": "Moscow, Russia",
        "space_revenue_usd": "3.5B",
        "employees": 170000,
        "key_programs": [
            "Soyuz-2 launch vehicle family",
            "Angara-A5 heavy-lift vehicle",
            "GLONASS navigation constellation",
            "Liana SIGINT/ELINT constellation (Lotos-S, Pion-NKS)",
            "ISS Segment operations (Zvezda, Nauka)",
            "Orel (Oryol) next-gen crew vehicle",
            "Luna-25/26/27/28 lunar program",
            "Sphere broadband constellation (planned)",
        ],
        "space_capabilities": [
            "Human spaceflight operations",
            "Launch vehicle production and operations",
            "Navigation satellite constellation (GLONASS)",
            "SIGINT/ELINT satellite systems",
            "Space station module manufacturing",
            "Lunar exploration missions",
        ],
        "threat_level": "high",
        "notes": (
            "Russian state space corporation reorganized in 2015. Severely impacted by "
            "Western sanctions post-2022 — loss of Western EEE parts, customer launches, "
            "and ESA cooperation. GLONASS degradation reported. Liana SIGINT constellation "
            "(Lotos-S1 14F145, Pion-NKS 14F139) provides ELINT targeting for Russian Navy. "
            "Conducted Nudol DA-ASAT test November 2021."
        ),
    },
    {
        "name": "RSC Energia",
        "country": "Russia",
        "category": "adversary_state_enterprise",
        "headquarters": "Korolev, Moscow Oblast, Russia",
        "space_revenue_usd": "1.2B",
        "employees": 22000,
        "key_programs": [
            "Soyuz MS crewed spacecraft",
            "Progress MS cargo spacecraft",
            "ISS Russian segment operations",
            "Orel next-gen crew vehicle (delayed)",
            "Russian Orbital Service Station (ROSS) planning",
            "Science Power Module (NEM)",
            "EVA suit / spacesuit development",
            "PTK spacecraft systems",
        ],
        "space_capabilities": [
            "Crewed spacecraft design and operations",
            "Cargo resupply vehicles",
            "Space station module development",
            "On-orbit assembly techniques",
            "Life support systems",
            "Orbital rendezvous and docking",
        ],
        "threat_level": "medium",
        "notes": (
            "Korolev's legacy organization — designed Soyuz, Salyut, Mir, ISS Russian "
            "segment. Post-sanctions, Energia faces severe technology constraints. "
            "ROSS space station intended to replace ISS Russian segment but faces "
            "significant funding and schedule challenges. Orel crew vehicle repeatedly "
            "delayed. Co-orbital inspection heritage from Soviet-era programs."
        ),
    },
    {
        "name": "ISS Reshetnev (Academician Reshetnev Information Satellite Systems)",
        "country": "Russia",
        "category": "adversary_state_enterprise",
        "headquarters": "Zheleznogorsk, Krasnoyarsk Krai, Russia",
        "space_revenue_usd": "0.8B",
        "employees": 9000,
        "key_programs": [
            "GLONASS-K / GLONASS-K2 navigation satellites",
            "Gonets-M LEO messaging constellation",
            "Blagovest military GEO SATCOM",
            "Meridian / Molniya-orbit military SATCOM",
            "Luch relay satellites (GEO — data relay / SIGINT)",
            "Express AM GEO communications satellites",
            "Sphere constellation (next-gen broadband, in development)",
            "Skif / Marafon LEO broadband demonstrators",
        ],
        "space_capabilities": [
            "Navigation satellite manufacturing (GLONASS)",
            "GEO military SATCOM buses",
            "HEO military communications",
            "Data relay satellite systems",
            "LEO constellation development",
            "Secure government communications",
        ],
        "threat_level": "medium",
        "notes": (
            "Russia's primary satellite manufacturer, located in the closed city of "
            "Zheleznogorsk (Krasnoyarsk-26). Builds GLONASS navigation satellites and "
            "most Russian military SATCOM. Luch relay satellites have been observed "
            "conducting proximity operations near Western GEO satellites — potential "
            "co-orbital SIGINT collection or inspection missions."
        ),
    },
    {
        "name": "Iran Space Agency (ISA) / IRGC Aerospace Force",
        "country": "Iran",
        "category": "adversary_state_enterprise",
        "headquarters": "Tehran, Iran",
        "space_revenue_usd": "0.05B (estimated)",
        "employees": 5000,
        "key_programs": [
            "Simorgh SLV (space launch vehicle — ICBM-derivative)",
            "Qased SLV (IRGC mobile solid-fuel launch)",
            "Noor military reconnaissance satellites",
            "Nahid communications satellite program",
            "Zafar remote sensing satellite",
            "Sorayya satellite (2024 — 750 km orbit)",
            "Chamran-1 imaging satellite",
            "Khayyam satellite (Russian-launched, Iranian-operated)",
        ],
        "space_capabilities": [
            "Indigenous SLV development (liquid and solid)",
            "LEO reconnaissance satellite operation",
            "Dual-use SLV/ICBM technology",
            "Mobile solid-fuel launch capability",
            "Space-based imaging for military ISR",
            "Space program as sanctions-evasion technology pathway",
        ],
        "threat_level": "medium",
        "notes": (
            "Dual-track space program — civilian ISA and IRGC Aerospace Force. "
            "Qased SLV is a mobile solid-fuel vehicle providing rapid-response launch "
            "and ICBM technology development pathway. Noor satellites provide basic "
            "military ISR capability. Space program is a proliferation concern — "
            "SLV/ICBM technology overlap monitored by MTCR partners."
        ),
    },
    {
        "name": "National Aerospace Development Administration (NADA)",
        "country": "DPRK",
        "category": "adversary_state_enterprise",
        "headquarters": "Pyongyang, DPRK",
        "space_revenue_usd": "unknown",
        "employees": "unknown",
        "key_programs": [
            "Chollima-1 SLV (3-stage orbital launcher)",
            "Malligyong-1 reconnaissance satellite",
            "Unha-3 SLV (Taepodong-derivative)",
            "Sohae satellite launch facility",
            "Tonghae satellite launch facility",
            "ICBM technology development (Hwasong series)",
            "Reconnaissance General Bureau space ISR",
            "Second reconnaissance satellite attempts",
        ],
        "space_capabilities": [
            "Indigenous SLV / ICBM development",
            "Basic LEO reconnaissance satellite",
            "Nuclear-capable ICBM (space-adjacent)",
            "Launch facility operations",
            "Satellite ground control (limited)",
            "Dual-use missile/space technology",
        ],
        "threat_level": "high",
        "notes": (
            "DPRK placed Malligyong-1 reconnaissance satellite in orbit November 2023 "
            "using Chollima-1 SLV after two failed attempts. Satellite reportedly non-"
            "functional or very limited capability. Primary concern is SLV/ICBM technology "
            "overlap — Hwasong-17/18 ICBMs can reach continental US. All launches violate "
            "UNSC resolutions 1718, 1874, 2087, 2094."
        ),
    },
]

# ===========================================================================
#  2. MAJOR CONTRACTS DATABASE (15+ entries)
# ===========================================================================

_MAJOR_CONTRACTS: List[dict] = [
    {
        "program": "GPS III Follow-On (GPS IIIF)",
        "contractor": "Lockheed Martin",
        "awarding_agency": "US Space Force — Space Systems Command",
        "value_usd": "7.2B",
        "contract_type": "Fixed-Price Incentive Firm (FPIF)",
        "period": "2018–2030",
        "status": "active — production",
        "description": (
            "22 GPS IIIF satellites (SV13-SV32) with enhanced capabilities including "
            "Military Code (M-Code) for anti-jam/anti-spoof PNT, Regional Military "
            "Protection (RMP), search and rescue (SAR), and a fully digital navigation "
            "payload. Builds on 10 GPS III SV01-SV10 baseline satellites."
        ),
        "fvey_impact": (
            "GPS IIIF provides next-generation M-Code anti-jam PNT to all FVEY forces. "
            "Regional Military Protection enables theater-level GPS signal protection. "
            "Critical enabler for precision-guided munitions across all FVEY militaries."
        ),
        "source": "Lockheed Martin 10-K; USSF budget justification FY2025; GAO-24-106050",
    },
    {
        "program": "Next-Generation Overhead Persistent Infrared (Next-Gen OPIR)",
        "contractor": "Lockheed Martin (GEO); Northrop Grumman (Polar)",
        "awarding_agency": "US Space Force — Space Systems Command",
        "value_usd": "4.9B (GEO) + 2.4B (Polar)",
        "contract_type": "Cost-Plus Incentive Fee (CPIF)",
        "period": "2018–2029",
        "status": "active — development / integration",
        "description": (
            "Replacement for legacy SBIRS missile warning constellation. Three GEO "
            "satellites (Lockheed Martin) and two polar-orbit satellites (Northrop "
            "Grumman) with wide-field-of-view and enhanced staring IR sensors for "
            "missile launch detection, tracking, and characterization."
        ),
        "fvey_impact": (
            "Provides initial missile warning for all FVEY nations via integrated "
            "ground processing. Enhanced dim-target tracking capability addresses "
            "hypersonic glide vehicle detection gap. Shared via SBIRS MCS ground "
            "segment and Allied Data Sharing agreements."
        ),
        "source": "USSF FY2025 budget; GAO-24-106800; Congressional Research Service IF11046",
    },
    {
        "program": "Space Development Agency (SDA) Proliferated Warfighter Space Architecture — Tranche 0/1/2",
        "contractor": "L3Harris, Northrop Grumman, Lockheed Martin, York Space Systems, SpaceX (launch)",
        "awarding_agency": "Space Development Agency (now under USSF SSC)",
        "value_usd": "13.5B+ (cumulative Tranche 0-2)",
        "contract_type": "Firm-Fixed-Price (FFP) — spiral development",
        "period": "2020–2028",
        "status": "active — Tranche 0 on-orbit; Tranche 1 launching; Tranche 2 contracted",
        "description": (
            "Proliferated LEO constellation of hundreds of satellites in Transport "
            "(optical mesh inter-satellite links), Tracking (missile warning/tracking "
            "from LEO), Custody (target custody handoff), and Battle Management layers. "
            "Tranche 0: 28 sats (2024). Tranche 1: ~150 sats (2025-2026). "
            "Tranche 2: ~250 sats (2027-2028). Total PWSA target: 500+ sats."
        ),
        "fvey_impact": (
            "PWSA provides hypersonic and ballistic missile tracking from LEO, "
            "persistent global transport mesh for fire control data, and resilient "
            "architecture through proliferation. Designed to be interoperable with "
            "allied BMD systems. Game-changing for FVEY integrated air and missile defense."
        ),
        "source": "SDA budget justification; GAO-24-106050; CRS IF12033",
    },
    {
        "program": "National Security Space Launch (NSSL) Phase 2 — Lane 1",
        "contractor": "SpaceX (Falcon 9/Heavy), ULA (Vulcan Centaur)",
        "awarding_agency": "US Space Force — Space Systems Command",
        "value_usd": "15B+ (total Phase 2 ceiling, 2022-2027)",
        "contract_type": "IDIQ with task orders",
        "period": "2022–2027 (Phase 2); Phase 3 planning underway",
        "status": "active — ongoing launches",
        "description": (
            "Assured access to space for US national security payloads across all "
            "orbit regimes (LEO, MEO, GEO, HEO, escape). Phase 2 split 60/40 between "
            "ULA and SpaceX. ~50 missions over 5-year ordering period. Phase 3 "
            "competition expected to include Blue Origin New Glenn and possibly "
            "Rocket Lab Neutron."
        ),
        "fvey_impact": (
            "Guarantees access to space for US military and intelligence community "
            "satellite deployments. Dual-provider strategy ensures resilience against "
            "single-provider failure. FVEY partners benefit from US launch capacity "
            "for hosted payloads and cooperative programs."
        ),
        "source": "USSF SSC contract announcements; GAO-24-106050; CRS IF11994",
    },
    {
        "program": "Starshield",
        "contractor": "SpaceX",
        "awarding_agency": "US DoD / NRO / USSF (multiple classified contracts)",
        "value_usd": "1.8B+ (reported, likely higher)",
        "contract_type": "Various (classified)",
        "period": "2023–ongoing",
        "status": "active — deployment underway",
        "description": (
            "Government/military variant of Starlink constellation with enhanced "
            "security, encryption, and inter-satellite laser links optimized for "
            "national security missions. Supports ISR data transport, missile "
            "tracking sensor hosting, and secure communications. NRO awarded "
            "classified contract for proliferated LEO ISR capabilities."
        ),
        "fvey_impact": (
            "Potential to provide resilient, low-latency military broadband to "
            "FVEY forces globally. Proliferated architecture provides inherent "
            "resilience against ASAT attack. Integration with SDA PWSA transport "
            "layer could create unprecedented military space mesh network."
        ),
        "source": "Reuters/WSJ reporting 2024; NRO press release; SpaceX Starshield website",
    },
    {
        "program": "Skynet 6A",
        "contractor": "Airbus Defence and Space",
        "awarding_agency": "UK Ministry of Defence",
        "value_usd": "~£6B ($7.6B) lifecycle",
        "contract_type": "Service Delivery contract",
        "period": "2020–2040+",
        "status": "active — development",
        "description": (
            "Next-generation UK military SATCOM replacing Skynet 5 constellation. "
            "Skynet 6A is a GEO military communications satellite with UHF, SHF, "
            "and EHF capacity, anti-jam features, and cyber-resilient design. "
            "Broader Skynet 6 program includes ground segment modernization and "
            "potential additional satellites."
        ),
        "fvey_impact": (
            "Skynet is a core FVEY SATCOM asset — provides protected MILSATCOM "
            "to UK, US, NATO, and allied forces. Skynet 6A ensures continuation "
            "of sovereign UK SATCOM and allied interoperability through 2040+. "
            "EHF payload provides highest level of anti-jam protection."
        ),
        "source": "UK MOD announcement; Airbus Defence and Space press release; RUSI commentary",
    },
    {
        "program": "JP 9102 — Defence Space Architecture",
        "contractor": "Multiple (Lockheed Martin Australia, Northrop Grumman Australia shortlisted)",
        "awarding_agency": "Australian Department of Defence",
        "value_usd": "AUD 3-5B ($2-3.3B) estimated",
        "contract_type": "TBD — competitive evaluation",
        "period": "2024–2035+",
        "status": "active — competition / down-select",
        "description": (
            "Australia's sovereign military satellite communications program under "
            "the Integrated Investment Program. Intended to provide protected MILSATCOM "
            "for ADF operations in the Indo-Pacific. Options range from sovereign GEO "
            "constellation to hosted payloads on allied/commercial platforms. AUKUS "
            "interoperability is a key requirement."
        ),
        "fvey_impact": (
            "Fills a critical FVEY SATCOM gap in the Indo-Pacific. Australia currently "
            "relies on US WGS and commercial SATCOM. Sovereign Australian MILSATCOM "
            "directly enhances FVEY coverage over the Western Pacific, Indian Ocean, "
            "and Southern Ocean/Antarctica."
        ),
        "source": "Australian DSR 2024; IIP public documentation; ASPI reporting",
    },
    {
        "program": "Wideband Global SATCOM (WGS) 11+",
        "contractor": "Boeing",
        "awarding_agency": "US Space Force / International Partners",
        "value_usd": "$1.2B (WGS 11-12)",
        "contract_type": "Fixed-Price Incentive",
        "period": "2023–2028",
        "status": "active — production",
        "description": (
            "Continuation of the WGS GEO military broadband constellation. WGS 11+ "
            "satellites feature enhanced digital channelizers, increased throughput "
            "(10+ Gbps per satellite), and hosted payloads. WGS is a multinational "
            "partnership with Australia, Canada, Denmark, Luxembourg, Netherlands, "
            "and New Zealand contributing funding."
        ),
        "fvey_impact": (
            "WGS is the primary FVEY wideband MILSATCOM system. All Five Eyes nations "
            "have access. Australia and Canada are formal international partners "
            "contributing to WGS procurement. WGS 11+ modernization ensures wideband "
            "capacity through the 2030s for FVEY combined operations."
        ),
        "source": "Boeing press release; USSF budget justification; WGS International Partnership docs",
    },
    {
        "program": "Space Fence (AN/FSY-3)",
        "contractor": "Lockheed Martin",
        "awarding_agency": "US Space Force — Space Operations Command",
        "value_usd": "$1.5B (development + initial operations)",
        "contract_type": "Cost-Plus Award Fee",
        "period": "2014–ongoing (IOC 2020)",
        "status": "operational",
        "description": (
            "S-band ground-based radar on Kwajalein Atoll, Marshall Islands. "
            "Detects and tracks objects as small as 10 cm in LEO. Dramatically "
            "increases the number of tracked objects in the US Space Surveillance "
            "Network from ~25,000 to 200,000+. Second site option (Western Australia) "
            "under consideration."
        ),
        "fvey_impact": (
            "Space Fence is the most capable SSA sensor in the US Space Surveillance "
            "Network. Provides uncued detection of new objects, maneuver detection, "
            "and breakup event characterization. FVEY nations benefit via Combined "
            "Space Operations Center (CSpOC) data sharing. Potential second site "
            "in Australia would provide Southern Hemisphere coverage."
        ),
        "source": "Lockheed Martin press; USSF fact sheet; SPACECOM testimony",
    },
    {
        "program": "GPS Operational Control Segment (GPS OCX)",
        "contractor": "Boeing (Raytheon legacy)",
        "awarding_agency": "US Space Force — Space Systems Command",
        "value_usd": "$6.2B (revised — significant cost growth)",
        "contract_type": "Cost-Plus Incentive Fee",
        "period": "2010–2026 (delayed from 2016)",
        "status": "active — testing / delayed",
        "description": (
            "Next-generation ground control segment for GPS III/IIIF constellation. "
            "OCX Block 0 (launch and checkout) delivered. OCX Block 1 (mission "
            "operations) and Block 2 (M-Code tasking) repeatedly delayed. Required "
            "to unlock full GPS III/IIIF M-Code anti-jam capability. GAO has "
            "designated GPS OCX a high-risk program."
        ),
        "fvey_impact": (
            "OCX delays prevent full M-Code anti-jam PNT activation for all FVEY "
            "forces. Until OCX Block 2 is operational, GPS III satellites operate "
            "with legacy ground control limiting their enhanced capabilities. "
            "A critical bottleneck for FVEY precision navigation and timing."
        ),
        "source": "GAO-24-106050; GAO-23-106059; USSF FY2025 budget justification",
    },
    {
        "program": "Evolved Strategic SATCOM (ESS)",
        "contractor": "Northrop Grumman (prime)",
        "awarding_agency": "US Space Force — Space Systems Command",
        "value_usd": "$3.2B (estimated)",
        "contract_type": "Cost-Plus Incentive Fee",
        "period": "2020–2030+",
        "status": "active — early development",
        "description": (
            "Replacement for legacy AEHF (Advanced Extremely High Frequency) protected "
            "SATCOM constellation. ESS will provide nuclear-survivable, anti-jam, "
            "low-probability-of-intercept strategic communications for US nuclear "
            "command and control (NC3). EHF and SHF payloads with advanced "
            "nulling antenna technology."
        ),
        "fvey_impact": (
            "ESS is the NC3 space communications backbone. While primary mission is "
            "US nuclear C2, AEHF (and successor ESS) provides protected SATCOM to "
            "UK and Canada under bilateral agreements. Critical for FVEY strategic "
            "deterrence communications."
        ),
        "source": "USSF FY2025 budget; CRS IF12032; Northrop Grumman announcement",
    },
    {
        "program": "Resilient Missile Warning / Missile Tracking (RMW/RMT)",
        "contractor": "Multiple (SDA — L3Harris, Northrop Grumman; USSF — Lockheed Martin for OPIR)",
        "awarding_agency": "US Space Force / SDA",
        "value_usd": "$8B+ (combined GEO OPIR + SDA LEO tracking)",
        "contract_type": "Various",
        "period": "2020–2030",
        "status": "active — multi-layer deployment",
        "description": (
            "Integrated missile warning/tracking architecture combining GEO (Next-Gen "
            "OPIR) with proliferated LEO (SDA Tracking Layer) for cradle-to-grave "
            "tracking of ballistic, hypersonic, and cruise missiles. Multi-layer "
            "approach provides redundancy and improved tracking geometry."
        ),
        "fvey_impact": (
            "Addresses the hypersonic missile tracking gap that threatens FVEY "
            "integrated air and missile defense. LEO tracking layer provides "
            "fire-control-quality data for terminal defense interceptors. "
            "Interoperable with Australian IAMD under AUKUS."
        ),
        "source": "SDA documentation; USSF testimony; MDA budget justification",
    },
    {
        "program": "NATO SATCOM Post-2025",
        "contractor": "Airbus / Thales Alenia Space (competing teams)",
        "awarding_agency": "NATO Communications and Information Agency (NCIA)",
        "value_usd": "€2.5B ($2.7B) estimated",
        "contract_type": "Competition — requirements definition phase",
        "period": "2025–2040",
        "status": "planning — requirements definition",
        "description": (
            "NATO's next-generation satellite communications capability to replace "
            "aging NATO SATCOM terminals and augment national MILSATCOM (Skynet, WGS, "
            "Syracuse, SatcomBw). Options include sovereign NATO constellation, "
            "hosted payloads, and commercial SATCOM integration."
        ),
        "fvey_impact": (
            "NATO SATCOM directly supports FVEY interoperability in NATO operations. "
            "Ensures alliance-wide MILSATCOM coverage for Article 5 scenarios. "
            "Must interoperate with US WGS, UK Skynet, and French Syracuse systems."
        ),
        "source": "NCIA announcements; NATO Summit communiqués 2024; RUSI commentary",
    },
    {
        "program": "MUOS (Mobile User Objective System) Follow-On",
        "contractor": "Lockheed Martin",
        "awarding_agency": "US Navy / US Space Force",
        "value_usd": "$7.5B (MUOS baseline); follow-on TBD",
        "contract_type": "Various",
        "period": "2010–2030",
        "status": "operational — 5 GEO satellites on orbit; follow-on planning",
        "description": (
            "Narrowband tactical SATCOM constellation providing 3G-equivalent "
            "cellular service to mobile forces via WCDMA waveform. Five GEO "
            "satellites with UHF legacy and WCDMA payload. Follow-on analysis "
            "of alternatives underway for post-2030 narrowband SATCOM."
        ),
        "fvey_impact": (
            "MUOS provides beyond-line-of-sight communications to tactical forces — "
            "dismounted soldiers, ships, aircraft. FVEY nations have access under "
            "bilateral agreements. Critical for coalition interoperability in "
            "contested environments where commercial SATCOM may be denied."
        ),
        "source": "US Navy PEO Space Systems; USSF budget justification; CRS RL33153",
    },
    {
        "program": "AUKUS Pillar II — Space Domain Awareness",
        "contractor": "Multiple (US/UK/AU industry)",
        "awarding_agency": "AUKUS Advanced Capabilities Group",
        "value_usd": "Classified (estimated $500M initial tranche)",
        "contract_type": "Government-to-government framework",
        "period": "2024–2035+",
        "status": "active — early capability development",
        "description": (
            "AUKUS Pillar II advanced capabilities includes deep space radar, "
            "optical SSA sensors, SDA data sharing, and resilient SATCOM. Specific "
            "projects include Space Surveillance Telescope relocation to NW Cape "
            "Australia, shared SSA data processing, and joint counter-space "
            "capability development."
        ),
        "fvey_impact": (
            "AUKUS space cooperation is the most significant expansion of FVEY "
            "space capability sharing since the original UKUSA agreement. Fills "
            "Southern Hemisphere SSA gap, establishes trilateral space operations "
            "interoperability, and accelerates allied counter-space posture."
        ),
        "source": "AUKUS Joint Leaders Statement 2024; ASD media release; US DoD fact sheet",
    },
]

# ===========================================================================
#  3. SUPPLY CHAIN VULNERABILITIES (10 entries)
# ===========================================================================

_SUPPLY_CHAIN_VULNS: List[dict] = [
    {
        "component": "Rare Earth Elements (REE)",
        "vulnerability": "critical",
        "prc_dependency_pct": 80,
        "description": (
            "Neodymium, samarium, dysprosium, and other rare earths essential for "
            "permanent magnets in reaction wheels, control moment gyros, solar array "
            "drives, and electric propulsion systems. PRC controls ~60% of global "
            "mining and ~90% of processing/refining capacity."
        ),
        "affected_systems": [
            "Reaction wheels / CMGs (satellite attitude control)",
            "Electric propulsion (Hall-effect thrusters)",
            "Solar array drive assemblies",
            "Precision actuators and motors",
            "Traveling wave tube amplifiers (TWTAs)",
        ],
        "mitigation_status": (
            "US DOE Critical Minerals Strategy; DOD Title III DPA investments; "
            "MP Materials (Mountain Pass, CA) domestic mining restart; Lynas Rare Earths "
            "(Australia) expansion with US DOD funding; EU Critical Raw Materials Act. "
            "However, refining capacity remains concentrated in PRC."
        ),
        "risk_scenario": (
            "PRC export restriction or embargo on rare earths during a Taiwan Strait "
            "crisis would halt or severely constrain satellite manufacturing for 12-24 "
            "months until alternative refining capacity comes online."
        ),
    },
    {
        "component": "Radiation-Hardened (Rad-Hard) Semiconductors",
        "vulnerability": "high",
        "prc_dependency_pct": 5,
        "description": (
            "Rad-hard processors, FPGAs, memory, and ASICs for space-grade electronics. "
            "Limited to a few qualified foundries: BAE Systems (Manassas, VA), Microchip "
            "(Chandler, AZ), Intel Custom Foundry, and European Atmel/Microchip. "
            "Long lead times (18-36 months) and single-source risks."
        ),
        "affected_systems": [
            "All satellite on-board computers",
            "Payload data processing",
            "Attitude determination and control",
            "Communication transponders (digital)",
            "GPS receivers (military-grade)",
        ],
        "mitigation_status": (
            "DARPA ERI (Electronics Resurgence Initiative); CHIPS Act funding for "
            "domestic semiconductor production; Radiation-hardened-by-design (RHBD) "
            "approaches using commercial foundries; USSF rad-hard FPGA qualification "
            "programs. Single-source risk remains for some critical components."
        ),
        "risk_scenario": (
            "Fab disruption at BAE Manassas or Microchip Chandler would delay "
            "multiple national security satellite programs by 2+ years. No rapid "
            "alternative for mil-spec rad-hard parts."
        ),
    },
    {
        "component": "Space-Grade Solar Cells (III-V Multi-Junction)",
        "vulnerability": "high",
        "prc_dependency_pct": 15,
        "description": (
            "Triple-junction (InGaP/GaAs/Ge) and next-gen quad-junction solar cells "
            "for satellite power generation. Primary Western suppliers: Rocket Lab "
            "(SolAero — Albuquerque, NM), Spectrolab (Boeing subsidiary — Sylmar, CA), "
            "and Azur Space (Germany). PRC has growing domestic capability (CTJ-30+)."
        ),
        "affected_systems": [
            "All satellite solar arrays",
            "Space station power systems",
            "Deep space probe power",
            "High-power GEO SATCOM platforms",
            "Lunar surface power systems",
        ],
        "mitigation_status": (
            "Rocket Lab acquisition of SolAero (2022) consolidated US supply. "
            "Spectrolab remains Boeing-captive. Azur Space (Germany) provides "
            "European alternative. Perovskite-tandem R&D may diversify supply "
            "long-term. Current capacity is tight for mega-constellation demand."
        ),
        "risk_scenario": (
            "SolAero or Spectrolab production disruption would bottleneck all US "
            "military and commercial satellite manufacturing. Dual-source strategy "
            "is limited by facility count."
        ),
    },
    {
        "component": "Star Trackers",
        "vulnerability": "medium",
        "prc_dependency_pct": 0,
        "description": (
            "Precision optical attitude determination sensors. Key Western suppliers: "
            "Ball Aerospace (CT-2020), Leonardo (AA-STR), Sodern/Airbus (Hydra/SED36), "
            "Terma (T1/T3). ITAR-controlled — PRC develops indigenous alternatives. "
            "Lead times of 12-18 months for flight-qualified units."
        ),
        "affected_systems": [
            "All precision-pointed satellites",
            "EO/IR imaging satellites (arc-second pointing)",
            "Missile warning satellites",
            "Navigation satellites",
            "Scientific observatories",
        ],
        "mitigation_status": (
            "Multiple qualified Western suppliers. ITAR controls prevent diversion "
            "to adversaries. Main risk is long lead time and limited production "
            "surge capacity for rapid constellation deployment scenarios."
        ),
        "risk_scenario": (
            "Demand surge from SDA PWSA + Starlink/Starshield + commercial "
            "constellations could exceed star tracker production capacity, "
            "causing delivery delays across national security programs."
        ),
    },
    {
        "component": "Reaction Wheels and Control Moment Gyros",
        "vulnerability": "medium",
        "prc_dependency_pct": 0,
        "description": (
            "Momentum exchange devices for satellite attitude control. Key suppliers: "
            "Collins Aerospace (formerly Rockwell Collins), Honeywell Aerospace, "
            "Rocket Lab (Sinclair Interplanetary), RUAG Space, and Bradford Space. "
            "Rare earth permanent magnets are a sub-component dependency."
        ),
        "affected_systems": [
            "All agile satellites (EO, SAR imaging)",
            "Space stations and large platforms",
            "Precision-pointed GEO SATCOM",
            "Missile warning satellites",
            "Scientific observatories",
        ],
        "mitigation_status": (
            "Rocket Lab acquisition of Sinclair Interplanetary added smallsat reaction "
            "wheel capability. Collins and Honeywell serve larger platforms. Underlying "
            "rare earth magnet dependency remains the primary risk vector."
        ),
        "risk_scenario": (
            "Rare earth supply disruption cascades into reaction wheel production "
            "bottleneck within 6 months as magnet inventories deplete."
        ),
    },
    {
        "component": "Launch Vehicle Propulsion — Liquid Engines",
        "vulnerability": "high",
        "prc_dependency_pct": 0,
        "description": (
            "LOX/kerosene, LOX/LH2, and LOX/methane engines for orbital launch. "
            "Key US engines: SpaceX Merlin/Raptor, Blue Origin BE-4, Aerojet Rocketdyne "
            "RS-25/RL-10. US previously depended on Russian RD-180 (Atlas V) — now "
            "eliminated with Vulcan/BE-4 transition. European Vulcain 2.1 / Vinci for "
            "Ariane 6. Single-source risk for several engine types."
        ),
        "affected_systems": [
            "Falcon 9/Heavy (Merlin 1D)",
            "Vulcan Centaur (BE-4 / RL-10C-2)",
            "New Glenn (BE-4)",
            "SLS (RS-25 / RL-10)",
            "Ariane 6 (Vulcain 2.1 / Vinci)",
        ],
        "mitigation_status": (
            "RD-180 dependency eliminated (last Atlas V with RD-180 in 2024). "
            "SpaceX vertically integrated. BE-4 production ramping for ULA and "
            "Blue Origin. Aerojet Rocketdyne (now L3Harris) is sole-source for "
            "RS-25 and RL-10. USSF Launch Enterprise driving dual-source strategy."
        ),
        "risk_scenario": (
            "BE-4 production bottleneck at Blue Origin delays both Vulcan and "
            "New Glenn — concentrating national security launch on SpaceX alone, "
            "eliminating assured access dual-provider strategy."
        ),
    },
    {
        "component": "Satellite Buses — GEO Class",
        "vulnerability": "medium",
        "prc_dependency_pct": 0,
        "description": (
            "High-power GEO satellite bus platforms. Western providers: Lockheed Martin "
            "(LM2100), Boeing (702), Northrop Grumman (GEOStar), Airbus (Eurostar Neo), "
            "Thales Alenia Space (Spacebus Neo). Limited to 5-6 global providers for "
            "mil-spec GEO platforms."
        ),
        "affected_systems": [
            "WGS (Boeing 702HP)",
            "AEHF/ESS (Lockheed Martin A2100/LM2100)",
            "Skynet 6A (Airbus Eurostar)",
            "MUOS (Lockheed Martin A2100)",
            "SBIRS GEO (Lockheed Martin A2100)",
        ],
        "mitigation_status": (
            "Multiple qualified Western providers. GEO market contraction (fewer "
            "commercial orders) is reducing production line health and workforce "
            "retention. DoD may face cost escalation as commercial volume declines."
        ),
        "risk_scenario": (
            "GEO satellite bus production lines become intermittent as commercial "
            "market shifts to LEO constellations. Loss of skilled workforce and "
            "supplier base increases cost and schedule risk for military GEO programs."
        ),
    },
    {
        "component": "Traveling Wave Tube Amplifiers (TWTAs)",
        "vulnerability": "high",
        "prc_dependency_pct": 5,
        "description": (
            "High-power RF amplifiers for satellite communications transponders. "
            "Key suppliers: L3Harris (Electron Devices), Thales Electron Devices, "
            "CPI (Communications & Power Industries). TWTAs require specialized "
            "vacuum tube manufacturing — extremely niche capability."
        ),
        "affected_systems": [
            "All MILSATCOM transponders (WGS, AEHF, Skynet, MUOS)",
            "Commercial GEO SATCOM",
            "SIGINT/ELINT satellite receivers",
            "Radar transponder systems",
            "Deep space communication (high-power downlink)",
        ],
        "mitigation_status": (
            "Solid-state power amplifiers (SSPAs) replacing TWTAs for some applications "
            "but cannot match TWTA efficiency at highest power levels. Only 3 Western "
            "TWTA manufacturers. DOD Title III investments in TWTA production capacity."
        ),
        "risk_scenario": (
            "Single TWTA facility disruption (e.g., L3Harris Torrance, CA) would "
            "bottleneck all US military SATCOM satellite production for 18+ months."
        ),
    },
    {
        "component": "Encryption / COMSEC Modules (Type 1)",
        "vulnerability": "low",
        "prc_dependency_pct": 0,
        "description": (
            "NSA-certified Type 1 encryption devices for classified satellite "
            "communications. Sole provider: General Dynamics Mission Systems (TACLANE, "
            "KGV-72, KI-series). ITAR/NOFORN controlled. FVEY nations have bilateral "
            "COMSEC agreements for interoperability."
        ),
        "affected_systems": [
            "AEHF/ESS terminals",
            "WGS MILSATCOM terminals",
            "Skynet terminals (via bilateral agreement)",
            "GPS M-Code receivers",
            "SIPRNet/JWICS satellite links",
        ],
        "mitigation_status": (
            "Sole-source risk but sovereign US capability with no foreign dependency. "
            "NSA/CSS manages Type 1 crypto supply. FVEY interoperability maintained "
            "via bilateral COMSEC agreements (UKUSA heritage)."
        ),
        "risk_scenario": (
            "Not a supply chain risk from adversary — primary risk is quantum computing "
            "threat to current encryption algorithms (PQC transition timeline)."
        ),
    },
    {
        "component": "Xenon / Krypton Propellant (Electric Propulsion)",
        "vulnerability": "medium",
        "prc_dependency_pct": 25,
        "description": (
            "Noble gas propellant for Hall-effect and ion thrusters used in satellite "
            "stationkeeping and orbit-raising. Global xenon supply ~60 tonnes/year, "
            "primarily from air separation units. Russia and PRC are significant "
            "producers. Krypton is an emerging lower-cost alternative."
        ),
        "affected_systems": [
            "All-electric GEO satellites (orbit raising)",
            "LEO constellation stationkeeping (Starlink uses krypton)",
            "Northrop Grumman MEV (life extension vehicles)",
            "Military GEO SATCOM (EP stationkeeping)",
            "Deep space missions (ion propulsion)",
        ],
        "mitigation_status": (
            "Starlink's shift from xenon to krypton eased xenon supply pressure. "
            "New air separation units planned in US and Australia. However, demand "
            "growth from mega-constellations may outpace supply expansion."
        ),
        "risk_scenario": (
            "Xenon supply disruption during a conflict involving Russia/PRC "
            "could limit satellite stationkeeping propellant availability, "
            "potentially shortening operational lifetimes of military GEO assets."
        ),
    },
]

# ===========================================================================
#  4. GRANTS & R&D PROGRAMS (10 entries)
# ===========================================================================

_GRANTS_FUNDING: List[dict] = [
    {
        "program": "DARPA Blackjack",
        "agency": "Defense Advanced Research Projects Agency (DARPA)",
        "country": "US",
        "budget_usd": "$325M (program total)",
        "period": "2018–2025",
        "status": "transitioning to SDA PWSA",
        "description": (
            "Demonstrated military utility of commercial LEO constellation technology "
            "for DoD missions. Blackjack validated that commercial satellite buses with "
            "military payloads in LEO can provide comparable capability to exquisite "
            "GEO systems at a fraction of the cost. Pathfinder for SDA PWSA architecture."
        ),
        "research_areas": [
            "Proliferated LEO architecture validation",
            "Autonomous satellite battle management",
            "Optical inter-satellite links (OISL)",
            "Missile tracking from LEO",
            "Pit Boss autonomous mission management",
        ],
        "fvey_relevance": (
            "Blackjack proved the concept that underpins SDA PWSA — the most important "
            "US military space architecture shift in decades. FVEY partners benefit "
            "from PWSA interoperability and data sharing."
        ),
    },
    {
        "program": "SDA Proliferated Warfighter Space Architecture (PWSA) R&D",
        "agency": "Space Development Agency / US Space Force",
        "country": "US",
        "budget_usd": "$4.6B (FY2025 request)",
        "period": "2019–ongoing (spiral development)",
        "status": "active — Tranche 1/2 procurement + Tranche 3 R&D",
        "description": (
            "Continuous R&D and rapid acquisition for the PWSA constellation layers. "
            "Tranche 3 R&D includes advanced missile tracking sensors, fire control "
            "quality custody, enhanced OISL throughput, battle management C2, and "
            "integration with JADC2 (Joint All-Domain Command and Control)."
        ),
        "research_areas": [
            "Hypersonic missile tracking algorithms",
            "Laser inter-satellite link scaling (100+ Gbps)",
            "On-board AI/ML for autonomous tracking",
            "Resilient mesh networking protocols",
            "Rapid satellite manufacturing (18-month build cycle)",
        ],
        "fvey_relevance": (
            "PWSA is designed for FVEY interoperability from inception. Transport Layer "
            "provides global low-latency backbone for allied fire control data sharing. "
            "AUKUS missile defense cooperation directly leverages PWSA data."
        ),
    },
    {
        "program": "US Space Force SBIR/STTR Program",
        "agency": "US Space Force — SpaceWERX",
        "country": "US",
        "budget_usd": "$500M+ annually",
        "period": "ongoing",
        "status": "active — continuous solicitation",
        "description": (
            "Small Business Innovation Research (SBIR) and Small Business Technology "
            "Transfer (STTR) program operated by SpaceWERX (AFWERX space division). "
            "Funds small businesses to develop innovative space technologies across "
            "all mission areas: launch, satellite, ground segment, SSA, cyber, and C2."
        ),
        "research_areas": [
            "Responsive space launch technologies",
            "On-orbit servicing and manufacturing",
            "Space domain awareness sensors",
            "Cyber-resilient satellite architectures",
            "Counter-space defensive measures",
            "Autonomous satellite operations",
        ],
        "fvey_relevance": (
            "SBIR innovations flow into major programs of record that benefit FVEY. "
            "SpaceWERX Strategic Financing (Strat-Fi) and Tactical Financing (Tac-Fi) "
            "bridge SBIR to production, accelerating technology transfer."
        ),
    },
    {
        "program": "AUKUS Pillar II — Advanced Space Capabilities",
        "agency": "AUKUS Advanced Capabilities Group (AU/UK/US)",
        "country": "Australia / UK / US",
        "budget_usd": "Classified (estimated $1B+ over 10 years)",
        "period": "2023–2035+",
        "status": "active — early projects underway",
        "description": (
            "Trilateral R&D cooperation under AUKUS Pillar II for deep space "
            "surveillance, space domain awareness, resilient SATCOM, electronic "
            "warfare in space, and counter-space technologies. Includes ITAR/EAR "
            "exemptions for faster technology sharing between US, UK, and Australia."
        ),
        "research_areas": [
            "Deep space radar and optical SSA",
            "Resilient MILSATCOM architectures",
            "Counter-space capability development",
            "Space electronic warfare",
            "AI/ML for space C2 and SSA",
            "Quantum-resistant space communications",
        ],
        "fvey_relevance": (
            "AUKUS Pillar II is the most significant FVEY space technology sharing "
            "expansion. ITAR exemptions enable unprecedented industrial collaboration. "
            "Space SST relocation to Australia fills Southern Hemisphere SSA gap."
        ),
    },
    {
        "program": "Australian Space Agency — Moon to Mars Initiative",
        "agency": "Australian Space Agency",
        "country": "Australia",
        "budget_usd": "AUD 150M ($100M)",
        "period": "2019–2030",
        "status": "active",
        "description": (
            "Australian government initiative to grow domestic space industry through "
            "participation in NASA Artemis program. Funds Australian companies to "
            "develop lunar surface robotics, communications, resource processing, "
            "and space medicine technologies."
        ),
        "research_areas": [
            "Autonomous lunar rover systems",
            "Optical communications for deep space",
            "In-situ resource utilization (ISRU)",
            "Space medicine and life support",
            "AI for remote autonomous operations",
            "Radiation shielding materials",
        ],
        "fvey_relevance": (
            "Builds Australian space industrial base relevant to FVEY space defense. "
            "Technologies developed for cislunar operations have dual-use applications "
            "for military space domain awareness and operations."
        ),
    },
    {
        "program": "UK National Space Strategy Implementation",
        "agency": "UK Space Agency / UK MOD",
        "country": "UK",
        "budget_usd": "£1.6B ($2B) over 10 years",
        "period": "2022–2032",
        "status": "active",
        "description": (
            "Implementation of the 2021 UK National Space Strategy and Defence Space "
            "Strategy (DSIS 2022). Funds sovereign SSA, launch from UK soil (SaxaVord "
            "Spaceport, Sutherland), OneWeb investment for sovereign LEO broadband, "
            "and military space capability through UK Space Command."
        ),
        "research_areas": [
            "Sovereign SSA sensor network",
            "UK vertical launch capability",
            "Space debris monitoring and removal",
            "Quantum key distribution via satellite",
            "Space electronic warfare",
            "Persistent surveillance from space",
        ],
        "fvey_relevance": (
            "UK National Space Strategy directly enhances FVEY space posture. "
            "Sovereign UK SSA contributes to FVEY SSA sharing. SaxaVord Spaceport "
            "provides polar orbit access from European soil. Space Command integration "
            "with CSpO enhances combined operations."
        ),
    },
    {
        "program": "NATO Defence Innovation Accelerator for the North Atlantic (DIANA)",
        "agency": "NATO DIANA",
        "country": "NATO (multinational)",
        "budget_usd": "€1B ($1.1B) innovation fund",
        "period": "2023–2033",
        "status": "active — first cohorts selected",
        "description": (
            "NATO's innovation accelerator supporting dual-use technology startups "
            "across alliance nations. Space-relevant focus areas include satellite "
            "communications resilience, space situational awareness, counter-UAS "
            "(space-adjacent), and AI for defence."
        ),
        "research_areas": [
            "Resilient SATCOM for contested environments",
            "AI/ML for space domain awareness",
            "Small satellite rapid manufacturing",
            "Counter-space detection and attribution",
            "Quantum sensing for SSA",
            "Space debris remediation technologies",
        ],
        "fvey_relevance": (
            "DIANA bridges FVEY innovation with broader NATO alliance. Test centres "
            "in US, UK, Canada, and across Europe. Accelerates dual-use technology "
            "adoption from commercial sector into allied military space."
        ),
    },
    {
        "program": "Defense Innovation Unit (DIU) — Space Portfolio",
        "agency": "Defense Innovation Unit (DIU)",
        "country": "US",
        "budget_usd": "$200M+ annually (space-related prototyping)",
        "period": "ongoing",
        "status": "active",
        "description": (
            "DIU bridges commercial innovation to DoD operational needs through "
            "Other Transaction Authority (OTA) contracts. Space portfolio includes "
            "commercial SSA data procurement, hybrid space architectures, responsive "
            "launch, and commercial SATCOM integration."
        ),
        "research_areas": [
            "Commercial SSA data fusion",
            "Hybrid government-commercial space architectures",
            "Responsive space launch services",
            "Commercial SATCOM for tactical forces",
            "On-orbit servicing prototyping",
            "Mesh networking for contested environments",
        ],
        "fvey_relevance": (
            "DIU's commercial-to-military pipeline creates exportable capabilities. "
            "Commercial SSA data sharing models (LeoLabs, ExoAnalytic) directly "
            "benefit FVEY SSA cooperation."
        ),
    },
    {
        "program": "Air Force Research Laboratory (AFRL) — Space Vehicles Directorate",
        "agency": "Air Force Research Laboratory (AFRL/RV)",
        "country": "US",
        "budget_usd": "$1.2B annually",
        "period": "ongoing",
        "status": "active",
        "description": (
            "AFRL Space Vehicles Directorate at Kirtland AFB, NM conducts foundational "
            "and applied research for USSF space systems. Programs include advanced "
            "spacecraft technology, space control, SSA, and space environment effects."
        ),
        "research_areas": [
            "Solar sail and advanced propulsion",
            "Deployable space structures",
            "Space situational awareness algorithms",
            "Radiation effects on electronics",
            "Satellite autonomy and AI",
            "Space-based laser communication",
            "Counter-space technology assessment",
            "Space weather prediction models",
        ],
        "fvey_relevance": (
            "AFRL research underpins all US military space technology. FVEY partners "
            "participate in collaborative research programs through bilateral S&T "
            "agreements. AFRL Kirtland hosts allied exchange officers and researchers."
        ),
    },
    {
        "program": "Canadian DRDC — Space Science & Technology Program",
        "agency": "Defence Research and Development Canada (DRDC)",
        "country": "Canada",
        "budget_usd": "CAD 80M ($60M) annually (space-related)",
        "period": "ongoing",
        "status": "active",
        "description": (
            "DRDC's space research supports Canadian Armed Forces space operations "
            "and Five Eyes intelligence sharing. Focus areas include Arctic SSA, "
            "SAR satellite exploitation, space weather effects on Northern operations, "
            "and satellite vulnerability assessment."
        ),
        "research_areas": [
            "Arctic SSA from space (RADARSAT exploitation)",
            "Dark vessel detection (SAR + AIS correlation)",
            "Space weather impact on HF communications",
            "Satellite hardening and resilience",
            "AI for SAR imagery analysis",
            "Quantum communications R&D",
        ],
        "fvey_relevance": (
            "DRDC space research directly feeds Five Eyes intelligence products. "
            "Arctic SSA capability is unique Canadian contribution — no other FVEY "
            "partner has equivalent northern coverage requirement. RADARSAT dark "
            "vessel detection supports FVEY maritime domain awareness."
        ),
    },
]

# ===========================================================================
#  5. INDUSTRY TRENDS (8 entries)
# ===========================================================================

_INDUSTRY_TRENDS: List[dict] = [
    {
        "trend": "Launch Cost Reduction",
        "category": "launch",
        "timeframe": "2015–2030",
        "status": "accelerating",
        "metric": "$/kg to LEO: $54,500 (Shuttle) -> $2,720 (Falcon 9) -> ~$200 target (Starship)",
        "description": (
            "SpaceX Falcon 9 reusability has driven a 10-20x reduction in launch costs "
            "since 2010. Starship fully-reusable architecture targets a further 10x "
            "reduction to ~$200/kg to LEO. Competitors (Rocket Lab Neutron, Blue Origin "
            "New Glenn, Relativity Terran R, Stoke Nova) are developing reusable vehicles. "
            "Chinese commercial launchers (iSpace, LandSpace, Galactic Energy) also "
            "pursuing reusability."
        ),
        "strategic_implications": (
            "Dramatically lowers the cost of deploying resilient proliferated constellations. "
            "Enables rapid reconstitution of degraded constellations during conflict. "
            "Reduces the cost-exchange ratio disadvantage of space assets vs ASAT weapons. "
            "A potential game-changer for FVEY space architecture affordability."
        ),
        "key_players": ["SpaceX", "Blue Origin", "Rocket Lab", "Relativity Space", "Stoke Space", "iSpace (PRC)"],
    },
    {
        "trend": "Smallsat / CubeSat Proliferation",
        "category": "manufacturing",
        "timeframe": "2012–2030",
        "status": "mature growth",
        "metric": "~400 smallsats/year (2020) -> ~2,800/year (2024) -> ~4,000+/year (projected 2028)",
        "description": (
            "Small satellites (<500 kg) now dominate launch manifests driven by "
            "mega-constellation deployments and commercial EO/IoT markets. Manufacturing "
            "has shifted from artisanal to production-line: SpaceX produces 5-6 Starlink "
            "satellites per day. SDA PWSA leverages commercial smallsat bus technology "
            "for military missions at commercial cost and schedule."
        ),
        "strategic_implications": (
            "Proliferation makes constellations inherently more resilient — destroying "
            "individual satellites has diminishing military utility. Enables 'responsive "
            "space' reconstitution concepts. However, also lowers the barrier for "
            "adversary reconnaissance constellations (PRC Yaogan expansion)."
        ),
        "key_players": ["SpaceX", "Planet Labs", "Spire Global", "L3Harris", "York Space Systems", "Loft Orbital"],
    },
    {
        "trend": "Mega-Constellation Deployment",
        "category": "communications",
        "timeframe": "2019–2035",
        "status": "rapid deployment",
        "metric": "Starlink: 6,400+ sats on orbit; Kuiper: 3,236 planned; Guowang (PRC): 12,992 planned",
        "description": (
            "Multiple mega-constellations deploying or planning: SpaceX Starlink "
            "(~12,000 authorized, 42,000 applied for), Amazon Kuiper (3,236), Eutelsat "
            "OneWeb (648), Telesat Lightspeed (198), PRC Guowang (12,992), PRC G60 "
            "Starlink-equivalent (~12,000). These constellations are reshaping the "
            "orbital environment and RF spectrum allocation."
        ),
        "strategic_implications": (
            "Creates a dual-use broadband infrastructure with military potential — "
            "Starshield demonstrates this for US DoD. PRC mega-constellations (Guowang, "
            "G60) will provide independent Chinese broadband globally, reducing "
            "FVEY information advantage. Massive increase in tracked objects complicates "
            "SSA and conjunction assessment."
        ),
        "key_players": ["SpaceX", "Amazon Kuiper", "Eutelsat OneWeb", "Telesat", "Shanghai CAST (Guowang)", "PRC G60"],
    },
    {
        "trend": "In-Space Servicing, Assembly, and Manufacturing (ISAM)",
        "category": "on_orbit_operations",
        "timeframe": "2020–2035",
        "status": "early operational",
        "metric": "MEV-1/2 operational (2020/2021); MRV launching 2025; OSAM-1 in development",
        "description": (
            "On-orbit satellite servicing transitioning from demonstration to commercial "
            "operations. Northrop Grumman MEV-1/MEV-2 successfully extended GEO satellite "
            "lifetimes. Mission Robotic Vehicle (MRV) with mission extension pods launching "
            "2025. NASA OSAM-1 will demonstrate robotic satellite refueling. Astroscale "
            "demonstrating active debris removal. PRC SJ-21 demonstrated GEO object "
            "relocation (2022) — dual-use military concern."
        ),
        "strategic_implications": (
            "ISAM enables life extension of expensive GEO military satellites, reducing "
            "replacement costs. Also enables adversary co-orbital inspection, sabotage, "
            "or capture of FVEY satellites. PRC SJ-21 GEO operations are a direct "
            "threat indicator. FVEY must develop both capability and defense against it."
        ),
        "key_players": ["Northrop Grumman (MEV/MRV)", "Astroscale", "Orbit Fab", "NASA (OSAM-1)", "PRC (SJ-21)"],
    },
    {
        "trend": "Active Debris Removal (ADR)",
        "category": "sustainability",
        "timeframe": "2025–2035",
        "status": "demonstration phase",
        "metric": "ESA ClearSpace-1 (2026); Astroscale ADRAS-J demo (2024); JAXA CRD2",
        "description": (
            "Growing international recognition that active debris removal is necessary "
            "to prevent Kessler syndrome in critical LEO orbital shells. ESA ClearSpace-1 "
            "mission (launching 2026) will demonstrate capture and deorbit of a Vega "
            "upper stage. Astroscale ADRAS-J completed rendezvous with a debris object "
            "in 2024. Japan, UK, and US all funding ADR technology development."
        ),
        "strategic_implications": (
            "ADR technology is inherently dual-use — a vehicle that can capture debris "
            "can also capture adversary satellites. Raises arms control verification "
            "challenges. However, LEO debris environment is approaching tipping point "
            "that could deny orbital regimes critical for military ISR (700-900 km)."
        ),
        "key_players": ["ESA / ClearSpace", "Astroscale", "JAXA", "D-Orbit", "UK Space Agency"],
    },
    {
        "trend": "Commercial Space Situational Awareness (SSA)",
        "category": "surveillance",
        "timeframe": "2018–2030",
        "status": "rapid growth",
        "metric": "LeoLabs: 6 radar sites; ExoAnalytic: 300+ telescopes; Slingshot Aerospace: AI platform",
        "description": (
            "Commercial SSA providers supplementing and in some cases surpassing "
            "government SSA capabilities. LeoLabs operates a global network of "
            "phased-array radars tracking 250,000+ objects. ExoAnalytic Solutions "
            "operates the world's largest commercial telescope network for GEO "
            "surveillance. Slingshot Aerospace provides AI-driven conjunction "
            "assessment and space traffic management."
        ),
        "strategic_implications": (
            "Commercial SSA democratizes space awareness — allies can procure SSA "
            "data without classified sharing agreements. Also means adversaries can "
            "access commercial SSA to track FVEY military satellites. Drives need "
            "for stealth/LO satellite technology. FVEY should integrate commercial "
            "SSA into Combined Space Operations Center (CSpOC) data fusion."
        ),
        "key_players": ["LeoLabs", "ExoAnalytic Solutions", "Slingshot Aerospace", "Numerica", "AGI/Ansys"],
    },
    {
        "trend": "Space-Based Solar Power (SBSP)",
        "category": "energy",
        "timeframe": "2025–2045",
        "status": "early R&D / demonstration",
        "metric": "Caltech SSPD-1 demo (2023); ESA SOLARIS study; PRC 2028 demo target; UK Space Energy Initiative",
        "description": (
            "Space-based solar power collects solar energy in GEO and transmits it "
            "to Earth via microwave or laser. Caltech SSPD-1 demonstrated wireless "
            "power transmission from orbit (2023). ESA SOLARIS program studying "
            "European SBSP architecture. PRC planning multi-megawatt demonstration "
            "by 2028 and operational system by 2035. UK Space Energy Initiative "
            "studying 2035+ deployment."
        ),
        "strategic_implications": (
            "SBSP could provide energy independence from terrestrial fuel supplies — "
            "strategic significance comparable to nuclear power. Microwave power "
            "beaming technology has dual-use directed energy weapon potential. "
            "PRC SBSP program is a long-term strategic concern. FVEY should monitor "
            "and invest to avoid technology surprise."
        ),
        "key_players": ["Caltech/Northrop SSPD", "ESA SOLARIS", "PRC (CAST)", "UK Space Energy Initiative", "JAXA"],
    },
    {
        "trend": "Cislunar Economy and Military Operations",
        "category": "cislunar",
        "timeframe": "2024–2040",
        "status": "emerging",
        "metric": "Artemis III (2026); Chang'e-7 (2026); ILRS vs Gateway; AFRL cislunar SSA R&D",
        "description": (
            "Human and robotic operations expanding beyond GEO into cislunar space "
            "(Earth-Moon system). Two competing blocs: US-led Artemis Accords (40+ "
            "signatories) with Lunar Gateway station, vs PRC-Russia International "
            "Lunar Research Station (ILRS). USSF and AFRL developing cislunar SSA "
            "capability. Commercial lunar landers (Astrobotic, Intuitive Machines, "
            "ispace) establishing cislunar logistics."
        ),
        "strategic_implications": (
            "Cislunar space is the next contested domain. Current SSA architecture "
            "has negligible coverage beyond GEO. PRC cislunar presence (Chang'e, "
            "ILRS) creates potential for space resource competition and military "
            "positioning. Lagrange points (L1, L2, L4, L5) are strategically "
            "significant for surveillance and staging. FVEY must extend domain "
            "awareness to cislunar — a 10-year capability gap exists."
        ),
        "key_players": [
            "NASA Artemis",
            "SpaceX (Starship HLS)",
            "Blue Origin (Blue Moon)",
            "PRC Chang'e / ILRS",
            "Astrobotic",
            "Intuitive Machines",
            "AFRL cislunar R&D",
        ],
    },
]


# ===========================================================================
#  PUBLIC API — synchronous data functions
# ===========================================================================

def get_defense_contractors() -> dict:
    """Return full defense contractor database."""
    hit = _cached("contractors")
    if hit:
        return hit

    all_contractors = _US_PRIMES + _ALLIED_CONTRACTORS + _ADVERSARY_INDUSTRY
    summary = {
        "us_primes": len(_US_PRIMES),
        "allied": len(_ALLIED_CONTRACTORS),
        "adversary": len(_ADVERSARY_INDUSTRY),
        "total": len(all_contractors),
    }
    result = _wrap("contractors", {
        "summary": summary,
        "us_primes": _US_PRIMES,
        "allied_contractors": _ALLIED_CONTRACTORS,
        "adversary_industry": _ADVERSARY_INDUSTRY,
    })
    return _store("contractors", result)


def get_major_contracts() -> dict:
    """Return major defense space contracts database."""
    hit = _cached("contracts")
    if hit:
        return hit

    total_value = 0
    for c in _MAJOR_CONTRACTS:
        val_str = c.get("value_usd", "")
        # Extract first numeric value from string like "$7.2B" or "AUD 3-5B"
        import re
        nums = re.findall(r"[\d.]+", val_str)
        if nums:
            factor = 1.0
            if "B" in val_str.upper():
                factor = 1e9
            elif "M" in val_str.upper():
                factor = 1e6
            total_value += float(nums[0]) * factor

    result = _wrap("contracts", {
        "total_contracts": len(_MAJOR_CONTRACTS),
        "estimated_total_value_usd": f"${total_value / 1e9:.1f}B+",
        "contracts": _MAJOR_CONTRACTS,
    })
    return _store("contracts", result)


def get_supply_chain_vulns() -> dict:
    """Return supply chain vulnerability analysis."""
    hit = _cached("supply_chain")
    if hit:
        return hit

    critical_count = sum(1 for v in _SUPPLY_CHAIN_VULNS if v["vulnerability"] == "critical")
    high_count = sum(1 for v in _SUPPLY_CHAIN_VULNS if v["vulnerability"] == "high")
    avg_prc = sum(v["prc_dependency_pct"] for v in _SUPPLY_CHAIN_VULNS) / len(_SUPPLY_CHAIN_VULNS)

    result = _wrap("supply_chain", {
        "total_vulnerabilities": len(_SUPPLY_CHAIN_VULNS),
        "critical_count": critical_count,
        "high_count": high_count,
        "average_prc_dependency_pct": round(avg_prc, 1),
        "assessment": (
            f"{critical_count} critical and {high_count} high-severity supply chain "
            f"vulnerabilities identified. Average PRC dependency across space components "
            f"is {avg_prc:.0f}%. Rare earth elements represent the single greatest "
            f"supply chain risk to FVEY space programs."
        ),
        "vulnerabilities": _SUPPLY_CHAIN_VULNS,
    })
    return _store("supply_chain", result)


def get_grants_funding() -> dict:
    """Return R&D grants and funding programs."""
    hit = _cached("grants")
    if hit:
        return hit

    by_country: Dict[str, int] = {}
    for g in _GRANTS_FUNDING:
        country = g["country"]
        by_country[country] = by_country.get(country, 0) + 1

    result = _wrap("grants", {
        "total_programs": len(_GRANTS_FUNDING),
        "by_country": by_country,
        "grants": _GRANTS_FUNDING,
    })
    return _store("grants", result)


def get_industry_trends() -> dict:
    """Return industry trends analysis."""
    hit = _cached("trends")
    if hit:
        return hit

    categories = list({t["category"] for t in _INDUSTRY_TRENDS})
    result = _wrap("trends", {
        "total_trends": len(_INDUSTRY_TRENDS),
        "categories": sorted(categories),
        "trends": _INDUSTRY_TRENDS,
    })
    return _store("trends", result)


# ===========================================================================
#  ASYNC API — live data from SAM.gov, USAspending, SBIR
# ===========================================================================

async def _fetch_sam_gov(client: httpx.AsyncClient) -> dict:
    """Fetch recent space/defense opportunities from SAM.gov API."""
    try:
        url = "https://api.sam.gov/opportunities/v2/search"
        params = {
            "api_key": "DEMO_KEY",
            "postedFrom": "01/01/2025",
            "limit": 10,
            "keyword": "satellite space",
            "ptype": "o",  # opportunities
        }
        resp = await client.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            opportunities = data.get("opportunitiesData", [])
            return {
                "source": "SAM.gov",
                "status": "live",
                "count": len(opportunities),
                "opportunities": [
                    {
                        "title": opp.get("title", ""),
                        "solicitation_number": opp.get("solicitationNumber", ""),
                        "department": opp.get("department", ""),
                        "posted_date": opp.get("postedDate", ""),
                        "response_deadline": opp.get("responseDeadLine", ""),
                        "type": opp.get("type", ""),
                        "url": opp.get("uiLink", ""),
                    }
                    for opp in opportunities[:10]
                ],
            }
        return {
            "source": "SAM.gov",
            "status": "unavailable",
            "reason": f"HTTP {resp.status_code}",
            "count": 0,
            "opportunities": [],
        }
    except (httpx.HTTPError, httpx.TimeoutException, ValueError) as exc:
        return {
            "source": "SAM.gov",
            "status": "error",
            "reason": str(exc),
            "count": 0,
            "opportunities": [],
        }


async def _fetch_usaspending(client: httpx.AsyncClient) -> dict:
    """Fetch space-related federal spending from USAspending.gov API."""
    try:
        url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
        payload = {
            "filters": {
                "keywords": ["satellite", "space launch", "space domain awareness"],
                "time_period": [{"start_date": "2024-01-01", "end_date": "2025-12-31"}],
                "award_type_codes": ["A", "B", "C", "D"],
            },
            "fields": [
                "Award ID",
                "Recipient Name",
                "Award Amount",
                "Awarding Agency",
                "Description",
                "Start Date",
            ],
            "limit": 10,
            "page": 1,
            "sort": "Award Amount",
            "order": "desc",
        }
        resp = await client.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            return {
                "source": "USAspending.gov",
                "status": "live",
                "count": len(results),
                "awards": [
                    {
                        "award_id": r.get("Award ID", ""),
                        "recipient": r.get("Recipient Name", ""),
                        "amount": r.get("Award Amount", 0),
                        "agency": r.get("Awarding Agency", ""),
                        "description": r.get("Description", ""),
                        "start_date": r.get("Start Date", ""),
                    }
                    for r in results[:10]
                ],
            }
        return {
            "source": "USAspending.gov",
            "status": "unavailable",
            "reason": f"HTTP {resp.status_code}",
            "count": 0,
            "awards": [],
        }
    except (httpx.HTTPError, httpx.TimeoutException, ValueError) as exc:
        return {
            "source": "USAspending.gov",
            "status": "error",
            "reason": str(exc),
            "count": 0,
            "awards": [],
        }


async def _fetch_sbir(client: httpx.AsyncClient) -> dict:
    """Fetch space-related SBIR/STTR awards from SBIR.gov API."""
    try:
        url = "https://api.sbir.gov/public/awards"
        params = {
            "keyword": "satellite space defense",
            "rows": 10,
            "start": 0,
        }
        resp = await client.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            # SBIR API may return results in different structures
            results = data if isinstance(data, list) else data.get("results", data.get("awards", []))
            if isinstance(results, list):
                return {
                    "source": "SBIR.gov",
                    "status": "live",
                    "count": len(results),
                    "awards": [
                        {
                            "company": r.get("firm", r.get("company", "")),
                            "title": r.get("award_title", r.get("title", "")),
                            "agency": r.get("agency", ""),
                            "amount": r.get("award_amount", r.get("amount", 0)),
                            "year": r.get("award_year", r.get("year", "")),
                            "abstract": (r.get("abstract", "") or "")[:300],
                        }
                        for r in results[:10]
                    ],
                }
            return {
                "source": "SBIR.gov",
                "status": "live",
                "count": 0,
                "note": "Unexpected response format",
                "awards": [],
            }
        return {
            "source": "SBIR.gov",
            "status": "unavailable",
            "reason": f"HTTP {resp.status_code}",
            "count": 0,
            "awards": [],
        }
    except (httpx.HTTPError, httpx.TimeoutException, ValueError) as exc:
        return {
            "source": "SBIR.gov",
            "status": "error",
            "reason": str(exc),
            "count": 0,
            "awards": [],
        }


async def get_industry_overview(client: httpx.AsyncClient) -> dict:
    """
    Composite industry intelligence overview with live contract/grant data.

    Fetches from SAM.gov, USAspending.gov, and SBIR.gov APIs concurrently,
    then merges with static industry intelligence databases.
    """
    hit = _cached("overview")
    if hit:
        return hit

    # Fetch all live sources concurrently
    sam_result, usa_result, sbir_result = await asyncio.gather(
        _fetch_sam_gov(client),
        _fetch_usaspending(client),
        _fetch_sbir(client),
    )

    # Compute live source status
    live_sources = [sam_result, usa_result, sbir_result]
    live_count = sum(1 for s in live_sources if s.get("status") == "live")

    # Build static summaries
    contractors = get_defense_contractors()
    contracts = get_major_contracts()
    supply_chain = get_supply_chain_vulns()
    grants = get_grants_funding()
    trends = get_industry_trends()

    result = {
        "classification": _CLASSIFICATION,
        "section": "industry_overview",
        "generated_at": _GENERATED_AT(),
        "live_data_sources": {
            "total": 3,
            "live": live_count,
            "sam_gov": sam_result,
            "usaspending": usa_result,
            "sbir": sbir_result,
        },
        "static_intelligence": {
            "contractors_summary": contractors.get("summary", {}),
            "contracts_count": contracts.get("total_contracts", 0),
            "contracts_total_value": contracts.get("estimated_total_value_usd", ""),
            "supply_chain_critical": supply_chain.get("critical_count", 0),
            "supply_chain_high": supply_chain.get("high_count", 0),
            "avg_prc_dependency_pct": supply_chain.get("average_prc_dependency_pct", 0),
            "rd_programs_count": grants.get("total_programs", 0),
            "industry_trends_count": trends.get("total_trends", 0),
        },
        "assessment": (
            "Space defense industrial base assessment: The US maintains technological "
            "leadership through 10 prime contractors and a robust SBIR ecosystem. "
            "Allied industrial capacity is concentrated in Airbus, Thales, BAE, and MDA. "
            "Critical supply chain vulnerabilities exist in rare earth elements (80% PRC "
            "dependency), rad-hard semiconductors, and TWTA amplifiers. PRC state "
            "enterprises (CASC, CASIC) represent the primary adversary industrial threat "
            "with vertically integrated launch-to-constellation capabilities and an "
            "estimated $50B+ combined annual space expenditure."
        ),
    }
    return _store("overview", result)
