"""
Historical Space Security Incident Database
A structured, searchable database of documented space security incidents
compiled from CSIS Aerospace Security Project, Secure World Foundation,
USSPACECOM, and open-source news reporting.

No public dashboard tool provides this as an integrated, filterable dataset.

Functions:
- get_all_incidents       — full timeline
- get_incidents_by_type   — filter by incident type
- get_incidents_by_actor  — filter by nation
- get_incidents_by_year   — filter by year
- get_incident_stats      — summary statistics

Classification: UNCLASSIFIED // OSINT
All incidents are from public, documented sources.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Incident Database — all events from open sources
# ---------------------------------------------------------------------------

_INCIDENTS = [
    {
        "id": "INCIDENT-2007-001",
        "date": "2007-01-11",
        "title": "PRC FY-1C ASAT Test",
        "type": "DA-ASAT",
        "actors": ["PRC"],
        "description": (
            "People's Republic of China conducted a direct-ascent anti-satellite "
            "weapons test, destroying the decommissioned Fengyun-1C (FY-1C) weather "
            "satellite at approximately 865 km altitude using a kinetic kill vehicle "
            "launched on a modified DF-21 / SC-19 missile. The test created over "
            "3,000 pieces of trackable debris, making it the single worst debris-"
            "generating event in the history of spaceflight. As of 2024, a significant "
            "portion of this debris remains in orbit and continues to pose conjunction "
            "risks to operational satellites."
        ),
        "debris_count": 3000,
        "orbit_affected": "LEO",
        "severity": "critical",
        "source_references": [
            "CSIS Aerospace Security Project — Space Threat Assessment 2023",
            "Secure World Foundation — Global Counterspace Capabilities (2023)",
            "NASA Orbital Debris Quarterly News",
        ],
        "related_norad_ids": [25730],
    },
    {
        "id": "INCIDENT-2008-001",
        "date": "2008-02-21",
        "title": "USA-193 Shootdown (Operation Burnt Frost)",
        "type": "DA-ASAT",
        "actors": ["US"],
        "description": (
            "United States Navy destroyer USS Lake Erie (CG-70) launched a modified "
            "SM-3 Block IA missile to intercept the non-responsive National "
            "Reconnaissance Office satellite USA-193 (NROL-21) at approximately "
            "247 km altitude. The satellite was targeted due to its decaying orbit "
            "and onboard hydrazine fuel tank. The intercept was successful, and the "
            "low altitude ensured most debris re-entered within weeks. The operation "
            "demonstrated US ASAT capability using the Aegis BMD system."
        ),
        "debris_count": 174,
        "orbit_affected": "LEO",
        "severity": "high",
        "source_references": [
            "DoD Press Briefing — 21 Feb 2008",
            "CSIS Aerospace Security Project",
            "Secure World Foundation — Global Counterspace Capabilities",
        ],
        "related_norad_ids": [29651],
    },
    {
        "id": "INCIDENT-2009-001",
        "date": "2009-02-10",
        "title": "Iridium 33 / Cosmos 2251 Collision",
        "type": "collision",
        "actors": ["US", "CIS"],
        "description": (
            "First confirmed accidental hypervelocity collision between two intact "
            "satellites. The operational Iridium 33 communications satellite collided "
            "with the derelict Russian Cosmos 2251 military communications satellite "
            "at approximately 790 km altitude over Siberia, at a relative velocity "
            "of roughly 11.7 km/s. The collision destroyed both spacecraft and "
            "created over 2,000 pieces of trackable debris, significantly increasing "
            "the debris population in the 750-900 km LEO band."
        ),
        "debris_count": 2000,
        "orbit_affected": "LEO",
        "severity": "critical",
        "source_references": [
            "NASA Orbital Debris Quarterly News — Vol 13, Issue 2",
            "USSTRATCOM conjunction assessment",
            "CSIS Aerospace Security Project",
        ],
        "related_norad_ids": [24946, 22675],
    },
    {
        "id": "INCIDENT-2013-001",
        "date": "2013-05-13",
        "title": "PRC DN-2 Exoatmospheric Intercept Test",
        "type": "test",
        "actors": ["PRC"],
        "description": (
            "PRC conducted a high-altitude ballistic missile test assessed by US "
            "intelligence as a test of the Dong Neng-2 (DN-2) exoatmospheric "
            "kinetic kill vehicle. The test reached altitudes consistent with "
            "MEO/GEO-capable ASAT intercept. While officially described as a "
            "\"scientific experiment\" for \"space exploration,\" the trajectory "
            "and characteristics were assessed as a non-destructive ASAT test "
            "that did not create debris, suggesting a fly-by or near-miss profile."
        ),
        "debris_count": 0,
        "orbit_affected": "MEO",
        "severity": "high",
        "source_references": [
            "USAF Space Command statement — May 2013",
            "Secure World Foundation — Global Counterspace Capabilities",
            "NASIC — Competing in Space (2018 assessment)",
        ],
        "related_norad_ids": [],
    },
    {
        "id": "INCIDENT-2014-001",
        "date": "2014-07-23",
        "title": "PRC Co-Orbital ASAT Test (\"Space Debris Cleanup\")",
        "type": "co-orbital",
        "actors": ["PRC"],
        "description": (
            "PRC launched what was officially described as a \"space debris cleanup\" "
            "technology demonstration. The Shijian-17 precursor mission exhibited "
            "co-orbital maneuvering capabilities, including rendezvous and proximity "
            "operations (RPO) with other objects. Western intelligence agencies "
            "assessed the mission as a test of co-orbital ASAT technology, "
            "specifically a robotic arm or grappling mechanism capable of "
            "interfering with adversary satellites."
        ),
        "debris_count": 0,
        "orbit_affected": "LEO",
        "severity": "high",
        "source_references": [
            "Secure World Foundation — Global Counterspace Capabilities (2023)",
            "CSIS — Space Threat Assessment 2023",
            "The Diplomat — \"China's New Space Debris Clean-Up Satellite\"",
        ],
        "related_norad_ids": [],
    },
    {
        "id": "INCIDENT-2015-001",
        "date": "2015-10-16",
        "title": "Russia Cosmos 2504 Inspector Satellite RPO",
        "type": "co-orbital",
        "actors": ["CIS"],
        "description": (
            "Russian military satellite Cosmos 2504, launched in March 2015, "
            "conducted a series of rendezvous and proximity operations (RPO) with "
            "the Briz-KM upper stage from its own launch. The satellite demonstrated "
            "orbital maneuvering capabilities including close approach, station-"
            "keeping, and departure maneuvers. Western analysts assessed these "
            "operations as tests of inspector/co-orbital ASAT technology consistent "
            "with Russia's Burevestnik program."
        ),
        "debris_count": 0,
        "orbit_affected": "LEO",
        "severity": "medium",
        "source_references": [
            "Secure World Foundation — Global Counterspace Capabilities",
            "Union of Concerned Scientists Satellite Database",
            "CSIS — Space Threat Assessment",
        ],
        "related_norad_ids": [40555],
    },
    {
        "id": "INCIDENT-2018-001",
        "date": "2018-02-01",
        "title": "PRC DN-3 Midcourse Interceptor Test",
        "type": "test",
        "actors": ["PRC"],
        "description": (
            "PRC conducted a midcourse missile defense test assessed by US "
            "intelligence as a test of the Dong Neng-3 (DN-3) system. The DN-3 is "
            "a successor to the DN-2 and is designed for midcourse interception "
            "of ballistic missiles and potentially satellites at higher altitudes "
            "than previous systems. China officially described the test as a "
            "\"land-based midcourse missile interception technology\" experiment. "
            "The dual-use nature of midcourse interceptors gives them inherent "
            "ASAT capability."
        ),
        "debris_count": 0,
        "orbit_affected": "LEO",
        "severity": "high",
        "source_references": [
            "PRC Ministry of Defense statement — Feb 2018",
            "NASIC — Competing in Space (2019)",
            "Secure World Foundation — Global Counterspace Capabilities",
        ],
        "related_norad_ids": [],
    },
    {
        "id": "INCIDENT-2019-001",
        "date": "2019-03-27",
        "title": "India Mission Shakti — DA-ASAT Test",
        "type": "DA-ASAT",
        "actors": ["India"],
        "description": (
            "India conducted its first direct-ascent anti-satellite weapons test, "
            "\"Mission Shakti,\" destroying the Microsat-R satellite at approximately "
            "300 km altitude using a modified Prithvi Defense Vehicle Mark-II "
            "interceptor. The relatively low altitude was chosen to ensure debris "
            "would deorbit quickly, though NASA initially tracked approximately "
            "400 debris fragments, with some reaching altitudes above the ISS orbit. "
            "India became the fourth nation to demonstrate ASAT capability."
        ),
        "debris_count": 400,
        "orbit_affected": "LEO",
        "severity": "high",
        "source_references": [
            "Indian PM Modi public address — 27 Mar 2019",
            "NASA Administrator statement — 1 Apr 2019",
            "Secure World Foundation — Global Counterspace Capabilities",
        ],
        "related_norad_ids": [43947],
    },
    {
        "id": "INCIDENT-2019-002",
        "date": "2019-11-26",
        "title": "Russia Cosmos 2542 Approaches USA-245",
        "type": "co-orbital",
        "actors": ["CIS"],
        "description": (
            "Russian inspector satellite Cosmos 2542 (launched Nov 2019) maneuvered "
            "into an orbit approaching the US National Reconnaissance Office "
            "satellite USA-245 (KH-11 class reconnaissance satellite). US Space "
            "Command publicly stated that the Russian satellite's behavior was "
            "\"unusual and disturbing\" and appeared to be stalking the NRO asset. "
            "Cosmos 2542 subsequently released a sub-satellite (Cosmos 2543) which "
            "further demonstrated inspector capabilities."
        ),
        "debris_count": 0,
        "orbit_affected": "LEO",
        "severity": "critical",
        "source_references": [
            "USSPACECOM Commander Gen. John Raymond — public statement Feb 2020",
            "Time Magazine — \"The US Military Says Russia Is Stalking a US Spy Satellite\"",
            "CSIS — Space Threat Assessment 2020",
        ],
        "related_norad_ids": [44834],
    },
    {
        "id": "INCIDENT-2020-001",
        "date": "2020-04-22",
        "title": "Iran Launches Noor-1 on IRGC Qased SLV",
        "type": "test",
        "actors": ["Iran"],
        "description": (
            "Iran's Islamic Revolutionary Guard Corps (IRGC) Aerospace Force "
            "successfully launched the Noor-1 (Light-1) military satellite into "
            "a 426 km LEO orbit using the Qased (Messenger) space launch vehicle. "
            "This was the first successful orbital launch by the IRGC (as distinct "
            "from Iran's civilian ISA). The Qased SLV is derived from the Shahab-3 "
            "ballistic missile, demonstrating Iran's ability to leverage its "
            "missile program for space access. The satellite was assessed to have "
            "limited imaging capability."
        ),
        "debris_count": 0,
        "orbit_affected": "LEO",
        "severity": "medium",
        "source_references": [
            "IRGC official announcement — Apr 2020",
            "USSPACECOM tracking confirmation",
            "CSIS — Space Threat Assessment 2021",
        ],
        "related_norad_ids": [45529],
    },
    {
        "id": "INCIDENT-2020-002",
        "date": "2020-07-15",
        "title": "Russia Cosmos 2543 Releases Sub-Satellite Near USA-245",
        "type": "co-orbital",
        "actors": ["CIS"],
        "description": (
            "Cosmos 2543 (sub-satellite of Cosmos 2542) released a small object "
            "at high relative velocity while in proximity to the US NRO satellite "
            "USA-245. USSPACECOM characterized this as a \"projectile\" release "
            "and stated it was \"consistent with an on-orbit weapon test.\" The "
            "release demonstrated Russia's capability to deploy kinetic kill "
            "vehicles from inspector satellites, representing a significant "
            "evolution of the co-orbital ASAT threat. Gen. Raymond publicly "
            "called it \"evidence of Russia's continuing efforts to develop and "
            "test space-based systems.\""
        ),
        "debris_count": 0,
        "orbit_affected": "LEO",
        "severity": "critical",
        "source_references": [
            "USSPACECOM press release — 23 Jul 2020",
            "Gen. John Raymond — CNN interview Jul 2020",
            "Secure World Foundation — Global Counterspace Capabilities (2021)",
        ],
        "related_norad_ids": [44835, 45915],
    },
    {
        "id": "INCIDENT-2021-001",
        "date": "2021-11-15",
        "title": "Russia Nudol DA-ASAT Destroys Cosmos 1408",
        "type": "DA-ASAT",
        "actors": ["CIS"],
        "description": (
            "Russia conducted a direct-ascent anti-satellite weapons test using "
            "the A-235 Nudol system, destroying the derelict Soviet-era Cosmos 1408 "
            "(ELINT satellite, launched 1982) at approximately 480 km altitude. The "
            "test generated over 1,500 pieces of trackable debris and forced the "
            "crew of the International Space Station to take shelter in their "
            "return vehicles as debris clouds passed nearby. The test was widely "
            "condemned internationally. As of 2024, much of the debris remains "
            "in orbit posing ongoing conjunction risks."
        ),
        "debris_count": 1500,
        "orbit_affected": "LEO",
        "severity": "critical",
        "source_references": [
            "US State Department statement — 15 Nov 2021",
            "USSPACECOM tracking data",
            "NASA ISS conjunction assessment — Nov 2021",
            "CSIS — Space Threat Assessment 2022",
        ],
        "related_norad_ids": [13552],
    },
    {
        "id": "INCIDENT-2022-001",
        "date": "2022-01-22",
        "title": "PRC SJ-21 Tows Dead BeiDou Satellite Out of GEO",
        "type": "co-orbital",
        "actors": ["PRC"],
        "description": (
            "PRC's Shijian-21 (SJ-21) \"space debris mitigation technology "
            "verification\" satellite grappled a defunct BeiDou-2 G2 navigation "
            "satellite and relocated it from geostationary orbit to a graveyard "
            "orbit above GEO. While presented as a debris cleanup demonstration, "
            "this was the first confirmed instance of a satellite physically "
            "towing another spacecraft in GEO. The capability has profound "
            "implications for GEO-based ASAT operations — the same technology "
            "could disable or relocate adversary GEO assets including early "
            "warning, communications, and intelligence satellites."
        ),
        "debris_count": 0,
        "orbit_affected": "GEO",
        "severity": "critical",
        "source_references": [
            "ExoAnalytic Solutions tracking data — Jan 2022",
            "CSIS — Space Threat Assessment 2023",
            "Secure World Foundation — Global Counterspace Capabilities (2023)",
        ],
        "related_norad_ids": [49258, 36590],
    },
    {
        "id": "INCIDENT-2022-002",
        "date": "2022-02-24",
        "title": "Viasat KA-SAT Cyberattack (AcidRain Wiper)",
        "type": "cyber",
        "actors": ["CIS"],
        "description": (
            "Hours before Russia's full-scale invasion of Ukraine, a cyberattack "
            "attributed to Russian military intelligence (GRU) targeted Viasat's "
            "KA-SAT network using the \"AcidRain\" wiper malware. The attack "
            "disabled tens of thousands of satellite broadband modems across Europe, "
            "disrupting Ukrainian military communications and causing collateral "
            "damage to satellite internet users across the continent, including "
            "disruption to 5,800 wind turbines in Germany. This was the most "
            "significant publicly documented cyber attack against space "
            "infrastructure and demonstrated the vulnerability of commercial "
            "satellite systems to state-sponsored cyber operations."
        ),
        "debris_count": 0,
        "orbit_affected": "GEO",
        "severity": "critical",
        "source_references": [
            "EU Council attribution statement — May 2022",
            "NSA / CISA advisory — Mar 2022",
            "Viasat incident report — Mar 2022",
            "SentinelOne AcidRain analysis",
        ],
        "related_norad_ids": [],
    },
    {
        "id": "INCIDENT-2022-003",
        "date": "2022-08-01",
        "title": "Russia Cosmos 2558 Placed Near USA-326",
        "type": "co-orbital",
        "actors": ["CIS"],
        "description": (
            "Russia launched Cosmos 2558 into an orbital plane closely matching "
            "that of the classified US satellite USA-326 (likely an NRO asset). "
            "The orbital parameters placed Cosmos 2558 in a position to observe "
            "USA-326, continuing Russia's pattern of deploying inspector satellites "
            "near sensitive US national security space systems. USSPACECOM "
            "confirmed awareness of the situation. The co-planar deployment "
            "was assessed as deliberate, enabling periodic close approaches for "
            "intelligence collection on the US asset."
        ),
        "debris_count": 0,
        "orbit_affected": "LEO",
        "severity": "high",
        "source_references": [
            "USSPACECOM tracking data",
            "CSIS — Space Threat Assessment 2023",
            "Secure World Foundation — Global Counterspace Capabilities (2023)",
        ],
        "related_norad_ids": [53328],
    },
    {
        "id": "INCIDENT-2023-001",
        "date": "2023-01-01",
        "title": "Persistent GPS Jamming — Baltic, Black Sea, Eastern Mediterranean",
        "type": "EW",
        "actors": ["CIS"],
        "description": (
            "Ongoing, large-scale GPS jamming and interference operations detected "
            "across the Baltic Sea, Black Sea, and Eastern Mediterranean regions. "
            "The jamming has been attributed to Russian electronic warfare systems, "
            "including ground-based and ship-based GPS denial capabilities. "
            "Commercial aviation has reported repeated GPS outages, with EASA and "
            "EUROCONTROL issuing multiple advisories. The jamming affects both "
            "GPS L1 and L2 frequencies and has been correlated with Russian "
            "military exercises and operations. The persistent nature represents "
            "a sustained electronic warfare campaign against GNSS infrastructure."
        ),
        "debris_count": 0,
        "orbit_affected": "MEO",
        "severity": "high",
        "source_references": [
            "EUROCONTROL Safety Advisory — 2023/2024",
            "EASA Safety Information Bulletin",
            "C4ADS — \"Above Us Only Stars\" report",
            "CSIS — Space Threat Assessment 2024",
        ],
        "related_norad_ids": [],
    },
    {
        "id": "INCIDENT-2024-001",
        "date": "2024-01-01",
        "title": "GPS Spoofing Affecting Aviation in Middle East",
        "type": "EW",
        "actors": ["CIS", "Iran"],
        "description": (
            "Widespread GPS spoofing operations affecting commercial and military "
            "aviation across the Middle East, with hotspots near Iraq, Syria, Iran, "
            "and the Eastern Mediterranean. Aircraft navigation systems have "
            "received false GPS signals causing erroneous position reporting, with "
            "some aircraft displaced by hundreds of kilometers on navigation "
            "displays. The spoofing operations are assessed to originate from "
            "multiple state actors, including Russian forces in Syria and Iranian "
            "electronic warfare systems. OPSGROUP and multiple airlines have issued "
            "warnings. This represents the most sophisticated and widespread GPS "
            "spoofing campaign publicly documented."
        ),
        "debris_count": 0,
        "orbit_affected": "MEO",
        "severity": "high",
        "source_references": [
            "OPSGROUP GPS spoofing reports — 2023/2024",
            "EASA Safety Information Bulletin — 2024",
            "University of Texas Radionavigation Lab analysis",
            "CSIS — Space Threat Assessment 2024",
        ],
        "related_norad_ids": [],
    },
]


# ---------------------------------------------------------------------------
# Incident types and actor constants
# ---------------------------------------------------------------------------

INCIDENT_TYPES = ["DA-ASAT", "co-orbital", "cyber", "collision", "EW", "test"]
ACTORS = ["PRC", "CIS", "US", "India", "Iran", "NKOR"]


# ---------------------------------------------------------------------------
# Query Functions
# ---------------------------------------------------------------------------

def get_all_incidents() -> dict:
    """Return the full incident timeline, sorted chronologically."""
    incidents = sorted(_INCIDENTS, key=lambda i: i["date"])
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total_incidents": len(incidents),
        "incidents": incidents,
    }


def get_incidents_by_type(incident_type: str) -> dict:
    """Filter incidents by type (DA-ASAT, co-orbital, cyber, collision, EW, test)."""
    t = incident_type.strip()
    # Case-insensitive match
    incidents = [
        i for i in _INCIDENTS
        if i["type"].lower() == t.lower()
    ]
    incidents.sort(key=lambda i: i["date"])
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "filter": {"type": t},
        "total_incidents": len(incidents),
        "incidents": incidents,
    }


def get_incidents_by_actor(actor: str) -> dict:
    """Filter incidents by actor/nation (PRC, CIS, US, India, Iran)."""
    a = actor.strip().upper()
    # Handle common aliases
    alias_map = {
        "RUSSIA": "CIS",
        "CHINA": "PRC",
        "DPRK": "NKOR",
        "NORTHKOREA": "NKOR",
    }
    a = alias_map.get(a, a)

    incidents = [
        i for i in _INCIDENTS
        if a in [x.upper() for x in i["actors"]]
    ]
    incidents.sort(key=lambda i: i["date"])
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "filter": {"actor": a},
        "total_incidents": len(incidents),
        "incidents": incidents,
    }


def get_incidents_by_year(year: int) -> dict:
    """Filter incidents by year."""
    incidents = [
        i for i in _INCIDENTS
        if i["date"].startswith(str(year))
    ]
    incidents.sort(key=lambda i: i["date"])
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "filter": {"year": year},
        "total_incidents": len(incidents),
        "incidents": incidents,
    }


def get_incident_stats() -> dict:
    """Summary statistics across all incidents."""
    total = len(_INCIDENTS)

    # By type
    by_type = {}  # type: Dict[str, int]
    for i in _INCIDENTS:
        t = i["type"]
        by_type[t] = by_type.get(t, 0) + 1

    # By actor
    by_actor = {}  # type: Dict[str, int]
    for i in _INCIDENTS:
        for a in i["actors"]:
            by_actor[a] = by_actor.get(a, 0) + 1

    # By decade
    by_decade = {}  # type: Dict[str, int]
    for i in _INCIDENTS:
        year = int(i["date"][:4])
        decade = f"{(year // 10) * 10}s"
        by_decade[decade] = by_decade.get(decade, 0) + 1

    # By severity
    by_severity = {}  # type: Dict[str, int]
    for i in _INCIDENTS:
        s = i["severity"]
        by_severity[s] = by_severity.get(s, 0) + 1

    # By orbit
    by_orbit = {}  # type: Dict[str, int]
    for i in _INCIDENTS:
        o = i["orbit_affected"]
        by_orbit[o] = by_orbit.get(o, 0) + 1

    # Total debris generated
    total_debris = sum(i.get("debris_count", 0) for i in _INCIDENTS)

    # Most active actor
    most_active = max(by_actor.items(), key=lambda x: x[1]) if by_actor else ("N/A", 0)

    # Most common type
    most_common_type = max(by_type.items(), key=lambda x: x[1]) if by_type else ("N/A", 0)

    # Year with most incidents
    by_year = {}  # type: Dict[str, int]
    for i in _INCIDENTS:
        y = i["date"][:4]
        by_year[y] = by_year.get(y, 0) + 1
    busiest_year = max(by_year.items(), key=lambda x: x[1]) if by_year else ("N/A", 0)

    # Critical incidents
    critical_count = sum(1 for i in _INCIDENTS if i["severity"] == "critical")

    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total_incidents": total,
        "total_debris_generated": total_debris,
        "critical_incidents": critical_count,
        "most_active_actor": {"actor": most_active[0], "incident_count": most_active[1]},
        "most_common_type": {"type": most_common_type[0], "count": most_common_type[1]},
        "busiest_year": {"year": busiest_year[0], "count": busiest_year[1]},
        "by_type": by_type,
        "by_actor": by_actor,
        "by_decade": by_decade,
        "by_severity": by_severity,
        "by_orbit_affected": by_orbit,
        "by_year": by_year,
        "trend_assessment": (
            "Space security incidents are accelerating in frequency and sophistication. "
            "Co-orbital/RPO activities have become the dominant threat vector since 2019, "
            "replacing direct-ascent ASAT tests as nations seek to demonstrate capabilities "
            "without generating debris. Electronic warfare (GPS jamming/spoofing) has "
            "emerged as a persistent, daily threat since 2023. The 2022 Viasat cyberattack "
            "demonstrated that space ground segments are vulnerable to state-level cyber "
            "operations during armed conflict."
        ),
    }
