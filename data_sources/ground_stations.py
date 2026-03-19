"""
Adversary & FVEY ground station / space infrastructure database
All data sourced from open-source intelligence: Google Earth imagery analysis,
academic publications, government white papers, CSIS Aerospace Security Project,
Secure World Foundation reports, NASIC unclassified assessments, and news reporting.

Coordinates are approximate and derived from public satellite imagery.
"""
from __future__ import annotations

from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Facility type constants
# ---------------------------------------------------------------------------
TYPE_LAUNCH = "launch"
TYPE_TTC = "ttc"             # Telemetry, Tracking & Command
TYPE_SURVEILLANCE = "surveillance"
TYPE_RADAR = "radar"
TYPE_C2 = "c2"              # Command & Control
TYPE_DEEP_SPACE = "deep_space"
TYPE_MOBILE = "mobile"
TYPE_MULTI = "multi"         # Multiple functions

STATUS_ACTIVE = "active"
STATUS_SUSPECTED = "suspected"
STATUS_DECOMMISSIONED = "decommissioned"
STATUS_UNDER_CONSTRUCTION = "under_construction"

# ---------------------------------------------------------------------------
# PRC Ground Stations & Facilities
# ---------------------------------------------------------------------------

_PRC_STATIONS: List[dict] = [
    {
        "name": "Xi'an Satellite Control Centre (XSCC)",
        "lat": 34.26,
        "lng": 108.94,
        "country": "PRC",
        "type": TYPE_C2,
        "status": STATUS_ACTIVE,
        "description": (
            "Primary satellite TT&C hub for the PLA Strategic Support Force (now "
            "Information Support Force). Controls military and civilian satellites. "
            "Hosts the Beijing Aerospace Control Centre (BACC) operations for human "
            "spaceflight and deep space missions. Coordinates the distributed TT&C "
            "network including ground stations and Yuan Wang tracking ships."
        ),
        "open_source_ref": "CSIS Aerospace Security Project; PRC state media; SWF Global Counterspace Capabilities 2023",
    },
    {
        "name": "Kashgar TT&C Station",
        "lat": 39.50,
        "lng": 75.98,
        "country": "PRC",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Western China ground station providing TT&C coverage for satellites "
            "passing over Central and South Asia. Critical for BeiDou navigation "
            "constellation management and deep space communications. Features "
            "multiple large-aperture dish antennas visible in commercial satellite imagery."
        ),
        "open_source_ref": "Google Earth imagery; ESPI China space report 2022; BeiDou ICD public documentation",
    },
    {
        "name": "Sanya TT&C Station",
        "lat": 18.31,
        "lng": 109.60,
        "country": "PRC",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Located on Hainan Island, provides southern coverage for GEO satellite "
            "operations and launch tracking from Wenchang. Key for South China Sea "
            "satellite coverage. Expanded significantly after 2016 with construction "
            "of new antenna facilities."
        ),
        "open_source_ref": "Commercial satellite imagery analysis; CSIS Asia Maritime Transparency Initiative",
    },
    {
        "name": "Miyun Ground Station",
        "lat": 40.56,
        "lng": 116.87,
        "country": "PRC",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Located northeast of Beijing. Hosts multiple dish antennas for satellite "
            "data reception. Key node in PRC earth observation data downlink network. "
            "Operated by Chinese Academy of Sciences (CAS) for civilian remote sensing "
            "but data shared with military users."
        ),
        "open_source_ref": "CAS public listings; academic publications from CAS Remote Sensing Institute",
    },
    {
        "name": "Changchun Observatory / Space Surveillance",
        "lat": 43.79,
        "lng": 125.44,
        "country": "PRC",
        "type": TYPE_SURVEILLANCE,
        "status": STATUS_ACTIVE,
        "description": (
            "National Astronomical Observatories of China (NAOC) facility involved "
            "in optical space surveillance and satellite laser ranging (SLR). Part of "
            "China's expanding SSA network. Research published in open literature on "
            "debris tracking and conjunction analysis."
        ),
        "open_source_ref": "NAOC publications; IAC conference papers on Chinese SSA",
    },
    {
        "name": "Kunming TT&C Station",
        "lat": 25.03,
        "lng": 102.80,
        "country": "PRC",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Yunnan province TT&C station providing coverage for southern orbital passes. "
            "Part of the distributed ground network. Supports BeiDou and other constellation "
            "operations."
        ),
        "open_source_ref": "BeiDou system documentation; PRC space white papers",
    },
    {
        "name": "Jiamusi Deep Space Station",
        "lat": 46.50,
        "lng": 130.32,
        "country": "PRC",
        "type": TYPE_DEEP_SPACE,
        "status": STATUS_ACTIVE,
        "description": (
            "66-m and 35-m antenna complex in Heilongjiang province. Part of the "
            "Chinese Deep Space Network (CDSN). Supports lunar and planetary missions "
            "(Chang'e, Tianwen). Provides deep space tracking to ~400 million km. "
            "Dual-use capability for military GEO satellite operations."
        ),
        "open_source_ref": "CDSN design papers (IAC); PRC state media Xinhua; commercial imagery",
    },
    {
        "name": "Kashi (Kashgar) Deep Space Station",
        "lat": 39.51,
        "lng": 76.03,
        "country": "PRC",
        "type": TYPE_DEEP_SPACE,
        "status": STATUS_ACTIVE,
        "description": (
            "35-m antenna deep space station co-located near Kashgar TT&C. Provides "
            "western-hemisphere deep space coverage for Chang'e and Tianwen missions. "
            "Part of 3-station CDSN baseline with Jiamusi and overseas stations."
        ),
        "open_source_ref": "CDSN documentation; IAC 2019 papers; ESA cooperation reports",
    },
    {
        "name": "Weinan TT&C Station",
        "lat": 34.50,
        "lng": 109.50,
        "country": "PRC",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Located in Shaanxi province near Xi'an. Supports XSCC operations as a "
            "nearby ground station. Handles routine TT&C for LEO satellite passes."
        ),
        "open_source_ref": "PRC state media reports on satellite operations",
    },
    {
        "name": "Yuan Wang Tracking Ships (Fleet)",
        "lat": -5.0,
        "lng": 165.0,
        "country": "PRC",
        "type": TYPE_MOBILE,
        "status": STATUS_ACTIVE,
        "description": (
            "Fleet of ~7 operational space tracking ships (Yuan Wang 3, 5, 6, 7 etc.) "
            "deployed globally to fill TT&C coverage gaps over oceans. Routinely operate "
            "in the South Pacific, Indian Ocean, and Atlantic. Provide launch telemetry, "
            "orbital injection confirmation, and satellite commanding. Also reported to "
            "conduct SIGINT collection. Position shown is approximate typical deployment "
            "area; actual positions vary by mission."
        ),
        "open_source_ref": "MarineTraffic AIS data; OSINT analysis by @HenriKenhworthy; PRC MOD press releases",
    },
    {
        "name": "Wenchang Satellite Launch Centre",
        "lat": 19.61,
        "lng": 110.95,
        "country": "PRC",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "Hainan Island coastal launch facility. Supports Long March 5, 7, 8 series. "
            "Primary facility for heavy-lift missions including space station modules, "
            "lunar missions, and GEO satellites. Equatorial advantage for GTO launches."
        ),
        "open_source_ref": "PRC state media; commercial satellite imagery; launch manifest databases",
    },
    {
        "name": "Jiuquan Satellite Launch Centre",
        "lat": 40.96,
        "lng": 100.29,
        "country": "PRC",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "Oldest PRC launch site in the Gobi Desert. Supports crewed Shenzhou launches, "
            "LEO missions. Multiple pads for Long March 2, 4, 11 series and commercial vehicles."
        ),
        "open_source_ref": "Public launch records; Gunter's Space Page; satellite imagery",
    },
    {
        "name": "Xichang Satellite Launch Centre",
        "lat": 28.25,
        "lng": 102.03,
        "country": "PRC",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "Sichuan province launch facility. Primary site for GEO satellite launches "
            "including BeiDou constellation deployment. Supports Long March 3 series."
        ),
        "open_source_ref": "Public launch records; Gunter's Space Page; satellite imagery",
    },
    {
        "name": "Taiyuan Satellite Launch Centre",
        "lat": 38.85,
        "lng": 111.61,
        "country": "PRC",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "Shanxi province launch facility specializing in polar and sun-synchronous "
            "orbit launches. Primary site for Yaogan ISR constellation and Fengyun "
            "weather satellites. Supports Long March 2, 4, 6 series."
        ),
        "open_source_ref": "Public launch records; Gunter's Space Page; satellite imagery",
    },
    {
        "name": "Purple Mountain Observatory SSA",
        "lat": 32.07,
        "lng": 118.83,
        "country": "PRC",
        "type": TYPE_SURVEILLANCE,
        "status": STATUS_ACTIVE,
        "description": (
            "CAS facility near Nanjing conducting space debris tracking and SSA research. "
            "Operates optical telescopes and laser ranging systems. Publishes conjunction "
            "assessments in open literature."
        ),
        "open_source_ref": "CAS publications; IAA Space Debris Committee papers",
    },
    {
        "name": "PRC Space Surveillance Phased-Array Radar (Xinjiang)",
        "lat": 41.5,
        "lng": 86.0,
        "country": "PRC",
        "type": TYPE_RADAR,
        "status": STATUS_SUSPECTED,
        "description": (
            "Suspected large phased-array radar facility in Xinjiang region. Assessed "
            "to provide space surveillance and potential missile early warning capability. "
            "Analysis of commercial satellite imagery shows large radar structures consistent "
            "with deep-space tracking."
        ),
        "open_source_ref": "Commercial satellite imagery analysis (Planet Labs); OSINT analyst reports",
    },
]

# ---------------------------------------------------------------------------
# Russia Ground Stations & Facilities
# ---------------------------------------------------------------------------

_RUSSIA_STATIONS: List[dict] = [
    {
        "name": "Titov Main Test and Space Systems Control Centre (TsITU-KS)",
        "lat": 55.56,
        "lng": 36.75,
        "country": "Russia",
        "type": TYPE_C2,
        "status": STATUS_ACTIVE,
        "description": (
            "Primary command and control centre for Russian military and civilian satellite "
            "constellations, located in Krasnoznamensk near Moscow. Controls GLONASS, "
            "military comms, ISR, and early warning satellites. Equivalent role to US "
            "Combined Space Operations Center (CSpOC). Operated by the Aerospace Forces "
            "(VKS) 15th Aerospace Army."
        ),
        "open_source_ref": "Russian MOD press releases; Bart Hendrickx analysis (The Space Review); SWF reports",
    },
    {
        "name": "Plesetsk Cosmodrome",
        "lat": 62.93,
        "lng": 40.58,
        "country": "Russia",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "Primary military launch site in Arkhangelsk Oblast. Launches Soyuz, Angara, "
            "and Rokot vehicles. High-inclination orbit access. Site of most Russian "
            "military satellite launches including GLONASS replenishment, EKS early warning, "
            "and COSMOS military payloads. Also hosts Nudol DA-ASAT testing infrastructure."
        ),
        "open_source_ref": "Russian MOD announcements; launch records; commercial satellite imagery",
    },
    {
        "name": "Baikonur Cosmodrome",
        "lat": 45.92,
        "lng": 63.34,
        "country": "Russia",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "Historic launch facility in Kazakhstan, leased by Russia until 2050. "
            "Supports Soyuz crewed launches, Proton heavy-lift, and remaining "
            "commercial missions. Strategic importance declining as Russia shifts "
            "to Vostochny. Multiple launch pads across the sprawling complex."
        ),
        "open_source_ref": "Roscosmos press releases; lease agreements (public); satellite imagery",
    },
    {
        "name": "Vostochny Cosmodrome",
        "lat": 51.88,
        "lng": 128.33,
        "country": "Russia",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "New launch facility in Amur Oblast, Russian Far East. Soyuz-2 pad operational "
            "since 2016. Angara-A5 pad under construction/testing. Intended to reduce "
            "dependence on Baikonur (Kazakhstan). Eastward location enables Pacific "
            "tracking and international cooperation."
        ),
        "open_source_ref": "Roscosmos; commercial imagery; news reporting",
    },
    {
        "name": "Altay Optical-Laser Centre",
        "lat": 51.34,
        "lng": 85.67,
        "country": "Russia",
        "type": TYPE_SURVEILLANCE,
        "status": STATUS_ACTIVE,
        "description": (
            "Advanced optical-laser facility in the Altai Mountains. Conducts satellite "
            "laser ranging, space debris tracking, and is assessed to have capability for "
            "anti-satellite laser dazzling/blinding of imaging satellites. Clear mountain "
            "skies provide excellent seeing conditions."
        ),
        "open_source_ref": "Russian academic publications; Secure World Foundation 2023 report; ROSCOSMOS documentation",
    },
    {
        "name": "Dunay Radar (Chekhov)",
        "lat": 55.04,
        "lng": 37.20,
        "country": "Russia",
        "type": TYPE_RADAR,
        "status": STATUS_ACTIVE,
        "description": (
            "Dunay-3U over-the-horizon radar near Moscow. Part of the Russian space "
            "surveillance network (SKKP). Provides space object tracking and missile "
            "early warning. Legacy system being supplemented by Voronezh radars."
        ),
        "open_source_ref": "Russian MOD; Pavel Podvig (Russian Nuclear Forces Project); FAS analysis",
    },
    {
        "name": "Voronezh Radar — Lekhtusi (St Petersburg)",
        "lat": 60.38,
        "lng": 30.55,
        "country": "Russia",
        "type": TYPE_RADAR,
        "status": STATUS_ACTIVE,
        "description": (
            "Voronezh-M VHF phased-array early warning radar covering northwestern "
            "approaches (SLBM corridor from North Atlantic/Norwegian Sea). Operational "
            "since 2012. Can track space objects as secondary mission."
        ),
        "open_source_ref": "Russian MOD press; Pavel Podvig analysis; CSIS Missile Defense Project",
    },
    {
        "name": "Voronezh Radar — Armavir (Southern Russia)",
        "lat": 44.85,
        "lng": 40.52,
        "country": "Russia",
        "type": TYPE_RADAR,
        "status": STATUS_ACTIVE,
        "description": (
            "Two Voronezh-DM radar stations covering southwestern approaches (Turkey, "
            "Mediterranean, Middle East). Operational since 2009. Detects ballistic "
            "missile launches and tracks space objects."
        ),
        "open_source_ref": "Russian MOD; NTI analysis; commercial satellite imagery",
    },
    {
        "name": "Voronezh Radar — Kaliningrad",
        "lat": 54.80,
        "lng": 20.38,
        "country": "Russia",
        "type": TYPE_RADAR,
        "status": STATUS_ACTIVE,
        "description": (
            "Voronezh-DM radar covering western approaches (Central/Western Europe). "
            "Operational since 2014. Part of the continuous early warning perimeter "
            "Russia is rebuilding post-Soviet collapse."
        ),
        "open_source_ref": "Russian MOD; Podvig/IPFM analysis",
    },
    {
        "name": "Voronezh Radar — Barnaul (Siberia)",
        "lat": 52.90,
        "lng": 84.33,
        "country": "Russia",
        "type": TYPE_RADAR,
        "status": STATUS_ACTIVE,
        "description": (
            "Voronezh-DM radar covering southern Siberia approaches (China, Central Asia). "
            "Operational since 2016. Fills the gap left by the decommissioned Balkhash "
            "radar in Kazakhstan."
        ),
        "open_source_ref": "Russian MOD announcements; FAS Strategic Security blog",
    },
    {
        "name": "Voronezh Radar — Yeniseysk (Central Siberia)",
        "lat": 58.46,
        "lng": 91.99,
        "country": "Russia",
        "type": TYPE_RADAR,
        "status": STATUS_ACTIVE,
        "description": (
            "Voronezh-M radar covering eastern approaches. Fills coverage gap in "
            "central Siberia for ICBM/SLBM detection from the Pacific."
        ),
        "open_source_ref": "Russian MOD; Pavel Podvig Russian Nuclear Forces Project",
    },
    {
        "name": "Okno-M Space Surveillance (Nurek, Tajikistan)",
        "lat": 38.39,
        "lng": 69.32,
        "country": "Russia",
        "type": TYPE_SURVEILLANCE,
        "status": STATUS_ACTIVE,
        "description": (
            "Electro-optical space surveillance system at ~2,200m altitude in Tajikistan. "
            "Detects and tracks objects in GEO and HEO. Can characterize satellite "
            "maneuvers and identify new launches. Upgraded to Okno-M standard. Primary "
            "Russian sensor for monitoring GEO belt activity."
        ),
        "open_source_ref": "SWF Global Counterspace Capabilities; Russian MOD; Bart Hendrickx (The Space Review)",
    },
    {
        "name": "Krona Space Surveillance (Zelenchukskaya)",
        "lat": 43.65,
        "lng": 41.44,
        "country": "Russia",
        "type": TYPE_SURVEILLANCE,
        "status": STATUS_ACTIVE,
        "description": (
            "Combined radar-optical space surveillance complex in the North Caucasus. "
            "Radar component detects objects in LEO/MEO; optical telescope characterizes "
            "them. Can image satellite structure at close range. Part of the SKKP "
            "(Space Control System)."
        ),
        "open_source_ref": "Russian MOD; Bart Hendrickx analysis; SWF reports",
    },
    {
        "name": "Bear Lakes Ground Station (NIP-14, Medvezhi Ozera)",
        "lat": 55.87,
        "lng": 38.01,
        "country": "Russia",
        "type": TYPE_DEEP_SPACE,
        "status": STATUS_ACTIVE,
        "description": (
            "Deep space communication complex east of Moscow. Multiple large antennas "
            "(up to 64m). Supports interplanetary missions and high-orbit satellite "
            "communications. Part of the deep space network alongside Ussuriysk."
        ),
        "open_source_ref": "IKI/RAS publications; Roscosmos documentation",
    },
    {
        "name": "Ussuriysk Ground Station (NIP-15)",
        "lat": 43.80,
        "lng": 131.77,
        "country": "Russia",
        "type": TYPE_DEEP_SPACE,
        "status": STATUS_ACTIVE,
        "description": (
            "Far-eastern deep space station near Vladivostok. 70m RT-70 antenna "
            "provides eastern hemisphere deep space coverage. Critical for "
            "interplanetary mission support. Dual civilian/military use."
        ),
        "open_source_ref": "IKI publications; Roscosmos; academic papers",
    },
    {
        "name": "Crimea Tracking Stations (Yevpatoria/NIP-16)",
        "lat": 45.19,
        "lng": 33.20,
        "country": "Russia",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Multiple tracking facilities in Crimea including the historic 70m RT-70 "
            "deep space antenna at Yevpatoria. Russia seized control post-2014 annexation. "
            "Used for satellite tracking, deep space communication, and assessed EW "
            "operations. Operational status partially degraded."
        ),
        "open_source_ref": "Post-2014 media reporting; satellite imagery; OSINT analysis",
    },
    {
        "name": "Peresvet Laser System (Mobile/Multiple Locations)",
        "lat": 56.0,
        "lng": 44.0,
        "country": "Russia",
        "type": TYPE_SURVEILLANCE,
        "status": STATUS_ACTIVE,
        "description": (
            "Ground-based mobile laser system assessed capable of dazzling/blinding "
            "adversary imaging satellites. Announced operational with RVSN (Strategic "
            "Rocket Forces) units in 2018. Exact deployment locations classified; "
            "assessed at ICBM bases for satellite denial during launch operations. "
            "Position shown is approximate (Kozelsk ICBM base region)."
        ),
        "open_source_ref": "Putin 2018 address; Russian MOD video releases; SWF Global Counterspace 2023",
    },
]

# ---------------------------------------------------------------------------
# DPRK Ground Stations & Facilities
# ---------------------------------------------------------------------------

_DPRK_STATIONS: List[dict] = [
    {
        "name": "Sohae Satellite Launching Station (Tongchang-ri)",
        "lat": 39.66,
        "lng": 124.71,
        "country": "DPRK",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "Primary DPRK satellite launch facility on the west coast. Upgraded launch "
            "pad and engine test stand. Used for Unha-3 SLV launches (2012) and "
            "Chollima-1 (2023, failed). Vertical assembly building and mobile "
            "infrastructure visible in commercial imagery. Also used for ICBM "
            "engine ground testing."
        ),
        "open_source_ref": "38 North analysis; Planet Labs imagery; CSIS Missile Threat Project",
    },
    {
        "name": "Tonghae Satellite Launching Ground (Musudan-ri)",
        "lat": 40.85,
        "lng": 129.66,
        "country": "DPRK",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "East coast launch facility. Used for early Taepodong/Unha launches. "
            "Features launch pad, assembly building, and tracking radars. Currently "
            "secondary to Sohae but maintained for surge or east-over-water trajectories."
        ),
        "open_source_ref": "38 North; NGA unclassified imagery analysis; news reporting",
    },
    {
        "name": "Pyongyang Space Control Centre",
        "lat": 39.05,
        "lng": 125.73,
        "country": "DPRK",
        "type": TYPE_C2,
        "status": STATUS_ACTIVE,
        "description": (
            "General Satellite Control Centre in Pyongyang. Receives telemetry from "
            "Kwangmyongsong and Malligyong-1 satellites. Limited capability — DPRK "
            "satellites have shown minimal operational activity post-launch, suggesting "
            "ground segment limitations."
        ),
        "open_source_ref": "KCNA state media; 38 North analysis; SWF tracking data",
    },
    {
        "name": "Sanum-dong Research & Development Facility",
        "lat": 39.04,
        "lng": 125.74,
        "country": "DPRK",
        "type": TYPE_MULTI,
        "status": STATUS_ACTIVE,
        "description": (
            "Key missile and SLV R&D and assembly facility in Pyongyang. ICBMs and "
            "SLVs assembled here before transport to launch sites. Visible in "
            "commercial imagery: large assembly buildings, transporter-erector vehicles."
        ),
        "open_source_ref": "38 North; CSIS Beyond Parallel; commercial imagery",
    },
    {
        "name": "Pongdong-ni Radar/Tracking Station",
        "lat": 39.90,
        "lng": 124.50,
        "country": "DPRK",
        "type": TYPE_RADAR,
        "status": STATUS_SUSPECTED,
        "description": (
            "Suspected tracking radar facility near Sohae. Likely provides launch "
            "telemetry and tracking for SLV launches. Multiple radar dishes visible "
            "in commercial imagery."
        ),
        "open_source_ref": "38 North imagery analysis; OSINT estimates",
    },
]

# ---------------------------------------------------------------------------
# Iran Ground Stations & Facilities
# ---------------------------------------------------------------------------

_IRAN_STATIONS: List[dict] = [
    {
        "name": "Semnan Space Centre (Imam Khomeini Spaceport)",
        "lat": 35.23,
        "lng": 53.92,
        "country": "Iran",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "Primary Iranian civilian space launch site ~230km east of Tehran. "
            "Operated by the Iranian Space Agency (ISA). Supports Simorgh and Safir "
            "SLV launches. Features launch pad, propellant storage, and assembly "
            "facilities. Multiple successful and failed orbital attempts from this site."
        ),
        "open_source_ref": "ISA public releases; commercial satellite imagery (Maxar/Planet); CSIS Missile Threat",
    },
    {
        "name": "Shahrud Missile & Space Test Site",
        "lat": 36.42,
        "lng": 55.32,
        "country": "Iran",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "IRGC Aerospace Force operated facility near Shahrud. Used for Qased SLV "
            "launches (successfully orbited Noor-1 in April 2020). Features mobile "
            "launch infrastructure, allowing rapid-response orbital delivery. Also used "
            "for ballistic missile testing. Separate from ISA civilian program."
        ),
        "open_source_ref": "IRGC announcements; Middlebury MIIS analysis; Planet Labs imagery; CSIS reports",
    },
    {
        "name": "Imam Khomeini Space Centre (New Site)",
        "lat": 35.30,
        "lng": 52.05,
        "country": "Iran",
        "type": TYPE_LAUNCH,
        "status": STATUS_UNDER_CONSTRUCTION,
        "description": (
            "Reported new space launch facility under development. Assessed to support "
            "larger SLVs including potential Simorgh successors. Limited open-source "
            "confirmation of operational status."
        ),
        "open_source_ref": "Iranian state media reports; OSINT satellite imagery analysis",
    },
    {
        "name": "Tabriz Space Tracking Station",
        "lat": 38.08,
        "lng": 46.30,
        "country": "Iran",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Ground station in northwest Iran providing TT&C support for Noor and "
            "other Iranian satellites. Part of the distributed Iranian ground network. "
            "Features tracking antennas visible in commercial imagery."
        ),
        "open_source_ref": "Iranian state media; academic publications from University of Tabriz",
    },
    {
        "name": "Mahdasht Ground Station",
        "lat": 35.72,
        "lng": 50.83,
        "country": "Iran",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Satellite ground station west of Tehran. Multiple dish antennas for "
            "satellite communication and TT&C. Supports both civilian and military "
            "satellite operations."
        ),
        "open_source_ref": "Commercial satellite imagery; Iranian space program documentation",
    },
    {
        "name": "Chabahar Space Tracking Station",
        "lat": 25.30,
        "lng": 60.64,
        "country": "Iran",
        "type": TYPE_TTC,
        "status": STATUS_SUSPECTED,
        "description": (
            "Reported southern tracking station in Sistan-Baluchestan province. "
            "Would provide coverage for satellites in equatorial and southern orbits. "
            "Limited open-source confirmation."
        ),
        "open_source_ref": "Iranian academic publications; OSINT estimates",
    },
]

# ---------------------------------------------------------------------------
# FVEY Ground Stations & Facilities
# ---------------------------------------------------------------------------

_FVEY_STATIONS: List[dict] = [
    # --- United States ---
    {
        "name": "Vandenberg Space Force Base",
        "lat": 34.74,
        "lng": -120.57,
        "country": "US",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "West coast launch facility for polar/SSO missions. Supports SpaceX Falcon 9, "
            "Delta IV Heavy (retired), Atlas V, and future Vulcan launches. Also hosts "
            "4th Space Launch Squadron and ICBM test launch facilities. Critical for "
            "NRO ISR satellite deployment."
        ),
        "open_source_ref": "USSF public affairs; SpaceX manifest; launch databases",
    },
    {
        "name": "Cape Canaveral Space Force Station / Kennedy Space Center",
        "lat": 28.49,
        "lng": -80.58,
        "country": "US",
        "type": TYPE_LAUNCH,
        "status": STATUS_ACTIVE,
        "description": (
            "Primary US launch complex on the east coast. Multiple active pads "
            "(SLC-40, SLC-41, LC-39A/B). Supports SpaceX, ULA, Blue Origin, and "
            "Rocket Lab. Highest launch cadence facility globally."
        ),
        "open_source_ref": "USSF/NASA public records; launch manifest databases",
    },
    {
        "name": "Buckley Space Force Base (SBIRS Ground Station)",
        "lat": 39.72,
        "lng": -104.75,
        "country": "US",
        "type": TYPE_C2,
        "status": STATUS_ACTIVE,
        "description": (
            "Home of the SBIRS (Space-Based Infrared System) Mission Control Station. "
            "Processes missile early warning data from SBIRS GEO and HEO sensors. "
            "Also hosts intelligence ground processing for NRO and NGA."
        ),
        "open_source_ref": "USSF fact sheets; DoD budget documents; Congressional Research Service",
    },
    {
        "name": "Schriever Space Force Base",
        "lat": 38.80,
        "lng": -104.53,
        "country": "US",
        "type": TYPE_C2,
        "status": STATUS_ACTIVE,
        "description": (
            "Home of the Combined Space Operations Center (CSpOC) and 2nd Space "
            "Operations Squadron (GPS master control). Controls GPS constellation, "
            "provides space domain awareness, and coordinates allied space operations "
            "through the Combined Space Operations (CSpO) initiative."
        ),
        "open_source_ref": "USSF fact sheets; GAO reports; CSpO press releases",
    },
    {
        "name": "Pine Gap (Joint Defence Facility)",
        "lat": -23.80,
        "lng": 133.74,
        "country": "AU",
        "type": TYPE_C2,
        "status": STATUS_ACTIVE,
        "description": (
            "Joint US-Australian intelligence facility near Alice Springs. Ground station "
            "for US SIGINT satellites (Orion/Mentor GEO constellation) and missile early "
            "warning (relay station for SBIRS). One of the most important FVEY space "
            "intelligence ground nodes. Operated by CIA/NRO and ASD."
        ),
        "open_source_ref": "Desmond Ball (ANU) publications; ABC/Reuters reporting; Congressional records",
    },
    {
        "name": "Diego Garcia Ground Station",
        "lat": -7.32,
        "lng": 72.42,
        "country": "US",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Indian Ocean tracking station on British Indian Ocean Territory. Provides "
            "GPS monitoring, SBIRS downlink, and general satellite TT&C. Critical "
            "for Indian Ocean coverage gap. Also supports GEODSS space surveillance "
            "telescope."
        ),
        "open_source_ref": "USSF fact sheets; DoD installations database",
    },
    {
        "name": "Kwajalein Atoll (Ronald Reagan Ballistic Missile Defense Test Site)",
        "lat": 9.40,
        "lng": 167.47,
        "country": "US",
        "type": TYPE_RADAR,
        "status": STATUS_ACTIVE,
        "description": (
            "Pacific missile range instrumentation complex. Hosts ALTAIR and ALCOR "
            "tracking radars, Space Fence prototype, and missile defense test "
            "infrastructure. Provides space surveillance and missile tracking."
        ),
        "open_source_ref": "MDA public reports; SMDC fact sheets; Kwajalein Range fact sheets",
    },
    {
        "name": "Space Fence (Kwajalein Atoll, Marshall Islands)",
        "lat": 9.39,
        "lng": 167.48,
        "country": "US",
        "type": TYPE_SURVEILLANCE,
        "status": STATUS_ACTIVE,
        "description": (
            "S-band ground-based space surveillance radar. Operational since 2020. "
            "Detects, tracks, and catalogs objects as small as 10cm in LEO. "
            "Dramatically expanded US Space Surveillance Network capacity. Can detect "
            "new launches, breakups, and maneuvers. Operated by 20th SPCS."
        ),
        "open_source_ref": "Lockheed Martin press releases; USSF fact sheets; GAO reports",
    },
    {
        "name": "GEODSS — Maui, Hawaii",
        "lat": 20.71,
        "lng": -156.26,
        "country": "US",
        "type": TYPE_SURVEILLANCE,
        "status": STATUS_ACTIVE,
        "description": (
            "Ground-based Electro-Optical Deep Space Surveillance system on Mt. "
            "Haleakala. Tracks objects in deep space (GEO/HEO). One of three GEODSS "
            "sites (with Diego Garcia and Socorro, NM). Also co-located with AMOS "
            "(Advanced Electro-Optical System) 3.67m telescope."
        ),
        "open_source_ref": "USSF Space Surveillance Network documentation; MIT Lincoln Lab",
    },
    {
        "name": "GEODSS — Socorro, New Mexico",
        "lat": 33.82,
        "lng": -106.66,
        "country": "US",
        "type": TYPE_SURVEILLANCE,
        "status": STATUS_ACTIVE,
        "description": (
            "GEODSS site at White Sands Missile Range. Deep-space optical tracking "
            "of GEO/HEO objects. Part of the US Space Surveillance Network."
        ),
        "open_source_ref": "USSF SSN documentation; White Sands public affairs",
    },
    # --- United Kingdom ---
    {
        "name": "RAF Fylingdales",
        "lat": 54.36,
        "lng": -0.67,
        "country": "UK",
        "type": TYPE_RADAR,
        "status": STATUS_ACTIVE,
        "description": (
            "Phased-array BMEWS (Ballistic Missile Early Warning System) radar in "
            "North Yorkshire. Provides missile early warning and space surveillance for "
            "both UK and US. AN/FPS-132 upgrade provides enhanced space tracking. "
            "Managed by RAF with US Space Force integration."
        ),
        "open_source_ref": "UK MOD fact sheets; USSF SSN network documentation; Parliamentary statements",
    },
    {
        "name": "Ascension Island Ground Station",
        "lat": -7.97,
        "lng": -14.40,
        "country": "UK",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Mid-Atlantic tracking station on British Overseas Territory. Hosts GPS "
            "monitoring station, USAF tracking antennas, and ESA ground station. "
            "Critical for Atlantic gap coverage in satellite tracking."
        ),
        "open_source_ref": "UK MOD; ESA ground station network; DoD installations",
    },
    # --- Australia ---
    {
        "name": "Woomera Test Range / RAAF Woomera",
        "lat": -31.16,
        "lng": 136.83,
        "country": "AU",
        "type": TYPE_MULTI,
        "status": STATUS_ACTIVE,
        "description": (
            "Vast test range in South Australia. Hosts space surveillance capabilities "
            "including C-band radar and optical tracking. Also used for missile and "
            "hypersonic vehicle testing. SSA data shared through Five Eyes channels."
        ),
        "open_source_ref": "Australian DoD annual reports; DSTG publications; industry reports",
    },
    {
        "name": "Naval Communication Station Harold E. Holt (NW Cape)",
        "lat": -21.82,
        "lng": 114.17,
        "country": "AU",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Joint US-AU facility at Exmouth, Western Australia. VLF/LF submarine "
            "communications. Also hosts Space Surveillance Telescope (SST) relocated "
            "from White Sands in 2020 — provides southern hemisphere deep-space "
            "optical tracking of GEO objects."
        ),
        "open_source_ref": "Australian DoD; DARPA SST program; relocation announcements",
    },
    # --- Canada ---
    {
        "name": "CFB Cold Lake / NORAD Radar",
        "lat": 54.41,
        "lng": -110.28,
        "country": "CA",
        "type": TYPE_RADAR,
        "status": STATUS_ACTIVE,
        "description": (
            "Canadian Forces Base in Alberta. Part of NORAD radar network. Provides "
            "aerospace warning and space surveillance data. Also hosts CF-18 "
            "interceptor alert force for North American air defense."
        ),
        "open_source_ref": "Canadian DND fact sheets; NORAD public documentation",
    },
    {
        "name": "22 Wing North Bay (NORAD Canadian Region HQ)",
        "lat": 46.36,
        "lng": -79.42,
        "country": "CA",
        "type": TYPE_C2,
        "status": STATUS_ACTIVE,
        "description": (
            "Underground NORAD complex and Canadian NORAD Region headquarters. "
            "Receives and processes space surveillance and missile warning data. "
            "Integrated with US Space Command for space domain awareness."
        ),
        "open_source_ref": "Canadian DND; NORAD public affairs",
    },
    {
        "name": "Sapphire Satellite — Ground Segment (Ottawa/Shirley Bay)",
        "lat": 45.35,
        "lng": -75.81,
        "country": "CA",
        "type": TYPE_SURVEILLANCE,
        "status": STATUS_ACTIVE,
        "description": (
            "Ground control for Canada's Sapphire space surveillance satellite. "
            "Satellite provides optical tracking of objects in deep space (>15,000 km). "
            "Data contributed to US Space Surveillance Network. First dedicated "
            "Canadian military space asset."
        ),
        "open_source_ref": "DND Sapphire project page; USSF SSN partner contributions",
    },
    # --- New Zealand ---
    {
        "name": "Waihopai Station",
        "lat": -41.59,
        "lng": 173.78,
        "country": "NZ",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "GCSB (Government Communications Security Bureau) satellite intelligence "
            "facility near Blenheim. Two radome-enclosed satellite dishes for SIGINT "
            "collection from SATCOM traffic. Part of the Five Eyes ECHELON network. "
            "Intercepts Pacific and Asian satellite communications."
        ),
        "open_source_ref": "Nicky Hager (Secret Power, 1996); GCSB Act documents; NZ media reporting",
    },
    {
        "name": "Awarua Satellite Ground Station",
        "lat": -46.53,
        "lng": 168.38,
        "country": "NZ",
        "type": TYPE_TTC,
        "status": STATUS_ACTIVE,
        "description": (
            "Southern New Zealand ground station providing satellite TT&C and data "
            "downlink services. Used by multiple operators including for earth "
            "observation data reception. Southern latitude provides unique coverage "
            "for polar-orbiting satellites."
        ),
        "open_source_ref": "NZ Space Agency; ground station operator public listings",
    },
]

# ---------------------------------------------------------------------------
# Aggregation & access functions
# ---------------------------------------------------------------------------

_ALL_ADVERSARY = _PRC_STATIONS + _RUSSIA_STATIONS + _DPRK_STATIONS + _IRAN_STATIONS
_ALL_FVEY = _FVEY_STATIONS
_ALL_STATIONS = _ALL_ADVERSARY + _ALL_FVEY

# Country lookup for convenience
_COUNTRY_MAP: Dict[str, List[dict]] = {}
for _s in _ALL_STATIONS:
    _COUNTRY_MAP.setdefault(_s["country"], []).append(_s)


def get_adversary_stations() -> List[dict]:
    """Return all adversary ground stations / space facilities."""
    return list(_ALL_ADVERSARY)


def get_fvey_stations() -> List[dict]:
    """Return all FVEY ground stations / space facilities."""
    return list(_ALL_FVEY)


def get_all_stations() -> List[dict]:
    """Return all stations (adversary + FVEY)."""
    return list(_ALL_STATIONS)


def get_stations_by_country(country: str) -> List[dict]:
    """Return stations for a specific country.

    Args:
        country: e.g. "PRC", "Russia", "DPRK", "Iran", "US", "UK", "AU", "CA", "NZ"
    """
    return list(_COUNTRY_MAP.get(country, []))


def get_stations_summary() -> dict:
    """Return a summary of station counts by country and type."""
    summary: Dict[str, dict] = {}
    for station in _ALL_STATIONS:
        c = station["country"]
        if c not in summary:
            summary[c] = {"total": 0, "by_type": {}, "by_status": {}}
        summary[c]["total"] += 1
        t = station["type"]
        summary[c]["by_type"][t] = summary[c]["by_type"].get(t, 0) + 1
        s = station["status"]
        summary[c]["by_status"][s] = summary[c]["by_status"].get(s, 0) + 1
    return summary
