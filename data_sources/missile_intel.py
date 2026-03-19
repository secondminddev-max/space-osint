"""
Adversary missile, ASAT, and counterspace capability database
All data from publicly available open-source intelligence:
- CSIS Missile Threat Project (missilethreat.csis.org)
- NASIC "Ballistic and Cruise Missile Threat" (2020)
- NASIC "Competing in Space" (2018, 2019)
- Secure World Foundation "Global Counterspace Capabilities" (2023, 2024)
- Congressional Research Service reports
- Defense Intelligence Agency "Challenges to Security in Space" (2022)
- UN Registry of Objects Launched into Outer Space
- Academic publications and news reporting

Classification: UNCLASSIFIED / OPEN SOURCE ONLY
"""
from __future__ import annotations

from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Threat level and type constants
# ---------------------------------------------------------------------------
THREAT_CRITICAL = "critical"
THREAT_HIGH = "high"
THREAT_MEDIUM = "medium"
THREAT_LOW = "low"

TYPE_DA_ASAT = "direct_ascent_asat"
TYPE_CO_ORBITAL = "co_orbital_asat"
TYPE_DEW = "directed_energy_weapon"
TYPE_EW = "electronic_warfare"
TYPE_CYBER = "cyber"
TYPE_DUAL_USE = "dual_use"
TYPE_ICBM_SLV = "icbm_slv"
TYPE_RPO = "rendezvous_proximity_ops"

STATUS_OPERATIONAL = "operational"
STATUS_DEVELOPMENT = "development"
STATUS_TESTED = "tested"
STATUS_SUSPECTED = "suspected"
STATUS_RETIRED = "retired"

# ---------------------------------------------------------------------------
# PRC Counterspace & Missile Capabilities
# ---------------------------------------------------------------------------

_PRC_SYSTEMS: List[dict] = [
    {
        "name": "SC-19 (DN-1)",
        "country": "PRC",
        "type": TYPE_DA_ASAT,
        "status": STATUS_TESTED,
        "max_altitude_km": 865,
        "description": (
            "Kinetic kill vehicle direct-ascent ASAT. On 11 January 2007, PRC destroyed "
            "the decommissioned FY-1C weather satellite (865 km altitude) using a "
            "ground-launched SC-19 missile, creating over 3,500 pieces of trackable debris "
            "(largest single debris-generating event in space history). Based on the "
            "KT-1 solid-fuel missile (derived from DF-21 MRBM). The test demonstrated "
            "capability to threaten any satellite in LEO. Follow-on tests in 2010 and "
            "2013 conducted as 'missile defense tests' (DN-2) at lower altitudes. The "
            "system is assessed as operational but not confirmed deployed."
        ),
        "first_tested": 2007,
        "threat_level": THREAT_CRITICAL,
        "evidence": (
            "FY-1C debris tracked by 18 SDS (formerly JSpOC); USSTRATCOM statements; "
            "PRC MOD acknowledged test; debris cataloged in Space-Track.org; SWF 2023 report"
        ),
    },
    {
        "name": "DN-2 (SC-19 variant / mid-course interceptor)",
        "country": "PRC",
        "type": TYPE_DA_ASAT,
        "status": STATUS_TESTED,
        "max_altitude_km": 30000,
        "description": (
            "Assessed mid-course ballistic missile interceptor with ASAT potential. "
            "Tested in 2013 with a launch reaching altitudes consistent with GEO "
            "engagement capability (~30,000 km apogee). US DoD assessed this as an "
            "ASAT test disguised as missile defense. Based on a larger booster than "
            "SC-19, potentially DF-26 derived. If operationalized, would threaten "
            "GPS, SBIRS, and other MEO/GEO assets."
        ),
        "first_tested": 2013,
        "threat_level": THREAT_CRITICAL,
        "evidence": (
            "US DoD report to Congress on PRC military power (2014, 2023); SWF analysis; "
            "Brian Weeden testimony to Congress; trajectory analysis by hobby trackers"
        ),
    },
    {
        "name": "DN-3 (exoatmospheric kill vehicle)",
        "country": "PRC",
        "type": TYPE_DA_ASAT,
        "status": STATUS_DEVELOPMENT,
        "max_altitude_km": 36000,
        "description": (
            "Reported exoatmospheric kinetic kill vehicle tested in 2018. Assessed "
            "to represent continued development of hit-to-kill technology for both "
            "missile defense and ASAT applications. Limited open-source detail on "
            "specific capabilities. Potentially represents GEO-capable ASAT."
        ),
        "first_tested": 2018,
        "threat_level": THREAT_HIGH,
        "evidence": "US DoD annual report on PRC military (2019); SWF Global Counterspace 2023",
    },
    {
        "name": "SJ-17 (Shijian-17) — Robotic Arm / RPO Satellite",
        "country": "PRC",
        "type": TYPE_CO_ORBITAL,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 36000,
        "description": (
            "GEO satellite launched October 2016 with a robotic arm for on-orbit "
            "servicing technology demonstration. Conducted proximity operations in GEO "
            "and reportedly grappled/moved a defunct PRC satellite. While characterized "
            "as a technology demo, the capability to approach, grapple, and relocate "
            "satellites in GEO represents a dual-use co-orbital ASAT capability. Any "
            "satellite with a robotic arm and RPO capability can potentially disable or "
            "capture adversary GEO satellites."
        ),
        "first_tested": 2016,
        "threat_level": THREAT_HIGH,
        "evidence": (
            "SWF Global Counterspace 2023; observed orbital maneuvers tracked by "
            "ExoAnalytic Solutions; PRC academic papers on robotic servicing"
        ),
    },
    {
        "name": "SJ-21 (Shijian-21) — GEO Towing/Debris Removal",
        "country": "PRC",
        "type": TYPE_CO_ORBITAL,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 36000,
        "description": (
            "Launched October 2021 to GEO, described as a 'space debris mitigation' "
            "technology demonstrator. In January 2022, SJ-21 was observed towing a "
            "defunct BeiDou navigation satellite (Compass-G2) from near-GEO to a "
            "super-synchronous graveyard orbit — the first observed instance of one "
            "satellite actively relocating another in GEO. This demonstrated a "
            "capability to physically move, capture, or deorbit satellites in the "
            "most strategically important orbital regime."
        ),
        "first_tested": 2021,
        "threat_level": THREAT_CRITICAL,
        "evidence": (
            "ExoAnalytic Solutions tracking data presented at space conferences; "
            "SWF Global Counterspace 2023; 18 SDS tracking data; Slingshot Aerospace analysis"
        ),
    },
    {
        "name": "Shijian Series Co-orbital Inspection Microsatellites",
        "country": "PRC",
        "type": TYPE_RPO,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 40000,
        "description": (
            "Multiple Shijian-series small satellites have demonstrated rendezvous and "
            "proximity operations (RPO) in both LEO and GEO. Notable examples: SJ-06F "
            "conducted RPO near other PRC satellites (2008); SJ-12 maneuvered close to "
            "SJ-06F (2010); SJ-15 involved in complex multi-satellite proximity "
            "operations. These demonstrate the building blocks for co-orbital ASAT: "
            "approach, inspect, and potentially interfere with target satellites."
        ),
        "first_tested": 2008,
        "threat_level": THREAT_HIGH,
        "evidence": (
            "Orbital tracking by 18 SDS; Brian Weeden SWF analysis; DoD reports; "
            "hobby satellite trackers; academic analysis of TLE data"
        ),
    },
    {
        "name": "Ground-Based Laser ASAT (Dazzling/Blinding)",
        "country": "PRC",
        "type": TYPE_DEW,
        "status": STATUS_SUSPECTED,
        "max_altitude_km": 1000,
        "description": (
            "PRC assessed to possess ground-based laser systems capable of dazzling or "
            "temporarily blinding electro-optical (EO) imaging satellites in LEO. "
            "Multiple incidents of laser illumination of US satellites reported by DoD "
            "(2006 reports of Chinese laser illumination of a US satellite). PRC has "
            "published extensive academic research on laser atmospheric propagation, "
            "adaptive optics for satellite engagement, and high-power laser development "
            "suggesting a mature R&D program. Permanent high-power laser facilities "
            "identified in satellite imagery."
        ),
        "first_tested": 2006,
        "threat_level": THREAT_HIGH,
        "evidence": (
            "DoD reports to Congress; NASIC Competing in Space; DIA Challenges to Security "
            "in Space 2022; PRC academic laser publications (Harbin Institute of Technology); "
            "SWF Global Counterspace 2023"
        ),
    },
    {
        "name": "GPS/SATCOM Jamming Systems",
        "country": "PRC",
        "type": TYPE_EW,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": None,
        "description": (
            "PRC has developed and deployed multiple ground-based and mobile electronic "
            "warfare systems capable of jamming GPS signals and SATCOM links. Assessed "
            "capabilities include: uplink jamming of SATCOM transponders, GPS spoofing "
            "in regional areas, and targeted jamming of specific satellite downlinks. "
            "PLA Strategic Support Force (now ISF) operates dedicated space electronic "
            "warfare units. Commercial GPS jamming detected around South China Sea "
            "military installations."
        ),
        "first_tested": 2000,
        "threat_level": THREAT_HIGH,
        "evidence": (
            "DIA Challenges to Security in Space; NASIC Competing in Space; C4ADS "
            "report on GPS spoofing; SWF Global Counterspace; DOT&E testing reports"
        ),
    },
    {
        "name": "CZ (Long March) SLV Series — Dual-Use Orbital Capability",
        "country": "PRC",
        "type": TYPE_DUAL_USE,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": None,
        "description": (
            "PRC's Long March family of SLVs provides the booster technology for any "
            "future DA-ASAT or FOBS (Fractional Orbital Bombardment System) capability. "
            "The July 2021 test of a hypersonic glide vehicle launched by a Long March "
            "into a fractional orbital trajectory demonstrated potential FOBS capability. "
            "CZ-11 solid-fuel SLV launched from mobile TEL provides rapid-response "
            "orbital access. CZ-6 supports responsive military satellite deployment."
        ),
        "first_tested": 1970,
        "threat_level": THREAT_MEDIUM,
        "evidence": (
            "FT reporting on 2021 HGV/FOBS test; DoD annual PRC military power report; "
            "public launch records; Congressional testimony"
        ),
    },
    {
        "name": "Satellite Communication Uplink Jamming (Counter-SATCOM)",
        "country": "PRC",
        "type": TYPE_EW,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": None,
        "description": (
            "Dedicated uplink jamming systems targeting adversary military SATCOM. "
            "Can degrade or deny satellite communications by transmitting interference "
            "toward GEO SATCOM transponders. Assessed capability against military "
            "UHF, SHF, and EHF bands. Mobile and fixed installations identified."
        ),
        "first_tested": 2005,
        "threat_level": THREAT_HIGH,
        "evidence": (
            "NASIC Competing in Space; DIA 2022 report; SWF counterspace assessment; "
            "DoD EW threat briefings (unclass)"
        ),
    },
    {
        "name": "Cyber Operations Against Space Systems",
        "country": "PRC",
        "type": TYPE_CYBER,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": None,
        "description": (
            "PRC cyber units have demonstrated capability and intent to target space "
            "system ground segments. Documented incidents include: intrusions into "
            "satellite operator networks, compromise of satellite ground control systems, "
            "and theft of satellite design data. APT groups linked to PRC (APT1/Unit "
            "61398, APT10, APT41) have targeted aerospace companies and satellite operators. "
            "Ground segment cyber attack can achieve effects equivalent to a physical "
            "ASAT without generating debris."
        ),
        "first_tested": 2007,
        "threat_level": THREAT_HIGH,
        "evidence": (
            "Mandiant APT1 report (2013); CISA advisories; DoD cyber threat assessments; "
            "Symantec Thrip group report (targeting satellite operators); DIA 2022 report"
        ),
    },
]

# ---------------------------------------------------------------------------
# Russia Counterspace & Missile Capabilities
# ---------------------------------------------------------------------------

_RUSSIA_SYSTEMS: List[dict] = [
    {
        "name": "Nudol (PL-19 / A-235)",
        "country": "Russia",
        "type": TYPE_DA_ASAT,
        "status": STATUS_TESTED,
        "max_altitude_km": 800,
        "description": (
            "Ground-launched direct-ascent ASAT missile based at Plesetsk Cosmodrome. "
            "Tested at least 10 times since 2014 (multiple failures and successes). "
            "Part of the A-235 missile defense system replacing the legacy A-135 Moscow "
            "ABM system. Dual-capable: both ballistic missile interceptor and LEO ASAT. "
            "Mobile TEL-based, potentially deployable beyond Plesetsk. Confirmed capable "
            "of engaging satellites in LEO based on trajectory analysis of tests."
        ),
        "first_tested": 2014,
        "threat_level": THREAT_CRITICAL,
        "evidence": (
            "US State Department statements; USSF tracking of tests; SWF analysis; "
            "Russian MOD partial acknowledgments; hobby trackers trajectory reconstruction"
        ),
    },
    {
        "name": "DA-ASAT (Cosmos 1408 Destruction — November 2021)",
        "country": "Russia",
        "type": TYPE_DA_ASAT,
        "status": STATUS_TESTED,
        "max_altitude_km": 485,
        "description": (
            "On 15 November 2021, Russia conducted a kinetic ASAT test destroying "
            "Cosmos 1408 (a defunct ELINT satellite, ~485 km altitude) using a "
            "ground-launched interceptor (likely Nudol variant). Created 1,500+ pieces "
            "of trackable debris, threatening the ISS and forcing crew to shelter. "
            "Debris field spread across LEO, endangering hundreds of operational "
            "satellites. Universally condemned including by FVEY nations. Demonstrated "
            "continued Russian ASAT capability and willingness to test."
        ),
        "first_tested": 2021,
        "threat_level": THREAT_CRITICAL,
        "evidence": (
            "USSPACECOM statement 15 Nov 2021; State Dept condemnation; LeoLabs tracking; "
            "ISS crew shelter-in-place confirmed by NASA; 18 SDS debris catalog entries"
        ),
    },
    {
        "name": "Cosmos 2542 / 2543 — Inspector/Sub-Satellite RPO",
        "country": "Russia",
        "type": TYPE_CO_ORBITAL,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 800,
        "description": (
            "Cosmos 2542 launched November 2019 maneuvered to within ~160 km of USA 245, "
            "a classified NRO satellite, in January 2020. Cosmos 2542 then released a "
            "sub-satellite (Cosmos 2543) which conducted proximity operations. In July "
            "2020, Cosmos 2543 released a projectile in orbit — assessed as a test of "
            "a co-orbital ASAT weapons delivery mechanism. This sequence demonstrated: "
            "adversary satellite inspection, sub-satellite deployment, and weapons "
            "release in orbit."
        ),
        "first_tested": 2019,
        "threat_level": THREAT_CRITICAL,
        "evidence": (
            "Gen. John Raymond (CSpOC Commander) statement Feb 2020; Time magazine reporting; "
            "18 SDS TLE tracking data showing maneuvers; SWF Global Counterspace 2023"
        ),
    },
    {
        "name": "Cosmos 2558 — Inspector Satellite",
        "country": "Russia",
        "type": TYPE_CO_ORBITAL,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 800,
        "description": (
            "Launched August 2022 into an orbit closely matching that of USA 326, a "
            "classified US satellite launched just weeks prior. Cosmos 2558 was assessed "
            "to be conducting intelligence-gathering proximity operations against the "
            "US satellite. Follows the established pattern of Russian inspector satellite "
            "missions (Cosmos 2519/2521/2523 series, Cosmos 2542/2543 series)."
        ),
        "first_tested": 2022,
        "threat_level": THREAT_HIGH,
        "evidence": (
            "USSPACECOM tracking; Slingshot Aerospace analysis; SWF Global Counterspace 2024; "
            "orbital analysis by independent trackers"
        ),
    },
    {
        "name": "IS (Istrebitel Sputnikov) — Legacy Co-Orbital ASAT",
        "country": "Russia",
        "type": TYPE_CO_ORBITAL,
        "status": STATUS_RETIRED,
        "max_altitude_km": 2000,
        "description": (
            "Soviet-era co-orbital ASAT system tested from 1963-1982. Interceptor "
            "satellite launched to match orbit of target, then detonated a fragmentation "
            "warhead. System was declared operational in 1973. Retired but the technology "
            "lineage continues in modern Cosmos inspector satellite programs. Demonstrated "
            "the Soviet/Russian tradition of co-orbital ASAT development."
        ),
        "first_tested": 1963,
        "threat_level": THREAT_LOW,
        "evidence": (
            "Soviet/Russian government historical records; Laura Grego Union of Concerned "
            "Scientists analysis; SWF historical counterspace timeline"
        ),
    },
    {
        "name": "Peresvet — Ground-Based Laser ASAT",
        "country": "Russia",
        "type": TYPE_DEW,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 1500,
        "description": (
            "Mobile ground-based laser system announced by President Putin in March 2018. "
            "Declared operational with Russian Strategic Rocket Forces (RVSN) in December "
            "2018. Assessed to be deployed at ICBM base locations to dazzle/blind "
            "adversary imaging satellites during ICBM operations (prevent real-time ISR "
            "of launch preparations). Named after medieval Russian warrior-monk Alexander "
            "Peresvet. Likely uses chemical or fiber laser technology. Exact power and "
            "engagement altitude classified but assessed effective against LEO EO satellites."
        ),
        "first_tested": 2017,
        "threat_level": THREAT_HIGH,
        "evidence": (
            "Putin March 2018 address; Russian MOD video/imagery; RVSN deployment statements; "
            "SWF Global Counterspace 2023; DIA Challenges to Security in Space 2022"
        ),
    },
    {
        "name": "Tirada-2 — Satellite Communications Jammer",
        "country": "Russia",
        "type": TYPE_EW,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": None,
        "description": (
            "Dedicated ground-based SATCOM jamming system. Designed to jam adversary "
            "military satellite communications across multiple frequency bands. Reported "
            "operational since ~2018. Targets communication satellites in GEO by "
            "transmitting interference toward transponder receive antennas. Can disrupt "
            "both military (MILSATCOM) and commercial SATCOM used by military forces."
        ),
        "first_tested": 2018,
        "threat_level": THREAT_HIGH,
        "evidence": (
            "Russian defense industry media (Izvestia); SWF Global Counterspace; "
            "Bart Hendrickx analysis; DIA 2022 report"
        ),
    },
    {
        "name": "Tobol — Counter-Space Electronic Warfare System",
        "country": "Russia",
        "type": TYPE_EW,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": None,
        "description": (
            "Ground-based electronic warfare system reportedly capable of jamming or "
            "spoofing adversary satellite signals. Assessed deployed at multiple Russian "
            "military installations. Limited open-source detail but reported by Russian "
            "defense media as operational with Aerospace Forces. May target GPS/GLONASS "
            "spoofing of adversary receivers or direct satellite uplink interference."
        ),
        "first_tested": 2019,
        "threat_level": THREAT_MEDIUM,
        "evidence": (
            "Russian defense media; Bart Hendrickx (The Space Review); "
            "SWF Global Counterspace 2023"
        ),
    },
    {
        "name": "S-500 Prometey — High-Altitude Interceptor",
        "country": "Russia",
        "type": TYPE_DUAL_USE,
        "status": STATUS_DEVELOPMENT,
        "max_altitude_km": 200,
        "description": (
            "Advanced long-range air and missile defense system. Claimed capable of "
            "engaging targets at altitudes up to ~200 km, which would give it limited "
            "LEO ASAT capability against very low satellites. Uses 77N6 series "
            "interceptors. Initial deliveries to Russian Aerospace Forces reported in "
            "2021-2022. While primarily a missile defense system, the engagement "
            "altitude overlaps with lowest LEO satellites."
        ),
        "first_tested": 2018,
        "threat_level": THREAT_MEDIUM,
        "evidence": (
            "Russian MOD announcements; Almaz-Antey marketing materials; "
            "NASIC Missile Threat assessments; open-source analysis"
        ),
    },
    {
        "name": "GPS Jamming / Spoofing (Operational Use)",
        "country": "Russia",
        "type": TYPE_EW,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": None,
        "description": (
            "Russia routinely conducts GPS jamming and spoofing operations, particularly "
            "in conflict zones. Documented GPS interference: eastern Mediterranean "
            "(Syria operations, affecting commercial aviation), Ukraine (extensive GPS "
            "warfare), Crimea/Black Sea region, Baltic region during exercises, and "
            "around Putin's known locations. Systems include R-330Zh Zhitel and other "
            "EW platforms. Demonstrated ability to spoof GPS signals, creating false "
            "position data for GPS receivers over wide areas."
        ),
        "first_tested": 2014,
        "threat_level": THREAT_HIGH,
        "evidence": (
            "C4ADS 'Above Us Only Stars' report (2019); EUROCONTROL GPS interference "
            "reports; NATO STRATCOM reporting; US DoD GPS interference bulletins"
        ),
    },
    {
        "name": "Burevestnik / Space EW Units",
        "country": "Russia",
        "type": TYPE_EW,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": None,
        "description": (
            "Russian Aerospace Forces operate dedicated space electronic warfare units "
            "equipped with multiple EW systems targeting satellite communications and "
            "navigation. The 15th Aerospace Army includes units specifically tasked "
            "with counter-space electronic warfare. Systems reportedly include both "
            "uplink jammers and ground-based signal spoofing capabilities."
        ),
        "first_tested": 2015,
        "threat_level": THREAT_MEDIUM,
        "evidence": (
            "Russian MOD organizational charts; Bart Hendrickx order-of-battle analysis; "
            "DIA Challenges to Security in Space"
        ),
    },
    {
        "name": "Cyber Operations Against Space Infrastructure",
        "country": "Russia",
        "type": TYPE_CYBER,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": None,
        "description": (
            "Russian cyber units (GRU, SVR, FSB) have targeted satellite ground "
            "infrastructure. Notable: the February 2022 cyberattack on Viasat's KA-SAT "
            "network at the start of the Ukraine invasion disabled tens of thousands of "
            "terminals across Europe and disrupted Ukrainian military communications. "
            "Attributed to GRU (Sandworm/Unit 74455). This was the most significant "
            "publicly known cyberattack against a satellite operator."
        ),
        "first_tested": 2022,
        "threat_level": THREAT_CRITICAL,
        "evidence": (
            "NSA/CISA/FBI joint advisory (May 2022); Viasat incident report; "
            "EU/UK/US attribution to Russia; SentinelOne analysis of AcidRain wiper malware"
        ),
    },
]

# ---------------------------------------------------------------------------
# DPRK Counterspace & Missile Capabilities
# ---------------------------------------------------------------------------

_DPRK_SYSTEMS: List[dict] = [
    {
        "name": "Hwasong-15 ICBM",
        "country": "DPRK",
        "type": TYPE_ICBM_SLV,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 4500,
        "description": (
            "Two-stage liquid-fueled ICBM. Tested on lofted trajectory in November 2017, "
            "reaching ~4,475 km altitude. Assessed range of 13,000+ km (all of CONUS). "
            "While not an ASAT weapon, the demonstrated altitude and kinetic energy "
            "provide a latent ASAT capability against LEO satellites if equipped with "
            "appropriate guidance. KKV development would be required."
        ),
        "first_tested": 2017,
        "threat_level": THREAT_MEDIUM,
        "evidence": (
            "CSIS Missile Threat; Japanese MOD tracking data; USSTRATCOM statements; "
            "NASIC Ballistic and Cruise Missile Threat 2020"
        ),
    },
    {
        "name": "Hwasong-17 ICBM",
        "country": "DPRK",
        "type": TYPE_ICBM_SLV,
        "status": STATUS_TESTED,
        "max_altitude_km": 6000,
        "description": (
            "Largest DPRK ICBM. Tested March 2022 on lofted trajectory reaching ~6,248 km "
            "altitude — the highest altitude ever achieved by a North Korean missile. "
            "Potentially capable of carrying multiple warheads. The extreme altitude "
            "reached demonstrates a theoretical capability to reach MEO altitudes with "
            "lighter payloads, though no ASAT guidance capability has been demonstrated."
        ),
        "first_tested": 2022,
        "threat_level": THREAT_MEDIUM,
        "evidence": (
            "Japanese MOD tracking; CSIS Missile Threat; NIS ROK assessments; "
            "KCNA imagery analysis"
        ),
    },
    {
        "name": "Unha-3 / Kwangmyongsong SLV",
        "country": "DPRK",
        "type": TYPE_ICBM_SLV,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 500,
        "description": (
            "Three-stage SLV that successfully orbited Kwangmyongsong-3 Unit 2 satellite "
            "in December 2012 (first and only successful DPRK orbital launch at that time). "
            "Demonstrates orbital mechanics knowledge and booster technology applicable to "
            "ICBM and potentially ASAT development. The satellite itself was assessed as "
            "tumbling and non-functional."
        ),
        "first_tested": 2012,
        "threat_level": THREAT_LOW,
        "evidence": (
            "18 SDS orbital tracking; CSIS Missile Threat; USSTRATCOM confirmation of orbit; "
            "amateur radio observations"
        ),
    },
    {
        "name": "Chollima-1 SLV / Malligyong-1 Reconnaissance Satellite",
        "country": "DPRK",
        "type": TYPE_ICBM_SLV,
        "status": STATUS_TESTED,
        "max_altitude_km": 500,
        "description": (
            "New SLV that successfully placed the Malligyong-1 ISR satellite into orbit "
            "on its third attempt in November 2023, with reported assistance from Russian "
            "technical advisors. The satellite was assessed to be providing limited-quality "
            "imagery to DPRK leadership. Represents a significant step in DPRK space "
            "capabilities and demonstrates continued ICBM/SLV technology maturation."
        ),
        "first_tested": 2023,
        "threat_level": THREAT_MEDIUM,
        "evidence": (
            "ROK JCS tracking; 18 SDS catalog entry; KCNA announcements; Japanese MOD; "
            "analysis by 38 North; US/ROK/Japan joint assessment of Russian technical aid"
        ),
    },
    {
        "name": "GPS Jamming Systems",
        "country": "DPRK",
        "type": TYPE_EW,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": None,
        "description": (
            "DPRK has conducted multiple GPS jamming operations targeting South Korea. "
            "Major incidents: 2010 (disrupted GPS for ~10 days, affected 1,000+ aircraft), "
            "2011, 2012 (affected 1,016 aircraft and 254 ships), and 2016. Jammers "
            "located near the DMZ can disrupt GPS signals across the Seoul metropolitan "
            "area. While limited compared to PRC/Russia EW capabilities, demonstrates "
            "intent and basic capability."
        ),
        "first_tested": 2010,
        "threat_level": THREAT_LOW,
        "evidence": (
            "ROK MOD statements; ICAO reports on GPS interference; "
            "C4ADS analysis; news reporting"
        ),
    },
]

# ---------------------------------------------------------------------------
# Iran Counterspace & Missile Capabilities
# ---------------------------------------------------------------------------

_IRAN_SYSTEMS: List[dict] = [
    {
        "name": "Simorgh SLV",
        "country": "Iran",
        "type": TYPE_ICBM_SLV,
        "status": STATUS_TESTED,
        "max_altitude_km": 500,
        "description": (
            "Two-stage liquid-fueled SLV derived from Shahab/Safir lineage but larger. "
            "Multiple launch attempts, mostly failed. Assessed capable of placing a "
            "small payload (~250 kg) into LEO. Development demonstrates Iran's continued "
            "pursuit of orbital capability and mastery of larger liquid-fuel engines. "
            "Could theoretically be adapted for ICBM role but currently assessed as "
            "unreliable."
        ),
        "first_tested": 2017,
        "threat_level": THREAT_LOW,
        "evidence": (
            "ISA announcements; CSIS Missile Threat; satellite imagery of Semnan launch "
            "facility; IAEA reporting; Congressional Research Service"
        ),
    },
    {
        "name": "Qased SLV (IRGC)",
        "country": "Iran",
        "type": TYPE_ICBM_SLV,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 425,
        "description": (
            "Three-stage SLV using solid-fuel first stage (derived from Ghadr MRBM). "
            "Operated by IRGC Aerospace Force (separate from ISA civilian program). "
            "Successfully orbited Noor-1 satellite in April 2020 and Noor-2 in March "
            "2022. Significant because: solid-fuel first stage allows rapid launch "
            "preparation (military-relevant), IRGC operation indicates military space "
            "program, and successful orbit demonstrates growing competence. "
            "Mobile launch platform observed at Shahrud site."
        ),
        "first_tested": 2020,
        "threat_level": THREAT_MEDIUM,
        "evidence": (
            "IRGC press releases; CSIS Missile Threat; satellite imagery analysis; "
            "18 SDS catalog entry for Noor-1/2; SWF Global Counterspace"
        ),
    },
    {
        "name": "Noor Military Satellite Series (IRGC)",
        "country": "Iran",
        "type": TYPE_DUAL_USE,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 425,
        "description": (
            "IRGC-operated military satellite series. Noor-1 (April 2020, ~425 km) "
            "was Iran's first military satellite. Noor-2 (March 2022) followed. "
            "Assessed as low-resolution imaging or signals intelligence platforms. "
            "While individually limited, they represent Iran establishing an indigenous "
            "military space capability. Future iterations likely to have improved sensors."
        ),
        "first_tested": 2020,
        "threat_level": THREAT_LOW,
        "evidence": (
            "IRGC announcements; 18 SDS tracking; amateur radio intercepts; "
            "SWF Global Counterspace 2023"
        ),
    },
    {
        "name": "GPS Spoofing Capability",
        "country": "Iran",
        "type": TYPE_EW,
        "status": STATUS_SUSPECTED,
        "max_altitude_km": None,
        "description": (
            "Iran claimed credit for GPS spoofing that forced the landing of a US "
            "RQ-170 Sentinel stealth drone in December 2011. While the exact mechanism "
            "is debated (may have been a crash with Iranian recovery, not spoofing), "
            "Iran has invested in electronic warfare capabilities including GPS "
            "jamming/spoofing. Multiple incidents of GPS interference reported in the "
            "Persian Gulf region. IRGC operates dedicated EW units."
        ),
        "first_tested": 2011,
        "threat_level": THREAT_LOW,
        "evidence": (
            "Iranian state media claims; DoD RQ-170 loss (Dec 2011); "
            "GPS interference reports (MARAD advisories, Persian Gulf); "
            "academic analysis of spoofing feasibility"
        ),
    },
    {
        "name": "Shahab-3 / Ghadr / Emad MRBM",
        "country": "Iran",
        "type": TYPE_ICBM_SLV,
        "status": STATUS_OPERATIONAL,
        "max_altitude_km": 600,
        "description": (
            "Medium-range ballistic missile family with ranges of 1,000-2,000 km. "
            "Not space weapons but the technology provides the foundation for SLV "
            "development (Safir/Qased use Shahab derivatives). Ghadr variant has "
            "improved guidance. Emad has maneuverable reentry vehicle. Demonstrates "
            "the missile technology base supporting Iran's space ambitions."
        ),
        "first_tested": 1998,
        "threat_level": THREAT_LOW,
        "evidence": (
            "CSIS Missile Threat; NASIC Ballistic and Cruise Missile Threat 2020; "
            "UNSCR 2231 monitoring reports"
        ),
    },
]

# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

_ALL_SYSTEMS = _PRC_SYSTEMS + _RUSSIA_SYSTEMS + _DPRK_SYSTEMS + _IRAN_SYSTEMS

_BY_COUNTRY: Dict[str, List[dict]] = {}
for _sys in _ALL_SYSTEMS:
    _BY_COUNTRY.setdefault(_sys["country"], []).append(_sys)

_BY_THREAT: Dict[str, List[dict]] = {}
for _sys in _ALL_SYSTEMS:
    _BY_THREAT.setdefault(_sys["threat_level"], []).append(_sys)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_missile_asat_data() -> List[dict]:
    """Return all adversary missile, ASAT, and counterspace capabilities."""
    return list(_ALL_SYSTEMS)


def get_by_country(country: str) -> List[dict]:
    """Return systems for a specific country.

    Args:
        country: "PRC", "Russia", "DPRK", or "Iran"
    """
    return list(_BY_COUNTRY.get(country, []))


def get_by_threat_level(level: str) -> List[dict]:
    """Return systems at a given threat level.

    Args:
        level: "critical", "high", "medium", or "low"
    """
    return list(_BY_THREAT.get(level, []))


def get_by_type(system_type: str) -> List[dict]:
    """Return systems of a given type.

    Args:
        system_type: e.g. "direct_ascent_asat", "co_orbital_asat",
                     "directed_energy_weapon", "electronic_warfare", etc.
    """
    return [s for s in _ALL_SYSTEMS if s["type"] == system_type]


def get_threat_summary() -> dict:
    """Return a summary of counterspace threats across all adversaries."""
    summary: Dict[str, dict] = {}
    for country in ("PRC", "Russia", "DPRK", "Iran"):
        systems = _BY_COUNTRY.get(country, [])
        summary[country] = {
            "total_systems": len(systems),
            "by_type": {},
            "by_threat_level": {},
            "critical_systems": [s["name"] for s in systems if s["threat_level"] == THREAT_CRITICAL],
            "has_da_asat": any(s["type"] == TYPE_DA_ASAT for s in systems),
            "has_co_orbital": any(s["type"] in (TYPE_CO_ORBITAL, TYPE_RPO) for s in systems),
            "has_dew": any(s["type"] == TYPE_DEW for s in systems),
            "has_ew": any(s["type"] == TYPE_EW for s in systems),
            "has_cyber": any(s["type"] == TYPE_CYBER for s in systems),
        }
        for s in systems:
            t = s["type"]
            summary[country]["by_type"][t] = summary[country]["by_type"].get(t, 0) + 1
            tl = s["threat_level"]
            summary[country]["by_threat_level"][tl] = (
                summary[country]["by_threat_level"].get(tl, 0) + 1
            )
    return summary
