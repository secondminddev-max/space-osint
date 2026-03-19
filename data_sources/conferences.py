"""
Global Space Conference & Events Database
Comprehensive structured database of recurring space conferences, forums, exercises,
and report releases relevant to FVEY space domain awareness.

Live data integration:
- Spaceflight News API events endpoint

Structured database compiled from:
- Conference organization websites
- IAF/IAC event calendars
- US Space Foundation events
- AIAA conference schedules
- Think tank publication schedules
- NATO/DoD exercise calendars

Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

import httpx

# ---------------------------------------------------------------------------
# Relevance and frequency constants
# ---------------------------------------------------------------------------
RELEVANCE_HIGH = "high"
RELEVANCE_MEDIUM = "medium"
RELEVANCE_LOW = "low"

FREQ_ANNUAL = "annual"
FREQ_BIENNIAL = "biennial"
FREQ_QUARTERLY = "quarterly"
FREQ_ONE_TIME = "one-time"
FREQ_ONGOING = "ongoing"

# ---------------------------------------------------------------------------
# Government / Military Conferences & Events
# ---------------------------------------------------------------------------

_GOV_MILITARY: List[dict] = [
    {
        "name": "UNGA First Committee (Disarmament and International Security)",
        "organization": "United Nations General Assembly",
        "location": "New York, USA",
        "date_start": "October",
        "date_end": "November",
        "frequency": FREQ_ANNUAL,
        "description": (
            "UN General Assembly First Committee addresses disarmament, global challenges "
            "and threats to peace. Includes resolutions on Prevention of an Arms Race in "
            "Outer Space (PAROS), transparency and confidence-building measures in space, "
            "and no first placement of weapons in outer space. Key forum for space norms "
            "development and voting alignment analysis."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "https://www.un.org/disarmament/institutions/disarmament-commission/",
        "next_occurrence": "2026-10",
        "topics": [
            "PAROS", "space arms control", "TCBMs",
            "responsible behavior norms", "debris mitigation"
        ],
    },
    {
        "name": "UN COPUOS (Committee on the Peaceful Uses of Outer Space)",
        "organization": "United Nations",
        "location": "Vienna, Austria",
        "date_start": "June",
        "date_end": "June",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Principal UN body for international cooperation in space. Annual session in "
            "Vienna plus Legal and Scientific/Technical subcommittees. Addresses space "
            "debris, space traffic management, Long-Term Sustainability guidelines, and "
            "space resource utilization governance. Key venue for monitoring PRC/Russia "
            "positions on space governance."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "https://www.unoosa.org/oosa/en/ourwork/copuos/index.html",
        "next_occurrence": "2026-06",
        "topics": [
            "space debris", "LTS guidelines", "space traffic management",
            "space resource utilization", "space sustainability"
        ],
    },
    {
        "name": "UN Conference on Disarmament (CD)",
        "organization": "United Nations",
        "location": "Geneva, Switzerland",
        "date_start": "January",
        "date_end": "March",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Multilateral disarmament negotiating forum. PAROS is a standing agenda item "
            "but the CD has been deadlocked for decades. Russia and China push draft PPWT "
            "(Prevention of Placement of Weapons in Outer Space Treaty); FVEY nations "
            "generally oppose as unverifiable. Key venue for monitoring adversary arms "
            "control positioning and narrative development."
        ),
        "relevance_to_fvey": RELEVANCE_MEDIUM,
        "url": "https://www.unog.ch/disarmament",
        "next_occurrence": "2027-01",
        "topics": [
            "PAROS", "PPWT draft treaty", "space arms control",
            "verification", "space weapons definitions"
        ],
    },
    {
        "name": "Schriever Wargame",
        "organization": "US Space Command / USSF",
        "location": "Various (typically Colorado Springs, USA)",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Senior-level space wargame examining space-enabled operations and "
            "counterspace threats in a multi-domain conflict scenario. Includes FVEY and "
            "allied nation participation. Classified but outcomes inform space strategy, "
            "doctrine, and capability development. Results typically briefed at unclassified "
            "level at subsequent conferences."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "",
        "next_occurrence": "2026",
        "topics": [
            "space wargaming", "counterspace operations", "FVEY space cooperation",
            "escalation dynamics", "space deterrence"
        ],
    },
    {
        "name": "Global Sentinel Exercise",
        "organization": "US Space Command",
        "location": "Vandenberg SFB, USA (varies)",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Multilateral space domain awareness exercise involving FVEY and partner "
            "nations. Focuses on sharing SSA data, combined space operations, and "
            "interoperability. Demonstrates allied commitment to cooperative space "
            "surveillance. Participants include FVEY plus select allies."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "",
        "next_occurrence": "2026",
        "topics": [
            "SSA sharing", "multinational space ops", "interoperability",
            "combined space C2", "data fusion"
        ],
    },
    {
        "name": "Space Symposium",
        "organization": "Space Foundation",
        "location": "Colorado Springs, CO, USA",
        "date_start": "April",
        "date_end": "April",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Largest annual gathering of the global space community. Attracts military, "
            "intelligence, civil, and commercial space leaders. Key venue for USSF/USSPACECOM "
            "senior leader speeches, policy announcements, and industry engagement. Typically "
            "20,000+ attendees. Side meetings and classified sessions. Critical for FVEY "
            "space community networking and intelligence collection."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "https://www.spacesymposium.org/",
        "next_occurrence": "2026-04",
        "topics": [
            "space policy", "USSF priorities", "commercial space", "allied space ops",
            "counterspace threats", "acquisition", "space industry"
        ],
    },
    {
        "name": "AMOS Conference (Advanced Maui Optical and Space Surveillance Technologies)",
        "organization": "Maui Economic Development Board",
        "location": "Maui, HI, USA",
        "date_start": "September",
        "date_end": "September",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Premier technical conference for space surveillance technology. Presentations "
            "on SSA sensors, space object characterization, orbit determination, astrodynamics, "
            "and space environment. Unique blend of military, academic, and industry SSA "
            "practitioners. Technical papers often reveal capability developments."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "https://amostech.com/",
        "next_occurrence": "2026-09",
        "topics": [
            "SSA technology", "optical tracking", "radar systems", "orbit determination",
            "space debris", "satellite characterization", "astrodynamics"
        ],
    },
    {
        "name": "Space & Missile Defense Symposium",
        "organization": "AUSA / SMDC",
        "location": "Huntsville, AL, USA",
        "date_start": "August",
        "date_end": "August",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Annual symposium focused on space and missile defense capabilities, technology, "
            "and policy. Hosted near Redstone Arsenal. Features MDA, SMDC, and USSF senior "
            "leaders. Key for monitoring US missile defense/space defense integration and "
            "counterspace capability development."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "https://smdsymposium.org/",
        "next_occurrence": "2026-08",
        "topics": [
            "missile defense", "space defense", "directed energy",
            "hypersonic defense", "ASAT defense", "integrated deterrence"
        ],
    },
    {
        "name": "DSEI (Defence and Security Equipment International)",
        "organization": "Clarion Events",
        "location": "London, UK",
        "date_start": "September",
        "date_end": "September",
        "frequency": FREQ_BIENNIAL,
        "description": (
            "Major international defence exhibition held biennially in London. Includes "
            "significant space and satellite zone with military SATCOM, ISR, and SSA "
            "exhibits. Key venue for European/UK space defence industry. Government "
            "delegations from 60+ nations attend."
        ),
        "relevance_to_fvey": RELEVANCE_MEDIUM,
        "url": "https://www.dsei.co.uk/",
        "next_occurrence": "2027-09",
        "topics": [
            "defence equipment", "space systems", "SATCOM",
            "ISR", "electronic warfare", "space resilience"
        ],
    },
    {
        "name": "NATO Space Seminar",
        "organization": "NATO / Allied Command Transformation",
        "location": "Various NATO locations",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Annual NATO seminar on space domain operations, policy, and interoperability. "
            "Addresses NATO space policy implementation, allied space contributions, and "
            "space support to NATO operations. Increasingly focused on counterspace threats "
            "and collective space defense."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "",
        "next_occurrence": "2026",
        "topics": [
            "NATO space policy", "allied space ops", "counterspace defense",
            "space interoperability", "collective defense in space"
        ],
    },
    {
        "name": "ASPI National Space Conference",
        "organization": "Australian Strategic Policy Institute",
        "location": "Canberra, Australia",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Australian Strategic Policy Institute annual space conference bringing together "
            "Australian Defence Force, Five Eyes partners, and regional allies to discuss "
            "space domain awareness, counterspace threats, and Australian space strategy. "
            "Key venue for Indo-Pacific space security discourse."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "https://www.aspi.org.au/",
        "next_occurrence": "2026",
        "topics": [
            "Australian space strategy", "Indo-Pacific space security", "FVEY SSA",
            "counterspace threats", "AUKUS space cooperation"
        ],
    },
    {
        "name": "Secure World Foundation Summit",
        "organization": "Secure World Foundation",
        "location": "Washington DC area, USA",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Annual summit by the leading space sustainability think tank. Addresses space "
            "security, sustainability, governance, and norms of behavior. Attracts government, "
            "military, academic, and industry leaders. SWF produces the authoritative annual "
            "Global Counterspace Capabilities report."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "https://swfound.org/",
        "next_occurrence": "2026",
        "topics": [
            "space sustainability", "norms of behavior", "counterspace",
            "space governance", "debris mitigation", "space traffic management"
        ],
    },
]

# ---------------------------------------------------------------------------
# Industry / Commercial Conferences
# ---------------------------------------------------------------------------

_INDUSTRY_COMMERCIAL: List[dict] = [
    {
        "name": "IAC (International Astronautical Congress)",
        "organization": "International Astronautical Federation (IAF)",
        "location": "Rotating city (annually)",
        "date_start": "September-October",
        "date_end": "September-October",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Largest global space conference with 5,000-10,000+ attendees from 80+ nations. "
            "Combines technical sessions, policy discussions, and exhibitions. Key venue for "
            "PRC/Russia space program announcements and papers. FVEY intelligence agencies "
            "monitor presentations for technology development indicators. Host city rotates "
            "globally."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "https://www.iafastro.org/",
        "next_occurrence": "2026-10",
        "topics": [
            "astronautics", "space exploration", "satellite technology",
            "launch vehicles", "space policy", "international cooperation"
        ],
    },
    {
        "name": "SATELLITE Conference & Exhibition",
        "organization": "Via Satellite / Access Intelligence",
        "location": "Washington DC, USA",
        "date_start": "March",
        "date_end": "March",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Major commercial satellite industry conference in Washington DC. Covers SATCOM, "
            "remote sensing, broadband, and launch services. Important for monitoring "
            "commercial space developments with military relevance. Government/military "
            "track included."
        ),
        "relevance_to_fvey": RELEVANCE_MEDIUM,
        "url": "https://www.satshow.com/",
        "next_occurrence": "2027-03",
        "topics": [
            "satellite communications", "broadband", "remote sensing",
            "launch services", "ground systems", "commercial space"
        ],
    },
    {
        "name": "SmallSat Conference",
        "organization": "AIAA / Utah State University",
        "location": "Logan, UT, USA",
        "date_start": "August",
        "date_end": "August",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Premier conference on small satellite technology and missions. Technical papers "
            "on CubeSats, microsats, and small satellite constellations. Increasingly relevant "
            "as military architectures shift to proliferated small satellites (SDA/PWSA). "
            "Academic and commercial focus with growing defense participation."
        ),
        "relevance_to_fvey": RELEVANCE_MEDIUM,
        "url": "https://smallsat.org/",
        "next_occurrence": "2026-08",
        "topics": [
            "small satellites", "CubeSats", "constellation design",
            "miniaturized payloads", "rideshare launch", "responsive space"
        ],
    },
    {
        "name": "Paris Air Show (Salon du Bourget)",
        "organization": "GIFAS / SIAE",
        "location": "Paris-Le Bourget, France",
        "date_start": "June",
        "date_end": "June",
        "frequency": FREQ_BIENNIAL,
        "description": (
            "World's largest aerospace exhibition (odd years, alternating with Farnborough). "
            "Significant space pavilion featuring ESA, CNES, Arianespace, and global space "
            "companies. Major contract announcements and program reveals. Key for European "
            "space industry intelligence."
        ),
        "relevance_to_fvey": RELEVANCE_MEDIUM,
        "url": "https://www.siae.fr/",
        "next_occurrence": "2027-06",
        "topics": [
            "aerospace industry", "launch vehicles", "satellite systems",
            "space exploration", "defence aerospace"
        ],
    },
    {
        "name": "Farnborough International Airshow",
        "organization": "Farnborough International",
        "location": "Farnborough, UK",
        "date_start": "July",
        "date_end": "July",
        "frequency": FREQ_BIENNIAL,
        "description": (
            "Major aerospace exhibition (even years, alternating with Paris). Significant "
            "space content including UK space industry, ESA programs, and international "
            "exhibitors. Defence space zone features military SATCOM, ISR, and SSA. "
            "UK MOD space announcements often timed to Farnborough."
        ),
        "relevance_to_fvey": RELEVANCE_MEDIUM,
        "url": "https://www.farnboroughairshow.com/",
        "next_occurrence": "2026-07",
        "topics": [
            "aerospace industry", "UK space", "ESA programs",
            "defence space", "satellite manufacturing"
        ],
    },
    {
        "name": "NewSpace Europe",
        "organization": "NewSpace Europe / Luxembourg",
        "location": "Luxembourg",
        "date_start": "November",
        "date_end": "November",
        "frequency": FREQ_ANNUAL,
        "description": (
            "European commercial space conference focusing on the emerging space economy. "
            "Covers space resources, commercial ISR, launch services, and in-orbit servicing. "
            "Luxembourg position as a space resources hub makes this increasingly relevant "
            "for space governance discussions."
        ),
        "relevance_to_fvey": RELEVANCE_LOW,
        "url": "https://newspace-europe.lu/",
        "next_occurrence": "2026-11",
        "topics": [
            "commercial space", "space resources", "NewSpace economy",
            "in-orbit servicing", "European space"
        ],
    },
    {
        "name": "SpaceCom",
        "organization": "SpaceCom",
        "location": "Orlando, FL, USA (varies)",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Conference connecting space technology with terrestrial industries. Covers "
            "space-enabled solutions for agriculture, energy, maritime, and defense. "
            "Growing military/government space track. Focus on practical applications "
            "of space data and services."
        ),
        "relevance_to_fvey": RELEVANCE_LOW,
        "url": "https://spacecomexpo.com/",
        "next_occurrence": "2026",
        "topics": [
            "space applications", "space data", "remote sensing applications",
            "SATCOM services", "PNT applications"
        ],
    },
    {
        "name": "CisLunar Security Conference",
        "organization": "AFRL / Various",
        "location": "USA (varies)",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Emerging conference focused specifically on security challenges in the cislunar "
            "domain (Earth-Moon space). Covers SSA beyond GEO, cislunar traffic management, "
            "lunar operations security, and counterspace in deep space. Gaining importance "
            "as lunar programs accelerate."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "",
        "next_occurrence": "2026",
        "topics": [
            "cislunar security", "deep space SSA", "lunar operations",
            "cislunar traffic management", "space domain beyond GEO"
        ],
    },
    {
        "name": "Indo-Pacific Space & Earth Conference",
        "organization": "Various (rotating host)",
        "location": "Indo-Pacific region (rotating)",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Regional forum on space cooperation in the Indo-Pacific. Covers earth "
            "observation, disaster response, satellite communications, and increasingly "
            "space security. Includes FVEY, Japan, South Korea, India, and ASEAN "
            "participants. Important for building regional space security partnerships."
        ),
        "relevance_to_fvey": RELEVANCE_MEDIUM,
        "url": "",
        "next_occurrence": "2026",
        "topics": [
            "Indo-Pacific space", "regional cooperation", "earth observation",
            "disaster response", "space security"
        ],
    },
]

# ---------------------------------------------------------------------------
# Academic / Think Tank Events & Report Releases
# ---------------------------------------------------------------------------

_ACADEMIC_THINKTANK: List[dict] = [
    {
        "name": "CSIS Space Threat Assessment (Annual Report Release)",
        "organization": "Center for Strategic and International Studies (CSIS)",
        "location": "Washington DC, USA (publication + launch event)",
        "date_start": "April",
        "date_end": "April",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Annual publication by CSIS Aerospace Security Project assessing counterspace "
            "threats from PRC, Russia, DPRK, Iran, and others. The most comprehensive "
            "unclassified annual assessment of space threats. Launch event includes expert "
            "panel discussion. Essential reading for FVEY space intelligence analysts."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "https://www.csis.org/programs/aerospace-security-project",
        "next_occurrence": "2026-04",
        "topics": [
            "counterspace threats", "ASAT", "electronic warfare",
            "cyber threats to space", "adversary space programs"
        ],
    },
    {
        "name": "SWF Global Counterspace Capabilities (Annual Report Release)",
        "organization": "Secure World Foundation",
        "location": "Washington DC, USA / Online (publication)",
        "date_start": "April",
        "date_end": "April",
        "frequency": FREQ_ANNUAL,
        "description": (
            "Comprehensive annual open-source assessment of counterspace capabilities "
            "worldwide. Covers DA-ASAT, co-orbital, DEW, EW, and cyber capabilities for "
            "PRC, Russia, US, India, and others. The authoritative unclassified reference "
            "on global counterspace. Typically released alongside Space Symposium."
        ),
        "relevance_to_fvey": RELEVANCE_HIGH,
        "url": "https://swfound.org/counterspace/",
        "next_occurrence": "2026-04",
        "topics": [
            "counterspace capabilities", "ASAT systems", "space weapons",
            "directed energy", "electronic warfare against space"
        ],
    },
    {
        "name": "Chatham House Space Security Conference",
        "organization": "Royal Institute of International Affairs (Chatham House)",
        "location": "London, UK",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_ANNUAL,
        "description": (
            "UK-based space security conference bringing together European, US, and allied "
            "experts on space governance, norms, and security. Chatham House Rule enables "
            "frank discussion. Important for European/UK space security policy perspectives "
            "and NATO space policy development."
        ),
        "relevance_to_fvey": RELEVANCE_MEDIUM,
        "url": "https://www.chathamhouse.org/",
        "next_occurrence": "2026",
        "topics": [
            "space security", "space governance", "norms of behavior",
            "European space policy", "UK space strategy"
        ],
    },
    {
        "name": "RAND Space Workshops",
        "organization": "RAND Corporation",
        "location": "Various (USA, typically Washington DC or Santa Monica)",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_QUARTERLY,
        "description": (
            "RAND Corporation conducts periodic workshops and publishes research on space "
            "security, deterrence, escalation dynamics, and counterspace operations. RAND "
            "studies significantly influence US space policy and strategy. Reports are "
            "frequently cited in DoD space documents."
        ),
        "relevance_to_fvey": RELEVANCE_MEDIUM,
        "url": "https://www.rand.org/topics/space-policy.html",
        "next_occurrence": "2026",
        "topics": [
            "space deterrence", "escalation dynamics", "counterspace strategy",
            "space architecture analysis", "cost-benefit of space systems"
        ],
    },
    {
        "name": "MIT Space Policy Seminar Series",
        "organization": "Massachusetts Institute of Technology",
        "location": "Cambridge, MA, USA / Online",
        "date_start": "Academic year (Sep-May)",
        "date_end": "Academic year",
        "frequency": FREQ_ONGOING,
        "description": (
            "MIT hosts ongoing seminars on space policy, technology, and security through "
            "the Department of Aeronautics and Astronautics and the Security Studies Program. "
            "Features leading academics, government officials, and industry experts. Seminar "
            "recordings often publicly available."
        ),
        "relevance_to_fvey": RELEVANCE_LOW,
        "url": "https://aeroastro.mit.edu/",
        "next_occurrence": "2026-09",
        "topics": [
            "space policy", "space technology", "space security research",
            "orbital mechanics", "space systems engineering"
        ],
    },
    {
        "name": "AIAA ASCEND / Space Conferences",
        "organization": "American Institute of Aeronautics and Astronautics",
        "location": "USA (varies)",
        "date_start": "Variable",
        "date_end": "Variable",
        "frequency": FREQ_ANNUAL,
        "description": (
            "AIAA's flagship space conference (formerly AIAA SPACE, now part of ASCEND). "
            "Covers space technology, exploration, and commercial space. Technical papers "
            "on satellite technology, launch vehicles, space operations, and space domain "
            "awareness. Important for monitoring technology development trends."
        ),
        "relevance_to_fvey": RELEVANCE_MEDIUM,
        "url": "https://www.aiaa.org/ascend",
        "next_occurrence": "2026",
        "topics": [
            "space technology", "space exploration", "commercial space",
            "space operations", "in-space servicing"
        ],
    },
]

# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

_ALL_CONFERENCES: List[dict] = _GOV_MILITARY + _INDUSTRY_COMMERCIAL + _ACADEMIC_THINKTANK


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_all_conferences() -> dict:
    """Return all conferences/events in the database."""
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total_events": len(_ALL_CONFERENCES),
        "categories": {
            "government_military": len(_GOV_MILITARY),
            "industry_commercial": len(_INDUSTRY_COMMERCIAL),
            "academic_thinktank": len(_ACADEMIC_THINKTANK),
        },
        "events": _ALL_CONFERENCES,
    }


def get_upcoming_conferences() -> dict:
    """Return conferences expected in the next 12 months, sorted by estimated date."""
    now = datetime.now(timezone.utc)
    current_year = now.year
    current_month = now.month

    upcoming: List[dict] = []
    for conf in _ALL_CONFERENCES:
        next_occ = conf.get("next_occurrence", "")
        if not next_occ:
            continue

        # Parse next_occurrence (formats: "2026-04", "2026", "2027-09")
        try:
            parts = next_occ.split("-")
            year = int(parts[0])
            month = int(parts[1]) if len(parts) > 1 else 6  # default to mid-year

            # Check if within next 12 months
            event_date = datetime(year, month, 1, tzinfo=timezone.utc)
            months_until = (event_date.year - now.year) * 12 + (event_date.month - now.month)

            if 0 <= months_until <= 12:
                entry = dict(conf)
                entry["estimated_date"] = f"{year}-{month:02d}"
                entry["months_until"] = months_until
                upcoming.append(entry)
        except (ValueError, IndexError):
            continue

    upcoming.sort(key=lambda e: e.get("estimated_date", "9999"))

    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": now.isoformat(),
        "window": "next 12 months",
        "total_upcoming": len(upcoming),
        "events": upcoming,
    }


def get_conferences_by_relevance(level: str) -> dict:
    """Filter conferences by FVEY relevance level (high/medium/low)."""
    lvl = level.strip().lower()
    filtered = [c for c in _ALL_CONFERENCES if c["relevance_to_fvey"] == lvl]
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "filter": {"relevance": lvl},
        "total_events": len(filtered),
        "events": filtered,
    }


async def fetch_live_events(client: httpx.AsyncClient) -> dict:
    """Fetch live events from Spaceflight News API."""
    url = "https://api.spaceflightnewsapi.net/v4/events/?limit=50"
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        events = data.get("results", [])
        return {
            "classification": "UNCLASSIFIED // OSINT",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "source": "Spaceflight News API",
            "total_events": len(events),
            "events": events,
        }
    except httpx.HTTPStatusError as exc:
        return {
            "source": "Spaceflight News API",
            "error": f"HTTP {exc.response.status_code}",
            "events": [],
        }
    except Exception as exc:
        return {
            "source": "Spaceflight News API",
            "error": str(exc),
            "events": [],
        }


def get_conference_calendar() -> dict:
    """Return a month-by-month calendar view of conferences.

    Groups events by their approximate month of occurrence.
    """
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    month_map: Dict[str, str] = {}
    for i, name in enumerate(month_names, 1):
        month_map[name.lower()] = f"{i:02d}"
        month_map[name[:3].lower()] = f"{i:02d}"

    calendar: Dict[str, List[dict]] = {f"{i:02d}": [] for i in range(1, 13)}
    unscheduled: List[dict] = []

    for conf in _ALL_CONFERENCES:
        date_start = conf.get("date_start", "")
        placed = False

        # Try to extract month from date_start
        for token in date_start.replace("-", " ").replace("/", " ").split():
            key = token.strip().lower()
            if key in month_map:
                calendar[month_map[key]].append({
                    "name": conf["name"],
                    "organization": conf["organization"],
                    "location": conf["location"],
                    "frequency": conf["frequency"],
                    "relevance_to_fvey": conf["relevance_to_fvey"],
                })
                placed = True
                break

        # Try next_occurrence if date_start didn't work
        if not placed:
            next_occ = conf.get("next_occurrence", "")
            try:
                parts = next_occ.split("-")
                if len(parts) >= 2:
                    month_num = f"{int(parts[1]):02d}"
                    calendar[month_num].append({
                        "name": conf["name"],
                        "organization": conf["organization"],
                        "location": conf["location"],
                        "frequency": conf["frequency"],
                        "relevance_to_fvey": conf["relevance_to_fvey"],
                    })
                    placed = True
            except (ValueError, IndexError):
                pass

        if not placed:
            unscheduled.append({
                "name": conf["name"],
                "organization": conf["organization"],
                "frequency": conf["frequency"],
                "relevance_to_fvey": conf["relevance_to_fvey"],
            })

    # Convert month numbers to names for readability
    named_calendar: Dict[str, List[dict]] = {}
    for i in range(1, 13):
        key = f"{i:02d}"
        month_label = f"{month_names[i-1]}"
        if calendar[key]:
            named_calendar[month_label] = calendar[key]

    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total_events": len(_ALL_CONFERENCES),
        "calendar": named_calendar,
        "variable_schedule": unscheduled,
    }
