"""
Ground Station Architecture Analysis Module
Detailed analysis of space ground segment architectures for PRC, Russia, and FVEY.
Goes beyond individual station listings to model network topology, communication links,
coverage areas, dependencies, and assessed vulnerabilities.

Sources:
- CSIS Aerospace Security Project
- Secure World Foundation reports
- DIA "Challenges to Security in Space" (2022)
- NASIC assessments (unclassified)
- Academic publications (IAC, AMOS, AIAA)
- Commercial satellite imagery analysis
- ESA/NASA ground network public documentation
- Desmond Ball (ANU) publications on Pine Gap
- Pavel Podvig (Russian Nuclear Forces Project)
- Bart Hendrickx (The Space Review)

Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# PRC Ground Architecture
# ---------------------------------------------------------------------------

def get_prc_architecture() -> dict:
    """Detailed PRC space ground segment architecture analysis."""
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "nation": "PRC",
        "overview": (
            "The PRC operates one of the most capable and rapidly expanding space ground "
            "segments globally. The architecture is centrally controlled through Xi'an "
            "Satellite Control Centre (XSCC) with distributed stations providing global "
            "TT&C coverage. The ground segment supports military (PLA), civilian (CNSA/CAS), "
            "and commercial operations with extensive dual-use overlap. The network has been "
            "significantly expanded since 2010 with overseas stations, Yuan Wang tracking "
            "ships, and the Tianlian data relay constellation."
        ),
        "ttc_network": {
            "description": (
                "Telemetry, Tracking and Command network organized in a hub-and-spoke "
                "topology centered on XSCC in Xi'an, Shaanxi province. Regional stations "
                "provide geographic coverage while XSCC coordinates operations."
            ),
            "hub": {
                "name": "Xi'an Satellite Control Centre (XSCC)",
                "role": (
                    "Primary C2 hub for all PRC satellite operations. Houses mission control "
                    "rooms for military, civilian, and human spaceflight operations. The "
                    "Beijing Aerospace Control Centre (BACC) coordinates human spaceflight "
                    "and deep space missions. XSCC manages the entire distributed TT&C "
                    "network including scheduling, commanding, and data routing."
                ),
                "coordinates": {"lat": 34.26, "lng": 108.94},
            },
            "regional_stations": [
                {
                    "name": "Kashgar (Kashi) TT&C Station",
                    "role": "Western coverage — Central/South Asia satellite passes",
                    "coordinates": {"lat": 39.50, "lng": 75.98},
                    "coverage": "Satellites visible from western China, covering South/Central Asia",
                },
                {
                    "name": "Sanya TT&C Station (Hainan)",
                    "role": "Southern coverage — GEO operations, South China Sea",
                    "coordinates": {"lat": 18.31, "lng": 109.60},
                    "coverage": "Low-latitude and GEO satellite coverage, launch tracking from Wenchang",
                },
                {
                    "name": "Weinan TT&C Station",
                    "role": "Central support near XSCC hub",
                    "coordinates": {"lat": 34.50, "lng": 109.50},
                    "coverage": "Overhead passes, routine LEO TT&C",
                },
                {
                    "name": "Miyun Ground Station (Beijing)",
                    "role": "Earth observation data downlink, CAS remote sensing",
                    "coordinates": {"lat": 40.56, "lng": 116.87},
                    "coverage": "LEO EO satellite data reception, shared military/civilian",
                },
                {
                    "name": "Kunming TT&C Station",
                    "role": "Southwestern coverage, BeiDou support",
                    "coordinates": {"lat": 25.03, "lng": 102.80},
                    "coverage": "Southern orbital passes, BeiDou constellation management",
                },
                {
                    "name": "Changchun Observatory",
                    "role": "Optical space surveillance and satellite laser ranging",
                    "coordinates": {"lat": 43.79, "lng": 125.44},
                    "coverage": "Northeastern SSA, debris tracking, SLR",
                },
            ],
            "overseas_stations": [
                {
                    "name": "Kiribati Ground Station (suspected, South Pacific)",
                    "role": "Pacific Ocean coverage for launch tracking and satellite passes",
                    "status": "reported/suspected",
                    "source": "OSINT reporting; Pacific island media",
                },
                {
                    "name": "Namibia TT&C Station (Swakopmund)",
                    "role": "Southern hemisphere and Atlantic Ocean coverage",
                    "status": "active",
                    "source": "CDSN documentation; CNSA cooperation agreements",
                },
                {
                    "name": "Pakistan TT&C Station (reported)",
                    "role": "Indian Ocean region coverage, BeiDou support",
                    "status": "reported",
                    "source": "Pakistan-China space cooperation agreements",
                },
                {
                    "name": "Argentina Deep Space Station (Neuquen)",
                    "role": "Southern hemisphere deep space coverage, part of CDSN",
                    "status": "active",
                    "coordinates": {"lat": -38.19, "lng": -70.15},
                    "source": "CONAE-CNSA agreement; commercial imagery; dual-use concerns raised by US",
                },
            ],
        },
        "yuan_wang_fleet": {
            "description": (
                "Fleet of approximately 7 operational space tracking ships providing mobile "
                "TT&C coverage over oceans where no ground stations exist. Critical for "
                "launch telemetry, orbital injection confirmation, and satellite commanding "
                "during ocean overflights."
            ),
            "ships": [
                "Yuan Wang 3", "Yuan Wang 5", "Yuan Wang 6", "Yuan Wang 7",
            ],
            "typical_patrol_areas": [
                "South Pacific (Kiribati/Fiji region) — launch support",
                "Indian Ocean — BeiDou/GEO satellite support",
                "South Atlantic — occasional deep space support",
                "Western Pacific — launch tracking corridor",
            ],
            "assessed_secondary_role": (
                "Yuan Wang ships are assessed to also conduct SIGINT collection during "
                "deployments, monitoring naval communications and radar emissions in patrol "
                "areas. Ship movements tracked via AIS (MarineTraffic) and OSINT."
            ),
        },
        "beidou_ground_control": {
            "description": (
                "BeiDou-3 Ground Control Segment comprises Master Control Stations (MCS), "
                "Upload Stations (ULS), and Monitor Stations (MS) distributed across China "
                "and partner nations. The ground segment generates navigation messages, "
                "monitors constellation health, and uploads ephemeris data."
            ),
            "master_control": "Beijing (primary) with backup at Xi'an",
            "monitor_stations": (
                "30+ stations across China plus overseas stations in Pakistan, Thailand, "
                "Malaysia, and other BRI partner nations. Provides global monitoring coverage "
                "for BeiDou-3 global service."
            ),
            "upload_stations": "Multiple stations across China for navigation message upload",
        },
        "tianlian_relay": {
            "description": (
                "Tianlian (Sky Link) data relay satellite constellation in GEO provides "
                "near-continuous communication with LEO satellites and crewed spacecraft. "
                "Functions similar to NASA's TDRS system. Enables real-time data relay "
                "without requiring ground station overflight."
            ),
            "satellites": [
                "Tianlian-1 series (4 satellites, GEO)",
                "Tianlian-2 series (2+ satellites, GEO, enhanced capacity)",
            ],
            "coverage": (
                "Near-global LEO coverage through GEO relay. Enables Tiangong station to "
                "maintain near-continuous communication with ground. Also supports real-time "
                "Yaogan ISR data downlink, dramatically reducing intelligence latency."
            ),
            "military_significance": (
                "Tianlian relay enables near-real-time ISR data from Yaogan constellation "
                "to ground processing centres without waiting for direct station overflight. "
                "This significantly reduces the sensor-to-shooter timeline for PLA operations."
            ),
        },
        "deep_space_network": {
            "description": (
                "Chinese Deep Space Network (CDSN) supports lunar (Chang'e) and planetary "
                "(Tianwen) missions. Three-station baseline provides near-continuous deep "
                "space coverage."
            ),
            "stations": [
                {
                    "name": "Jiamusi Deep Space Station",
                    "coordinates": {"lat": 46.50, "lng": 130.32},
                    "antennas": "66m and 35m dishes",
                    "role": "Eastern hemisphere deep space tracking",
                },
                {
                    "name": "Kashi (Kashgar) Deep Space Station",
                    "coordinates": {"lat": 39.51, "lng": 76.03},
                    "antennas": "35m dish",
                    "role": "Western coverage, Central Asian baseline",
                },
                {
                    "name": "Neuquen Deep Space Station (Argentina)",
                    "coordinates": {"lat": -38.19, "lng": -70.15},
                    "antennas": "35m dish",
                    "role": "Southern hemisphere, Americas coverage",
                },
            ],
            "capability": "Tracking to 400+ million km; supports Mars, lunar, and asteroid missions",
        },
        "assessed_vulnerabilities": [
            {
                "vulnerability": "Hub dependency on XSCC",
                "description": (
                    "Centralized C2 at XSCC creates a single point of failure. Disruption "
                    "of XSCC (kinetic, cyber, or EMP) would severely degrade satellite "
                    "command capability until backup operations established."
                ),
                "severity": "high",
            },
            {
                "vulnerability": "Yuan Wang fleet exposure",
                "description": (
                    "Yuan Wang tracking ships are vulnerable to interdiction in contested "
                    "waters. Loss of ship-based TT&C would create coverage gaps over oceans "
                    "during critical launch and orbital operations."
                ),
                "severity": "medium",
            },
            {
                "vulnerability": "Overseas station political risk",
                "description": (
                    "Overseas ground stations (Argentina, Namibia, Kiribati) are subject to "
                    "host nation political decisions. Political pressure could result in "
                    "access denial during a crisis."
                ),
                "severity": "medium",
            },
            {
                "vulnerability": "Tianlian relay as high-value target",
                "description": (
                    "The small number of Tianlian GEO relay satellites represent high-value "
                    "targets. Their loss would revert PRC to ground-station-only communications, "
                    "dramatically increasing ISR data latency."
                ),
                "severity": "high",
            },
        ],
        "source_references": [
            "CSIS Aerospace Security Project",
            "SWF Global Counterspace Capabilities reports",
            "CDSN design papers presented at IAC",
            "BeiDou ICD public documentation",
            "Commercial satellite imagery analysis",
            "DIA Challenges to Security in Space (2022)",
        ],
    }


# ---------------------------------------------------------------------------
# Russia Ground Architecture
# ---------------------------------------------------------------------------

def get_russia_architecture() -> dict:
    """Detailed Russian space ground segment architecture analysis."""
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "nation": "Russia",
        "overview": (
            "Russia maintains a extensive but aging space ground segment inherited from the "
            "Soviet Union with selective modernization. The architecture is centralized "
            "through the Titov Main Test and Space Systems Control Centre (TsITU-KS) at "
            "Krasnoznamensk. Key challenges include: loss of Soviet-era overseas stations, "
            "aging infrastructure, sanctions constraining electronics supply, and dependence "
            "on the Baikonur Cosmodrome in Kazakhstan."
        ),
        "titov_c2_architecture": {
            "description": (
                "The Titov Main Test Centre (TsITU-KS) at Krasnoznamensk is the primary C2 "
                "node for Russian military satellite operations. It coordinates the ground "
                "station network, processes tracking data, and generates commands for the "
                "satellite fleet. Operated by the 15th Aerospace Army of the Russian "
                "Aerospace Forces (VKS)."
            ),
            "hub": {
                "name": "Titov Main Test and Space Systems Control Centre (TsITU-KS)",
                "location": "Krasnoznamensk, Moscow Oblast",
                "coordinates": {"lat": 55.56, "lng": 36.75},
                "role": (
                    "Primary C2 for all Russian military satellites including GLONASS, "
                    "EKS early warning, Liana SIGINT, Bars-M ISR, and military comms. "
                    "Equivalent to US Combined Space Operations Center (CSpOC)."
                ),
                "subordinate_units": [
                    "Ground station network (NIP sites)",
                    "SKKP Space Surveillance system",
                    "Satellite testing and launch support",
                ],
            },
        },
        "voronezh_radar_network": {
            "description": (
                "Network of Voronezh-class phased-array early warning radars providing "
                "continuous perimeter missile warning coverage around Russia. Replacing "
                "Soviet-era Daryal and Dnepr radars. Each station provides 240-degree "
                "azimuth coverage with 6,000+ km detection range."
            ),
            "stations": [
                {
                    "name": "Voronezh-M — Lekhtusi (St Petersburg)",
                    "coordinates": {"lat": 60.38, "lng": 30.55},
                    "type": "VHF",
                    "coverage_sector": "Northwest (North Atlantic, Norwegian Sea SLBM corridor)",
                    "operational_since": 2012,
                },
                {
                    "name": "Voronezh-DM — Armavir",
                    "coordinates": {"lat": 44.85, "lng": 40.52},
                    "type": "UHF",
                    "coverage_sector": "Southwest (Turkey, Mediterranean, Middle East)",
                    "operational_since": 2009,
                },
                {
                    "name": "Voronezh-DM — Kaliningrad",
                    "coordinates": {"lat": 54.80, "lng": 20.38},
                    "type": "UHF",
                    "coverage_sector": "West (Central/Western Europe)",
                    "operational_since": 2014,
                },
                {
                    "name": "Voronezh-DM — Barnaul",
                    "coordinates": {"lat": 52.90, "lng": 84.33},
                    "type": "UHF",
                    "coverage_sector": "South (China, Central Asia)",
                    "operational_since": 2016,
                },
                {
                    "name": "Voronezh-M — Yeniseysk",
                    "coordinates": {"lat": 58.46, "lng": 91.99},
                    "type": "VHF",
                    "coverage_sector": "East (Pacific SLBM corridor)",
                    "operational_since": 2017,
                },
                {
                    "name": "Voronezh-VP — Orsk (reported under construction)",
                    "coordinates": {"lat": 51.20, "lng": 58.60},
                    "type": "UHF (advanced variant)",
                    "coverage_sector": "Southeast (Indian Ocean, South Asia)",
                    "operational_since": "under construction",
                },
                {
                    "name": "Voronezh — Sevastopol (Crimea, reported)",
                    "coordinates": {"lat": 44.60, "lng": 33.50},
                    "type": "UHF",
                    "coverage_sector": "South (Black Sea, Eastern Mediterranean)",
                    "operational_since": "reported under construction",
                },
            ],
            "space_surveillance_role": (
                "Voronezh radars have a secondary space object tracking capability. "
                "While primarily designed for ballistic missile detection, they can "
                "track objects in LEO/MEO as part of the SKKP (Space Surveillance System). "
                "Data feeds to Titov centre for catalog maintenance."
            ),
        },
        "okno_krona_space_surveillance": {
            "description": (
                "Dedicated space surveillance sensors providing object detection, tracking, "
                "and characterization. Part of the SKKP (Space Control System) under the "
                "15th Aerospace Army."
            ),
            "sensors": [
                {
                    "name": "Okno-M (Nurek, Tajikistan)",
                    "coordinates": {"lat": 38.39, "lng": 69.32},
                    "type": "Electro-optical",
                    "coverage": "GEO and HEO object detection and tracking",
                    "capability": (
                        "Primary Russian sensor for monitoring the GEO belt. Can detect "
                        "and characterize satellite maneuvers, new launches, and GEO-belt "
                        "proximity operations. Upgraded to Okno-M standard with improved "
                        "sensitivity. Altitude ~2,200m provides excellent seeing conditions."
                    ),
                },
                {
                    "name": "Krona (Zelenchukskaya, North Caucasus)",
                    "coordinates": {"lat": 43.65, "lng": 41.44},
                    "type": "Combined radar-optical",
                    "coverage": "LEO/MEO detection (radar) + characterization (optical)",
                    "capability": (
                        "Radar component detects objects in LEO/MEO; laser/optical component "
                        "provides high-resolution characterization of satellite structure. "
                        "Can image satellite features at close range. Part of SKKP."
                    ),
                },
                {
                    "name": "Altay Optical-Laser Centre",
                    "coordinates": {"lat": 51.34, "lng": 85.67},
                    "type": "Optical-laser",
                    "coverage": "Space object tracking and characterization",
                    "capability": (
                        "SLR, debris tracking, and assessed capability for satellite "
                        "dazzling/blinding of EO imaging satellites."
                    ),
                },
                {
                    "name": "Dunay-3U Radar (Chekhov, near Moscow)",
                    "coordinates": {"lat": 55.04, "lng": 37.20},
                    "type": "Radar",
                    "coverage": "Space object tracking, legacy system",
                    "capability": "Legacy OTH radar supplemented by Voronezh network",
                },
            ],
        },
        "deep_space_stations": {
            "description": (
                "Russian deep space communication network supporting interplanetary missions. "
                "Inherited from Soviet-era with selective modernization. Currently limited "
                "capacity constrains deep space mission support."
            ),
            "stations": [
                {
                    "name": "Bear Lakes (NIP-14, Medvezhi Ozera)",
                    "coordinates": {"lat": 55.87, "lng": 38.01},
                    "antennas": "64m RT-64 and smaller dishes",
                    "role": "Western hemisphere deep space comms",
                },
                {
                    "name": "Ussuriysk (NIP-15)",
                    "coordinates": {"lat": 43.80, "lng": 131.77},
                    "antennas": "70m RT-70",
                    "role": "Eastern hemisphere deep space comms",
                },
                {
                    "name": "Yevpatoria (NIP-16, Crimea)",
                    "coordinates": {"lat": 45.19, "lng": 33.20},
                    "antennas": "70m RT-70 (partially degraded)",
                    "role": "Southern deep space coverage (operational status uncertain post-2014)",
                },
            ],
        },
        "launch_infrastructure_roles": {
            "plesetsk": {
                "coordinates": {"lat": 62.93, "lng": 40.58},
                "role": (
                    "Primary military launch site. High-inclination orbits. Soyuz, Angara, "
                    "Rokot. Most Russian military satellite launches originate here. Also "
                    "hosts Nudol ASAT test infrastructure."
                ),
            },
            "baikonur": {
                "coordinates": {"lat": 45.92, "lng": 63.34},
                "role": (
                    "Leased from Kazakhstan (until 2050). Crewed Soyuz launches, Proton "
                    "heavy-lift (being retired), lower-inclination orbits. Strategic "
                    "importance declining as Russia shifts to Vostochny. Dependence on "
                    "foreign territory is a strategic vulnerability."
                ),
            },
            "vostochny": {
                "coordinates": {"lat": 51.88, "lng": 128.33},
                "role": (
                    "New launch facility in Russian Far East. Soyuz-2 operational since 2016. "
                    "Angara-A5 pad recently completed. Intended to achieve launch independence "
                    "from Baikonur. Slow buildout limits capability."
                ),
            },
        },
        "assessed_vulnerabilities": [
            {
                "vulnerability": "Geographic concentration on Russian territory",
                "description": (
                    "Unlike PRC, Russia has few overseas ground stations (lost most Soviet-era "
                    "overseas facilities). This creates significant coverage gaps over oceans "
                    "and the southern hemisphere, limiting satellite contact time."
                ),
                "severity": "high",
            },
            {
                "vulnerability": "Aging infrastructure",
                "description": (
                    "Much of the ground segment dates from the Soviet era with selective "
                    "modernization. Aging antennas, outdated electronics, and limited spare "
                    "parts constrain operational capacity. Sanctions further limit access to "
                    "modern electronics for upgrades."
                ),
                "severity": "high",
            },
            {
                "vulnerability": "Baikonur dependence",
                "description": (
                    "Continued dependence on Baikonur (Kazakhstan) for crewed and heavy-lift "
                    "launches. Political deterioration with Kazakhstan could deny access. "
                    "Vostochny buildout behind schedule."
                ),
                "severity": "medium",
            },
            {
                "vulnerability": "Okno dependence on Tajikistan",
                "description": (
                    "The primary GEO surveillance sensor (Okno-M) is located in Tajikistan, "
                    "a foreign country. Political instability or access denial would severely "
                    "degrade Russian GEO monitoring capability."
                ),
                "severity": "medium",
            },
            {
                "vulnerability": "Limited data relay capability",
                "description": (
                    "Russia lacks a robust data relay satellite system comparable to US TDRS "
                    "or PRC Tianlian. This means Russian ISR satellites must wait for ground "
                    "station overflight to downlink data, significantly increasing latency."
                ),
                "severity": "high",
            },
            {
                "vulnerability": "Sanctions impact on modernization",
                "description": (
                    "Western sanctions since 2014 (intensified 2022) severely constrain "
                    "access to radiation-hardened electronics, precision instruments, and "
                    "advanced manufacturing equipment needed for ground segment modernization."
                ),
                "severity": "critical",
            },
        ],
        "source_references": [
            "Pavel Podvig — Russian Nuclear Forces Project",
            "Bart Hendrickx — The Space Review (Russian space program analysis)",
            "SWF Global Counterspace Capabilities reports",
            "Russian MOD press releases and announcements",
            "FAS Strategic Security blog",
            "CSIS Aerospace Security Project",
        ],
    }


# ---------------------------------------------------------------------------
# FVEY Ground Architecture
# ---------------------------------------------------------------------------

def get_fvey_architecture() -> dict:
    """Detailed FVEY space ground segment architecture analysis."""
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "nation": "FVEY",
        "overview": (
            "The Five Eyes alliance operates the most capable and globally distributed space "
            "ground segment. The US provides the backbone through AFSCN, DSN, and Space "
            "Surveillance Network, while allied nations contribute geographically strategic "
            "sensors and facilities. The architecture benefits from global basing, advanced "
            "technology, and deep institutional integration across all five nations. "
            "Combined Space Operations (CSpO) initiative formalizes multinational space "
            "operations coordination."
        ),
        "afscn": {
            "name": "Air Force Satellite Control Network (AFSCN)",
            "description": (
                "Global network of ground stations providing TT&C for US military satellites. "
                "Operated by Space Operations Command. Remote Tracking Stations (RTS) are "
                "distributed worldwide to ensure continuous contact with satellites in all orbits."
            ),
            "stations": [
                {
                    "name": "Schriever SFB (Colorado) — AFSCN Hub / CSpOC",
                    "coordinates": {"lat": 38.80, "lng": -104.53},
                    "role": (
                        "Hub of AFSCN operations. Hosts Combined Space Operations Center "
                        "(CSpOC) and GPS Master Control Station. Coordinates all AFSCN RTS "
                        "operations. Primary C2 for US military space constellation."
                    ),
                },
                {
                    "name": "New Hampshire Tracking Station (RTS)",
                    "coordinates": {"lat": 42.95, "lng": -71.49},
                    "role": "Eastern US TT&C coverage",
                },
                {
                    "name": "Vandenberg Tracking Station (RTS)",
                    "coordinates": {"lat": 34.74, "lng": -120.57},
                    "role": "Western US TT&C and launch support",
                },
                {
                    "name": "Hawaii Tracking Station (RTS, Kaena Point)",
                    "coordinates": {"lat": 21.57, "lng": -158.25},
                    "role": "Pacific TT&C coverage",
                },
                {
                    "name": "Diego Garcia Tracking Station (RTS)",
                    "coordinates": {"lat": -7.32, "lng": 72.42},
                    "role": "Indian Ocean TT&C coverage",
                },
                {
                    "name": "Ascension Island Tracking Station (RTS)",
                    "coordinates": {"lat": -7.97, "lng": -14.40},
                    "role": "Mid-Atlantic TT&C coverage",
                },
                {
                    "name": "Thule Tracking Station (RTS, Greenland)",
                    "coordinates": {"lat": 76.53, "lng": -68.75},
                    "role": "High-latitude polar orbit TT&C, early warning",
                },
                {
                    "name": "Guam Tracking Station (RTS)",
                    "coordinates": {"lat": 13.62, "lng": 144.85},
                    "role": "Western Pacific TT&C coverage",
                },
            ],
        },
        "dsn": {
            "name": "Deep Space Network (DSN)",
            "description": (
                "NASA's Deep Space Network provides communication with spacecraft beyond "
                "Earth orbit. Three complexes spaced approximately 120 degrees apart in "
                "longitude ensure continuous deep-space coverage. Also supports high-orbit "
                "military satellite communication as a secondary mission."
            ),
            "complexes": [
                {
                    "name": "Goldstone Deep Space Complex",
                    "location": "Mojave Desert, California, USA",
                    "coordinates": {"lat": 35.43, "lng": -116.89},
                    "antennas": "70m DSS-14, 34m BWG antennas (DSS-24/25/26)",
                    "coverage": "Americas hemisphere deep space",
                },
                {
                    "name": "Canberra Deep Space Communication Complex",
                    "location": "Tidbinbilla, ACT, Australia",
                    "coordinates": {"lat": -35.40, "lng": 148.98},
                    "antennas": "70m DSS-43, 34m BWG antennas (DSS-34/35/36)",
                    "coverage": "Asia-Pacific hemisphere deep space",
                },
                {
                    "name": "Madrid Deep Space Communication Complex",
                    "location": "Robledo de Chavela, Spain",
                    "coordinates": {"lat": 40.43, "lng": -4.25},
                    "antennas": "70m DSS-63, 34m BWG antennas (DSS-54/55/56)",
                    "coverage": "Europe-Africa hemisphere deep space",
                },
            ],
            "military_relevance": (
                "DSN has been used for military satellite communication in emergencies and "
                "provides backup capability for high-orbit assets. The global 120-degree "
                "spacing ensures no deep-space communication gap. DSN expertise supports "
                "cislunar domain awareness development."
            ),
        },
        "space_surveillance_network": {
            "name": "Space Surveillance Network (SSN)",
            "description": (
                "Global network of radar and optical sensors tracking 47,000+ objects in "
                "Earth orbit. Provides the authoritative space object catalog. Operated by "
                "18th Space Defense Squadron with contributions from FVEY partners and allies."
            ),
            "key_sensors": [
                {
                    "name": "Space Fence (Kwajalein Atoll, Marshall Islands)",
                    "type": "S-band ground radar",
                    "coordinates": {"lat": 9.39, "lng": 167.48},
                    "capability": (
                        "Detects objects as small as 10cm in LEO. Operational since 2020. "
                        "Dramatically expanded catalog capacity. Can detect new launches, "
                        "breakups, and maneuvers within minutes."
                    ),
                },
                {
                    "name": "GEODSS — Maui, Hawaii",
                    "type": "Electro-optical",
                    "coordinates": {"lat": 20.71, "lng": -156.26},
                    "capability": "Deep-space (GEO/HEO) optical tracking",
                },
                {
                    "name": "GEODSS — Diego Garcia",
                    "type": "Electro-optical",
                    "coordinates": {"lat": -7.32, "lng": 72.42},
                    "capability": "Indian Ocean deep-space optical tracking",
                },
                {
                    "name": "GEODSS — Socorro, New Mexico",
                    "type": "Electro-optical",
                    "coordinates": {"lat": 33.82, "lng": -106.66},
                    "capability": "Americas deep-space optical tracking",
                },
                {
                    "name": "RAF Fylingdales (UK)",
                    "type": "AN/FPS-132 phased-array radar",
                    "coordinates": {"lat": 54.36, "lng": -0.67},
                    "capability": (
                        "BMEWS radar with space surveillance secondary mission. Provides "
                        "European coverage for space object tracking. Shared US/UK operation."
                    ),
                },
                {
                    "name": "Eglin Radar (AN/FPS-85, Florida)",
                    "type": "Phased-array radar",
                    "coordinates": {"lat": 30.57, "lng": -86.21},
                    "capability": "Dedicated space surveillance radar, deep-space capable",
                },
                {
                    "name": "Space Surveillance Telescope (SST, Exmouth, Australia)",
                    "type": "Electro-optical (3.5m aperture)",
                    "coordinates": {"lat": -21.82, "lng": 114.17},
                    "capability": (
                        "DARPA-developed wide-field telescope relocated from White Sands "
                        "to Australia in 2020. Provides southern hemisphere deep-space "
                        "surveillance of GEO belt. Addresses critical southern hemisphere "
                        "coverage gap."
                    ),
                },
                {
                    "name": "Woomera SSA Sensors (Australia)",
                    "type": "C-band radar + optical",
                    "coordinates": {"lat": -31.16, "lng": 136.83},
                    "capability": "Australian space surveillance contribution to SSN",
                },
                {
                    "name": "Sapphire Satellite (Canadian space surveillance asset)",
                    "type": "Space-based optical",
                    "coordinates": {"lat": 0.0, "lng": 0.0},
                    "capability": (
                        "Canadian military optical satellite tracking objects in deep space "
                        "(>15,000 km). Ground segment at Shirley Bay, Ottawa. Data contributed "
                        "to US SSN."
                    ),
                },
            ],
            "partner_contributions": [
                "UK: RAF Fylingdales radar, Ascension Island tracking",
                "Australia: SST at Exmouth, Woomera sensors, Pine Gap processing",
                "Canada: Sapphire satellite, NORAD data sharing",
                "New Zealand: Waihopai SIGINT, Awarua tracking",
            ],
        },
        "pine_gap": {
            "name": "Joint Defence Facility Pine Gap",
            "coordinates": {"lat": -23.80, "lng": 133.74},
            "description": (
                "Joint US-Australian intelligence facility near Alice Springs. One of the "
                "most important FVEY space intelligence ground nodes globally."
            ),
            "roles": [
                (
                    "Ground station for US SIGINT satellite constellation (Orion/Mentor "
                    "GEO SIGINT satellites). Processes signals intelligence collected from "
                    "space across the eastern hemisphere."
                ),
                (
                    "Relay and processing station for SBIRS missile early warning data. "
                    "Provides missile launch detection and tracking for the eastern hemisphere "
                    "including PRC, DPRK, and Indian Ocean regions."
                ),
                (
                    "Geospatial intelligence processing for NRO/NGA satellite imagery "
                    "products. Supports real-time intelligence production for Indo-Pacific "
                    "military operations."
                ),
                (
                    "Space domain awareness data fusion and analysis. Contributes to the "
                    "combined FVEY space picture."
                ),
            ],
            "operated_by": "CIA, NRO, NSA (US) and ASD, AGO (Australia)",
            "strategic_significance": (
                "Pine Gap's geographic location provides irreplaceable coverage of the "
                "eastern hemisphere. It is the primary ground node for US missile warning "
                "and SIGINT satellite operations covering Asia. Loss of Pine Gap would "
                "create a critical gap in US/FVEY space intelligence architecture."
            ),
        },
        "fvey_ssa_sharing": {
            "name": "Five Eyes SSA Sharing Architecture",
            "description": (
                "Formal and informal mechanisms for sharing space situational awareness "
                "data among FVEY nations and select allies."
            ),
            "mechanisms": [
                {
                    "name": "Combined Space Operations (CSpO) Initiative",
                    "description": (
                        "Multinational framework for combined space operations involving "
                        "US, UK, Australia, Canada, France, Germany, and New Zealand. "
                        "Coordinates SSA data sharing, space protection, and combined "
                        "space operations from the Combined Space Operations Center."
                    ),
                },
                {
                    "name": "SSA Data Sharing Agreements",
                    "description": (
                        "Bilateral and multilateral agreements for sharing space object "
                        "tracking data. 18th SDS provides basic conjunction warnings to "
                        "all operators; enhanced data shared with allied military partners."
                    ),
                },
                {
                    "name": "Operation Olympic Defender",
                    "description": (
                        "Multinational coalition operation for space domain awareness and "
                        "protection, led by US Space Command with FVEY participation. "
                        "Shares intelligence on adversary space activities and coordinates "
                        "defensive responses."
                    ),
                },
            ],
        },
        "gps_ground_control": {
            "name": "GPS Ground Control Segment",
            "description": (
                "GPS constellation ground control is operated by 2nd Space Operations "
                "Squadron from Schriever SFB with a worldwide network of monitoring "
                "stations and ground antennas."
            ),
            "master_control": "Schriever SFB, Colorado (with backup at Vandenberg SFB)",
            "monitor_stations": (
                "16 monitoring stations worldwide (6 AFSCN sites + 10 NGA sites) "
                "providing global GPS signal monitoring."
            ),
            "ground_antennas": (
                "Large ground antennas at Ascension Island, Diego Garcia, Kwajalein, "
                "and Cape Canaveral for navigation message upload."
            ),
        },
        "assessed_vulnerabilities": [
            {
                "vulnerability": "Concentration of C2 at Schriever/Colorado",
                "description": (
                    "Significant C2 functions concentrated in the Colorado Springs area "
                    "(Schriever, Peterson, Cheyenne Mountain). While dispersal efforts "
                    "are underway, current concentration creates a high-value target set."
                ),
                "severity": "medium",
            },
            {
                "vulnerability": "Ground station cyber vulnerability",
                "description": (
                    "AFSCN and SSN ground stations are networked systems vulnerable to "
                    "cyber attack. The 2022 Viasat incident demonstrated that ground "
                    "segment cyber attacks can disable space services without touching "
                    "the satellites themselves."
                ),
                "severity": "high",
            },
            {
                "vulnerability": "GEODSS weather dependence",
                "description": (
                    "Optical sensors (GEODSS, SST) are dependent on clear skies. Cloud "
                    "cover can reduce deep-space surveillance coverage, particularly at "
                    "individual sites. Mitigated by multiple geographic sites but gaps exist."
                ),
                "severity": "low",
            },
            {
                "vulnerability": "Pine Gap single point of failure",
                "description": (
                    "Pine Gap provides irreplaceable eastern hemisphere SIGINT satellite "
                    "ground processing. While hardened, its loss would severely degrade "
                    "FVEY space-based SIGINT coverage of Asia."
                ),
                "severity": "high",
            },
            {
                "vulnerability": "Political risk at overseas locations",
                "description": (
                    "Some AFSCN and SSN sites are located on foreign territory (Diego "
                    "Garcia, Ascension, Thule/Greenland). Host nation political changes "
                    "could affect access, though deep alliance relationships mitigate this."
                ),
                "severity": "low",
            },
            {
                "vulnerability": "Southern hemisphere coverage gap",
                "description": (
                    "Despite SST relocation to Australia and Diego Garcia assets, southern "
                    "hemisphere space surveillance coverage remains thinner than northern "
                    "hemisphere. Adversary satellites in high-inclination orbits have "
                    "reduced tracking over southern passages."
                ),
                "severity": "medium",
            },
        ],
        "source_references": [
            "USSF fact sheets and organizational documents",
            "GAO reports on GPS, SBIRS, and space surveillance",
            "Desmond Ball (ANU) — Pine Gap publications",
            "DARPA SST program documentation",
            "CSpO initiative public statements",
            "Congressional Research Service — US Space Force reports",
            "Australian DoD annual reports and Defence Strategic Review",
            "UK MOD Defence Command Paper",
            "Canadian DND space program documentation",
        ],
    }


# ---------------------------------------------------------------------------
# Architecture Comparison
# ---------------------------------------------------------------------------

def get_architecture_comparison() -> dict:
    """Side-by-side comparison of adversary vs FVEY ground capabilities."""
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "title": "Ground Segment Architecture Comparison: Adversary vs FVEY",
        "comparison_matrix": {
            "global_coverage": {
                "PRC": {
                    "rating": "expanding",
                    "assessment": (
                        "Rapidly expanding global coverage through overseas stations (Argentina, "
                        "Namibia, Pakistan), Yuan Wang tracking ships, and Tianlian relay "
                        "satellites. Still gaps in the Americas and Africa but closing fast."
                    ),
                },
                "Russia": {
                    "rating": "degraded",
                    "assessment": (
                        "Significantly degraded from Soviet-era global reach. Lost most overseas "
                        "stations. Coverage concentrated on Russian territory with gaps over "
                        "oceans and southern hemisphere. Okno in Tajikistan partially compensates."
                    ),
                },
                "FVEY": {
                    "rating": "superior",
                    "assessment": (
                        "Most globally distributed ground segment. AFSCN provides worldwide "
                        "TT&C. DSN covers all deep space. SSN sensors on multiple continents. "
                        "Allied contributions fill geographic gaps. TDRS relay eliminates most "
                        "coverage gaps for LEO assets."
                    ),
                },
            },
            "space_surveillance": {
                "PRC": {
                    "sensors": "Expanding optical/radar SSA network, satellite laser ranging",
                    "catalog_size": "Estimated 10,000+ objects (growing)",
                    "coverage": "Primarily northern hemisphere, GEO monitoring improving",
                    "assessment": (
                        "Rapidly improving but still behind FVEY in sensor number and geographic "
                        "distribution. Strong academic SSA research base. Growing but not yet "
                        "matching US 18th SDS catalog."
                    ),
                },
                "Russia": {
                    "sensors": "Voronezh radars, Okno-M, Krona, legacy systems",
                    "catalog_size": "Estimated 5,000-10,000 objects",
                    "coverage": "Primarily Eurasian, GEO coverage from Okno (Tajikistan)",
                    "assessment": (
                        "Selective modernization (Voronezh, Okno-M upgrade) but overall aging "
                        "and geographically limited. Significant southern hemisphere blind spots. "
                        "Capable but declining relative to PRC and FVEY."
                    ),
                },
                "FVEY": {
                    "sensors": "Space Fence, GEODSS, SST, Fylingdales, Eglin, allied sensors",
                    "catalog_size": "47,000+ objects (authoritative catalog)",
                    "coverage": "Global, all orbit regimes, supplemented by commercial SSA",
                    "assessment": (
                        "Maintains the authoritative space object catalog. Space Fence provides "
                        "unprecedented LEO detection. GEODSS/SST cover deep space. Allied "
                        "contributions (UK, Australia, Canada) extend coverage. Supplemented "
                        "by commercial SSA providers (LeoLabs, ExoAnalytic, Slingshot)."
                    ),
                },
            },
            "data_relay": {
                "PRC": {
                    "system": "Tianlian (Sky Link) GEO relay constellation",
                    "capability": "6+ relay satellites, near-continuous LEO coverage",
                    "assessment": (
                        "Functional and growing. Enables near-real-time ISR data from Yaogan "
                        "constellation. Reduces sensor-to-shooter timeline significantly."
                    ),
                },
                "Russia": {
                    "system": "Luch relay satellites (limited)",
                    "capability": "3 GEO relay satellites, limited bandwidth",
                    "assessment": (
                        "Significantly inferior to US TDRS and PRC Tianlian. Limited bandwidth "
                        "and satellite health issues. Russian ISR satellites still largely depend "
                        "on direct ground station downlink, increasing data latency."
                    ),
                },
                "FVEY": {
                    "system": "TDRS (Tracking and Data Relay Satellite System)",
                    "capability": "10+ GEO relay satellites, global LEO coverage, high bandwidth",
                    "assessment": (
                        "Most mature and capable data relay system. Provides continuous "
                        "high-bandwidth communication with LEO assets. Military and civilian "
                        "shared infrastructure. Being supplemented by commercial relay services."
                    ),
                },
            },
            "deep_space": {
                "PRC": {
                    "stations": 3,
                    "locations": "Jiamusi, Kashi, Neuquen (Argentina)",
                    "max_antenna": "66m",
                    "assessment": "Fully functional 3-station CDSN. Supports lunar and Mars missions.",
                },
                "Russia": {
                    "stations": 3,
                    "locations": "Bear Lakes, Ussuriysk, Yevpatoria (Crimea, degraded)",
                    "max_antenna": "70m",
                    "assessment": (
                        "Aging infrastructure. Yevpatoria status uncertain since 2014. "
                        "Sufficient for current limited deep space program but constrained."
                    ),
                },
                "FVEY": {
                    "stations": 3,
                    "locations": "Goldstone, Canberra, Madrid",
                    "max_antenna": "70m",
                    "assessment": (
                        "Most capable deep space network globally. Continuous coverage. "
                        "High bandwidth. Supports dozens of active deep space missions. "
                        "Being upgraded with new 34m antennas."
                    ),
                },
            },
            "launch_infrastructure": {
                "PRC": {
                    "sites": 4,
                    "locations": "Wenchang, Jiuquan, Xichang, Taiyuan",
                    "annual_launches_2024": "60+",
                    "assessment": (
                        "Highest launch cadence after US. Four active sites cover all orbit "
                        "types. Commercial sector emerging. Rapidly approaching US capability."
                    ),
                },
                "Russia": {
                    "sites": 3,
                    "locations": "Plesetsk, Baikonur (Kazakhstan), Vostochny",
                    "annual_launches_2024": "15-20",
                    "assessment": (
                        "Declining launch cadence. Baikonur dependence on Kazakhstan. "
                        "Vostochny buildout behind schedule. Angara replacing Proton slowly. "
                        "Significant decline from Soviet-era capability."
                    ),
                },
                "FVEY": {
                    "sites": "5+ (US) plus commercial",
                    "locations": "Cape Canaveral, Vandenberg, Wallops, Kodiak, Mahia (NZ), plus commercial",
                    "annual_launches_2024": "140+ (US alone, primarily SpaceX)",
                    "assessment": (
                        "Dominant global launch capability driven by SpaceX reusability. "
                        "Highest cadence globally. Multiple commercial providers. FVEY "
                        "benefits from Rocket Lab (NZ/US) and UK launch development."
                    ),
                },
            },
        },
        "key_gaps_and_asymmetries": [
            {
                "area": "PRC Tianlian relay vs FVEY TDRS",
                "assessment": (
                    "PRC is closing the data relay gap rapidly. Tianlian enables near-real-time "
                    "ISR from Yaogan constellation, reducing FVEY intelligence advantage."
                ),
            },
            {
                "area": "Russian ground segment decline",
                "assessment": (
                    "Russia's ground segment is the most constrained of the three blocs. "
                    "Sanctions, funding shortfalls, and loss of overseas stations create "
                    "significant coverage gaps. PRC-Russia cooperation may partially offset."
                ),
            },
            {
                "area": "FVEY commercial augmentation advantage",
                "assessment": (
                    "FVEY's commercial space ecosystem (SpaceX, Planet, Maxar, LeoLabs, etc.) "
                    "provides massive additional capacity beyond government systems. Neither "
                    "PRC nor Russia have equivalent commercial sector depth, though PRC is "
                    "building one rapidly."
                ),
            },
            {
                "area": "Southern hemisphere coverage",
                "assessment": (
                    "All parties have thinner southern hemisphere coverage, but FVEY has the "
                    "best southern sensors (DSN Canberra, SST Exmouth, Diego Garcia, Woomera). "
                    "PRC Argentina station partially addresses their gap."
                ),
            },
            {
                "area": "Cyber vulnerability — universal",
                "assessment": (
                    "All ground segments are vulnerable to cyber attack. The 2022 Viasat "
                    "incident demonstrated real-world impact. FVEY has the most sophisticated "
                    "cyber defense but also the largest attack surface due to network "
                    "connectivity and commercial integration."
                ),
            },
        ],
        "overall_assessment": (
            "FVEY maintains a significant overall ground segment advantage in global coverage, "
            "sensor capability, launch capacity, and data relay. PRC is the fastest-growing "
            "competitor, systematically closing gaps across all domains with particular strength "
            "in ISR data relay (Tianlian) and launch cadence. Russia's ground segment is in "
            "relative decline due to sanctions, funding constraints, and loss of overseas "
            "access, increasingly dependent on PRC cooperation. The FVEY advantage is most "
            "pronounced in commercial augmentation, SSA catalog completeness, and deep space "
            "capability, but PRC is on a trajectory to achieve near-parity in critical military "
            "domains by 2030."
        ),
        "source_references": [
            "CSIS Aerospace Security Project — Space Threat Assessment series",
            "SWF Global Counterspace Capabilities reports",
            "DIA Challenges to Security in Space (2022)",
            "GAO reports on US space systems",
            "Congressional Research Service — Space Force and Space Domain Awareness",
            "Australian DoD Defence Strategic Review",
            "Pavel Podvig — Russian Nuclear Forces Project",
            "Bart Hendrickx — The Space Review",
        ],
    }
