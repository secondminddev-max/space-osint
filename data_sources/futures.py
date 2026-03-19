"""
Future Space Program Database — All Nations
Structured intelligence database of announced, planned, and projected space programs
across adversary and FVEY/allied nations. Compiled from public government announcements,
white papers, budget documents, congressional testimony, and open-source analysis.

Sources:
- PRC State Council space white papers (2016, 2022)
- Roscosmos Federal Space Program documents
- US DoD budget justification documents
- Congressional Research Service reports
- UK MOD Defence Command Paper
- Australian Defence Strategic Review / Integrated Investment Program
- JAXA/JMOD published roadmaps
- KARI/DAPA announcements
- NASIC "Competing in Space" (2018, 2019)
- DIA "Challenges to Security in Space" (2022)
- CSIS Aerospace Security Project analysis
- Secure World Foundation reports

Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Status and domain constants
# ---------------------------------------------------------------------------
STATUS_ANNOUNCED = "announced"
STATUS_DEVELOPMENT = "development"
STATUS_TESTING = "testing"
STATUS_OPERATIONAL = "operational"
STATUS_DELAYED = "delayed"
STATUS_CANCELLED = "cancelled"

DOMAIN_ISR = "ISR"
DOMAIN_COMMS = "comms"
DOMAIN_PNT = "PNT"
DOMAIN_LAUNCH = "launch"
DOMAIN_HUMAN = "human_spaceflight"
DOMAIN_LUNAR = "lunar"
DOMAIN_ASAT = "ASAT"
DOMAIN_SDA = "SDA"
DOMAIN_SCIENCE = "science"
DOMAIN_BROADBAND = "broadband"
DOMAIN_SOLAR_POWER = "space_solar_power"

# ---------------------------------------------------------------------------
# PRC Future Plans
# ---------------------------------------------------------------------------

_PRC_FUTURES: List[dict] = [
    {
        "nation": "PRC",
        "program_name": "Tiangong Space Station Expansion",
        "description": (
            "Expansion of the Chinese Space Station (CSS/Tiangong) from three to six modules. "
            "The current T-shaped configuration (Tianhe core + Wentian + Mengtian) will be "
            "augmented with a second Tianhe-class core module and additional experiment modules "
            "to form a cross-shaped or multi-arm configuration. The expanded station will "
            "support 6 crew simultaneously and host larger scientific payloads. A commercial "
            "space station module from CAS Space is also planned for docking."
        ),
        "timeline": "2025-2030",
        "status": STATUS_ANNOUNCED,
        "domain": DOMAIN_HUMAN,
        "strategic_impact": (
            "Establishes PRC as a permanent crewed spacefaring nation independent of ISS. "
            "Enables long-duration microgravity research, technology demonstrations, and "
            "international partnerships outside the Western framework. Dual-use potential "
            "for on-orbit inspection and servicing technology development."
        ),
        "source_reference": "CMSA announcements; PRC State Council Space White Paper 2022; IAC 2023 presentations",
    },
    {
        "nation": "PRC",
        "program_name": "Chang'e-7 Lunar South Pole Mission",
        "description": (
            "Robotic lunar south pole exploration mission comprising an orbiter, lander, rover, "
            "and a mini-flying probe for crater shadow exploration. Will search for water ice "
            "in permanently shadowed regions near the lunar south pole. Includes advanced "
            "remote sensing instruments and in-situ resource detection payloads. Serves as a "
            "precursor to the ILRS."
        ),
        "timeline": "2026",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_LUNAR,
        "strategic_impact": (
            "First PRC mission to the lunar south pole. Water ice confirmation would be a "
            "major strategic asset for future cislunar operations. Establishes PRC presence "
            "at the most strategically valuable region on the Moon ahead of NASA Artemis III "
            "permanent base plans."
        ),
        "source_reference": "CNSA roadmap; Wu Weiren (chief designer) public statements; PRC State Council White Paper 2022",
    },
    {
        "nation": "PRC",
        "program_name": "Chang'e-8 ISRU Technology Test",
        "description": (
            "In-Situ Resource Utilization (ISRU) technology verification mission at the lunar "
            "south pole. Will test regolith processing, 3D printing from lunar materials, and "
            "potential oxygen extraction from lunar soil. Designed as the cornerstone of the "
            "International Lunar Research Station (ILRS) infrastructure. Includes a nuclear "
            "power demonstration."
        ),
        "timeline": "2028",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_LUNAR,
        "strategic_impact": (
            "ISRU capability is the key enabler for permanent lunar presence. Successful "
            "demonstration would reduce the logistics burden of lunar operations dramatically "
            "and establish PRC as a leader in cislunar resource exploitation. Forms the "
            "foundation of the ILRS."
        ),
        "source_reference": "CNSA ILRS roadmap; Wu Weiren IAC 2023 presentation; PRC media reporting",
    },
    {
        "nation": "PRC",
        "program_name": "PRC Crewed Lunar Landing",
        "description": (
            "First crewed lunar landing using a new-generation crewed spacecraft and a dedicated "
            "lunar lander launched on the Long March 10 (CZ-10) heavy-lift rocket. Two CZ-10 "
            "launches required per mission: one for the crewed vehicle, one for the lunar "
            "lander. Crew of 2 astronauts will conduct surface EVA operations."
        ),
        "timeline": "2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_LUNAR,
        "strategic_impact": (
            "PRC would become the second nation to land humans on the Moon. Major prestige and "
            "strategic milestone. Establishes physical human presence at the lunar south pole. "
            "Race with NASA Artemis III creates geopolitical competition for cislunar dominance."
        ),
        "source_reference": "CMSA official announcement 2023; Long March 10 development reports; PRC state media",
    },
    {
        "nation": "PRC",
        "program_name": "International Lunar Research Station (ILRS)",
        "description": (
            "Joint PRC-Russia lunar base concept with participation from Belarus, Pakistan, "
            "South Africa, Azerbaijan, UAE, and others. Phased construction: reconnaissance "
            "(2025-2030), construction (2030-2035), and utilization (2035+). Located at the "
            "lunar south pole. Includes power generation, habitat, communication relay, and "
            "resource processing facilities."
        ),
        "timeline": "2030-2040",
        "status": STATUS_ANNOUNCED,
        "domain": DOMAIN_LUNAR,
        "strategic_impact": (
            "Creates a PRC-led alternative to the US Artemis Accords framework. Establishes "
            "permanent infrastructure on the Moon under PRC-Russia coordination. Attracts "
            "partner nations outside the Western alliance. Could lead to competing lunar "
            "governance frameworks and territorial claims."
        ),
        "source_reference": "CNSA-Roscosmos ILRS MOU (2021); ILRS Guide for Partnership (2023); UNOOSA presentations",
    },
    {
        "nation": "PRC",
        "program_name": "Xuntian Space Telescope (China Space Station Telescope)",
        "description": (
            "2-meter aperture optical/UV space telescope co-orbiting with Tiangong. Field of "
            "view 300x larger than Hubble with comparable resolution. Will survey 17,500 sq "
            "deg (40%% of sky) over 10 years. Can dock with Tiangong for maintenance and "
            "instrument upgrades. Covers 255-1000nm wavelength range."
        ),
        "timeline": "2025-2026",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_SCIENCE,
        "strategic_impact": (
            "Provides PRC with independent deep-space observation capability comparable to "
            "Western space telescopes. Dual-use potential for SSA and deep-space object "
            "characterization. Demonstrates PRC ability to build flagship-class space "
            "science instruments."
        ),
        "source_reference": "NAOC/CAS presentations; PRC Space White Paper 2022; Xuntian science team publications",
    },
    {
        "nation": "PRC",
        "program_name": "Yaogan Constellation Expansion (300+ ISR Satellites)",
        "description": (
            "Massive expansion of the Yaogan/Jilin family of ISR satellites targeting 300+ "
            "operational spacecraft by 2030. Includes SAR, electro-optical, and electronic "
            "intelligence satellites in multiple orbital planes. Recent launches deploying "
            "triplets (SAR + EO + ELINT) suggest rapid constellation buildout. Commercial "
            "companies (Chang Guang Satellite Technology — Jilin-1 series) supplement "
            "military Yaogan systems."
        ),
        "timeline": "2025-2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_ISR,
        "strategic_impact": (
            "Near-persistent ISR coverage of the Indo-Pacific, including Taiwan Strait, "
            "South China Sea, and FVEY military facilities. Dramatically reduces revisit "
            "times from hours to near-real-time. Combined with AI-driven processing, "
            "provides PLA with comprehensive maritime domain awareness. Threatens FVEY "
            "ability to maneuver forces without detection."
        ),
        "source_reference": "Space-Track.org launch data; CSIS Aerospace Security Project; Jilin-1 commercial releases",
    },
    {
        "nation": "PRC",
        "program_name": "BeiDou-3 Enhancement and Maintenance",
        "description": (
            "Ongoing maintenance and enhancement of the 30-satellite BeiDou-3 global "
            "navigation satellite system. Includes replacement satellite launches, signal "
            "modernization (B2a, B1C new signals), and ground segment upgrades. Planning "
            "for BeiDou follow-on generation with improved accuracy and resilience."
        ),
        "timeline": "2025-2035",
        "status": STATUS_OPERATIONAL,
        "domain": DOMAIN_PNT,
        "strategic_impact": (
            "Ensures PRC independence from GPS. BeiDou provides PNT for PLA precision "
            "munitions, naval operations, and military communications timing. Global "
            "service enables PRC to offer PNT to Belt and Road partners, reducing their "
            "GPS dependence and increasing PRC influence."
        ),
        "source_reference": "BeiDou ICD documents; China Satellite Navigation Office; IAC papers",
    },
    {
        "nation": "PRC",
        "program_name": "Long March 9 Super Heavy-Lift Rocket",
        "description": (
            "Super heavy-lift launch vehicle with 150-tonne LEO capacity (comparable to "
            "Saturn V / SLS / Starship). Features reusable first stage with grid fins for "
            "propulsive landing (similar to Falcon 9). Kerolox engines (YF-215) in "
            "development. Will enable crewed lunar missions, large space station modules, "
            "and deep space exploration."
        ),
        "timeline": "2030 (first flight target)",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_LAUNCH,
        "strategic_impact": (
            "Provides PRC with heavy-lift capability matching or exceeding US SLS/Starship. "
            "Enables large-scale cislunar and deep space operations. Reusable design targets "
            "cost reduction for high-cadence operations. Military applications include large "
            "constellation deployment and potential space-based weapons platforms."
        ),
        "source_reference": "CASC presentations; Long Lehao (chief designer) public statements; CZ-9 design papers",
    },
    {
        "nation": "PRC",
        "program_name": "Reusable Launch Vehicle Program (Suborbital/Orbital)",
        "description": (
            "Multiple reusable launch vehicle programs in parallel. Includes: CASC suborbital "
            "reusable first stage tests (vertical takeoff/vertical landing), CAS Space ZK-series "
            "suborbital vehicle tests, and commercial reusable rocket companies (LandSpace, "
            "iSpace, Deep Blue Aerospace, Space Pioneer) developing Falcon 9-class reusable "
            "vehicles. Several successful hop tests completed."
        ),
        "timeline": "2025-2028",
        "status": STATUS_TESTING,
        "domain": DOMAIN_LAUNCH,
        "strategic_impact": (
            "Reusable launch dramatically reduces cost and increases cadence. Enables rapid "
            "constellation replenishment and responsive space operations. Commercial sector "
            "development mirrors early SpaceX trajectory. Military applications for "
            "tactically responsive space launch."
        ),
        "source_reference": "CASC/CAS Space public statements; commercial company announcements; test flight reporting",
    },
    {
        "nation": "PRC",
        "program_name": "Qian Xuesen Lab Advanced Concepts (Space-Based Solar Power)",
        "description": (
            "Advanced research programs at the Qian Xuesen Laboratory of Space Technology "
            "including space-based solar power (SBSP) technology demonstrations. Plans for a "
            "1 MW orbiting solar power station test by 2030 and potential GW-class operational "
            "system by 2050. Also pursuing advanced propulsion (nuclear thermal, electric), "
            "and large space structure assembly."
        ),
        "timeline": "2030-2050",
        "status": STATUS_ANNOUNCED,
        "domain": DOMAIN_SOLAR_POWER,
        "strategic_impact": (
            "SBSP could provide strategic energy independence. Technology for beaming power "
            "from space has dual-use implications for directed energy weapons. Large space "
            "structure assembly capability relevant to future space-based military platforms. "
            "Long-term program but demonstrates PRC strategic vision."
        ),
        "source_reference": "Qian Xuesen Lab publications; CASC presentations at IAC; PRC media reporting on SBSP",
    },
    {
        "nation": "PRC",
        "program_name": "Guowang (SatNet) Mega-Constellation",
        "description": (
            "PRC national broadband mega-constellation of approximately 13,000 LEO satellites "
            "filed with ITU. Operated by China SatNet (state-owned enterprise established "
            "2021). Intended as a state-backed competitor to Starlink. Will provide global "
            "broadband coverage with priority for Belt and Road nations. Production and "
            "deployment ramp-up expected mid-2020s."
        ),
        "timeline": "2025-2035",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_BROADBAND,
        "strategic_impact": (
            "Provides PRC-controlled global communications independent of Western infrastructure. "
            "Military utility for secure global comms, IoT/sensor networks, and redundant "
            "C2 links. Competes with Starlink for orbital slots and spectrum. Could be "
            "offered to nations seeking alternatives to Western satellite internet, extending "
            "PRC digital influence."
        ),
        "source_reference": "ITU filings; China SatNet establishment (2021); PRC State Council documents",
    },
    {
        "nation": "PRC",
        "program_name": "SJ-Series Inspector Satellite Expansion",
        "description": (
            "Continued development and deployment of Shijian-series satellites with RPO, "
            "inspection, and on-orbit servicing/manipulation capabilities. Follows SJ-17 "
            "(GEO RPO, robotic arm) and SJ-21 (GEO towing) demonstrations. Future systems "
            "expected to include more capable robotic systems, refueling capability, and "
            "multi-satellite cooperative operations."
        ),
        "timeline": "2025-2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_ASAT,
        "strategic_impact": (
            "Expanding co-orbital ASAT and space control capability. GEO manipulation "
            "demonstrated by SJ-21 represents a unique and critical threat to FVEY GEO "
            "assets (SBIRS, AEHF, WGS, etc.). Multi-satellite cooperative operations "
            "could overwhelm defensive measures."
        ),
        "source_reference": "SWF Global Counterspace Capabilities 2023; ExoAnalytic tracking; DIA 2022 report",
    },
    {
        "nation": "PRC",
        "program_name": "PRC Space Force Restructuring (Information Support Force)",
        "description": (
            "In April 2024, PRC announced the dissolution of the Strategic Support Force (SSF) "
            "and creation of three new forces: the Information Support Force (ISF), the "
            "Aerospace Force, and the Cyberspace Force. The space domain now falls primarily "
            "under the Aerospace Force with ISF coordination. This restructuring elevates "
            "space as an independent warfighting domain with dedicated command structure."
        ),
        "timeline": "2024-2027",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_SDA,
        "strategic_impact": (
            "Indicates PRC is treating space as a primary warfighting domain requiring "
            "dedicated force structure, similar to the US establishment of Space Force. "
            "Streamlined C2 for space operations. Separation from cyber/EW suggests "
            "maturation of space as an independent military branch."
        ),
        "source_reference": "PRC MOD announcements April 2024; PLA Daily reporting; CSIS analysis",
    },
]

# ---------------------------------------------------------------------------
# Russia Future Plans
# ---------------------------------------------------------------------------

_RUSSIA_FUTURES: List[dict] = [
    {
        "nation": "Russia",
        "program_name": "Sphere Constellation (Sfera)",
        "description": (
            "Ambitious LEO/MEO constellation plan comprising 600+ satellites for broadband "
            "communications, IoT, and earth observation. Includes multiple sub-constellations: "
            "Skif (broadband), Marathon (IoT), Smotr (EO). Repeatedly delayed due to funding "
            "shortfalls and sanctions limiting access to Western electronics. First Skif demo "
            "satellite launched 2022."
        ),
        "timeline": "2028-2035 (repeatedly delayed)",
        "status": STATUS_DELAYED,
        "domain": DOMAIN_BROADBAND,
        "strategic_impact": (
            "Would provide Russia with independent global communications but persistent "
            "delays undermine credibility. Sanctions severely constrain electronics supply. "
            "If completed, provides redundant military comms and ISR. Likely to remain "
            "significantly delayed without Chinese component supply."
        ),
        "source_reference": "Roscosmos Federal Space Program; Russian government decrees; Bart Hendrickx analysis",
    },
    {
        "nation": "Russia",
        "program_name": "Angara-A5 Heavy-Lift Rocket (Proton Replacement)",
        "description": (
            "Modular heavy-lift launch vehicle intended to replace the aging Proton-M for "
            "GTO and interplanetary missions. Launched from both Plesetsk and Vostochny "
            "(pad under construction). First successful GTO-profile test from Vostochny in "
            "April 2024. Uses environmentally cleaner kerolox propellant vs Proton's toxic "
            "UDMH/NTO. 24.5-tonne LEO capacity."
        ),
        "timeline": "2024-2030 (operational ramp-up)",
        "status": STATUS_TESTING,
        "domain": DOMAIN_LAUNCH,
        "strategic_impact": (
            "Essential for Russian military satellite deployment to GTO/GEO. Replaces Proton "
            "which is being retired. Vostochny pad eliminates dependence on Baikonur "
            "(Kazakhstan). Slow ramp-up constrains Russia's ability to replenish "
            "constellations rapidly."
        ),
        "source_reference": "Roscosmos announcements; Vostochny construction imagery; Russian space industry reporting",
    },
    {
        "nation": "Russia",
        "program_name": "Orel (Oryol) Crewed Spacecraft",
        "description": (
            "Next-generation crewed spacecraft intended to replace Soyuz for LEO and lunar "
            "missions. Reusable crew module for up to 6 crew. Originally planned for 2023, "
            "repeatedly delayed. First uncrewed test flight now projected 2028+. Launched "
            "on Angara-A5. Will service ROSS station and potentially ILRS lunar missions."
        ),
        "timeline": "2028+ (significantly delayed)",
        "status": STATUS_DELAYED,
        "domain": DOMAIN_HUMAN,
        "strategic_impact": (
            "Essential for Russian crewed spaceflight independence post-ISS. Persistent "
            "delays indicate deep problems in Russian space industry capacity. Without "
            "Orel, Russia depends on aging Soyuz or PRC cooperation for crew transport."
        ),
        "source_reference": "RSC Energia announcements; Roscosmos program documentation; news reporting",
    },
    {
        "nation": "Russia",
        "program_name": "Luna-26 Orbital Mission",
        "description": (
            "Lunar orbital mission following the failure of Luna-25 (August 2023 crash). "
            "Luna-26 will conduct remote sensing of the lunar surface from orbit, mapping "
            "resources and selecting sites for future missions. Carries Russian and "
            "international instruments."
        ),
        "timeline": "2027-2028",
        "status": STATUS_DELAYED,
        "domain": DOMAIN_LUNAR,
        "strategic_impact": (
            "Attempts to maintain Russian lunar exploration credibility after Luna-25 failure. "
            "Supports ILRS site selection. Post-sanctions technology constraints may cause "
            "further delays or force increased reliance on PRC components."
        ),
        "source_reference": "IKI RAS mission documentation; Roscosmos announcements; post-Luna-25 program review",
    },
    {
        "nation": "Russia",
        "program_name": "Luna-27 Lander (South Pole)",
        "description": (
            "Lunar south pole lander with European-built drill (PROSPECT) for subsurface "
            "sample analysis and water ice detection. ESA participation suspended post-2022 "
            "due to Ukraine invasion. Russia proceeding with indigenous instruments. "
            "Mission redesigned for purely Russian execution."
        ),
        "timeline": "2028-2030",
        "status": STATUS_DELAYED,
        "domain": DOMAIN_LUNAR,
        "strategic_impact": (
            "Loss of ESA cooperation degrades scientific capability. Russia seeking PRC "
            "partnership as alternative. Continued lunar ambitions linked to ILRS "
            "commitment with PRC. Delays widen gap with US Artemis and PRC Chang'e programs."
        ),
        "source_reference": "IKI RAS; ESA suspension announcements (2022); Roscosmos program revisions",
    },
    {
        "nation": "Russia",
        "program_name": "ROSS (Russian Orbital Service Station)",
        "description": (
            "Planned Russian independent orbital station to replace ISS participation (ISS "
            "cooperation extended to 2028 but Russia plans independent capability). Initial "
            "module (NEM-1) to launch 2027+. High-inclination orbit (97 deg) providing "
            "coverage of Russian territory including Arctic. Multiple modules planned for "
            "assembly over 2027-2032."
        ),
        "timeline": "2027-2032",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_HUMAN,
        "strategic_impact": (
            "High-inclination orbit provides persistent observation of Russian Arctic and "
            "northern military infrastructure. Dual-use for military surveillance. "
            "Eliminates dependence on Western ISS partners. But funding and industrial "
            "capacity remain major concerns."
        ),
        "source_reference": "RSC Energia design documents; Roscosmos announcements; Russian government funding approvals",
    },
    {
        "nation": "Russia",
        "program_name": "Nudol / S-550 ASAT System Expansion",
        "description": (
            "Continued development and potential deployment expansion of the A-235 Nudol "
            "direct-ascent ASAT system. The S-550 (reported designation for the mobile ASAT "
            "variant) may be deployed beyond the Plesetsk test site to operational locations. "
            "System demonstrated against Cosmos 1408 in November 2021."
        ),
        "timeline": "2025-2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_ASAT,
        "strategic_impact": (
            "Operational deployment of mobile DA-ASAT beyond test sites would enable Russia "
            "to threaten LEO satellites from dispersed, survivable locations. Combined with "
            "inspector satellites and Peresvet laser, creates layered counterspace capability."
        ),
        "source_reference": "SWF Global Counterspace 2023; Russian MOD statements; DIA 2022 report",
    },
    {
        "nation": "Russia",
        "program_name": "Peresvet Laser System Deployment Expansion",
        "description": (
            "Expansion of the Peresvet ground-based laser ASAT system to additional RVSN "
            "(Strategic Rocket Forces) base locations. Currently assessed deployed at ICBM "
            "bases to deny adversary ISR satellite imaging during launch preparations. "
            "Potential upgrade to higher power levels for permanent blinding capability."
        ),
        "timeline": "2025-2028",
        "status": STATUS_OPERATIONAL,
        "domain": DOMAIN_ASAT,
        "strategic_impact": (
            "Expanded deployment degrades FVEY ability to monitor Russian ICBM activities "
            "from space. Reversible dazzling avoids debris/escalation while providing "
            "tactical advantage. Upgrade to permanent blinding would represent significant "
            "escalation."
        ),
        "source_reference": "Russian MOD; Putin 2018 address; SWF Global Counterspace; DIA report",
    },
    {
        "nation": "Russia",
        "program_name": "Vostochny Cosmodrome Buildout",
        "description": (
            "Continued construction at Vostochny Cosmodrome in the Russian Far East. "
            "Angara-A5 launch pad completed 2024. Future phases include additional pads, "
            "crew launch infrastructure for Orel spacecraft, and potentially super-heavy "
            "launch capability. Intended to replace Baikonur as primary launch site."
        ),
        "timeline": "2024-2035",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_LAUNCH,
        "strategic_impact": (
            "Provides Russian launch independence from Kazakh-hosted Baikonur. Eastern "
            "location enables Pacific-direction launches. Full buildout essential for "
            "Russian space program sovereignty. Chronic construction delays and "
            "corruption scandals have slowed progress."
        ),
        "source_reference": "Russian government construction reports; satellite imagery; news reporting",
    },
    {
        "nation": "Russia",
        "program_name": "PRC-Russia Space Cooperation (ILRS & Beyond)",
        "description": (
            "Deepening space cooperation between Russia and PRC including: ILRS lunar base, "
            "joint lunar missions, potential component supply for Russian satellites "
            "(replacing sanctioned Western parts), launch cooperation, and data sharing. "
            "Post-2022 sanctions accelerated Russia's pivot to PRC space partnership."
        ),
        "timeline": "2024-2040",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_LUNAR,
        "strategic_impact": (
            "Creates an adversary space bloc with shared infrastructure and capabilities. "
            "PRC benefits from Russian heritage expertise in human spaceflight and deep "
            "space. Russia gains access to PRC electronics and manufacturing capacity. "
            "Joint programs complicate FVEY deterrence planning."
        ),
        "source_reference": "CNSA-Roscosmos ILRS MOU; bilateral agreements; joint mission announcements",
    },
]

# ---------------------------------------------------------------------------
# DPRK Future Plans
# ---------------------------------------------------------------------------

_DPRK_FUTURES: List[dict] = [
    {
        "nation": "DPRK",
        "program_name": "Malligyong-2 Reconnaissance Satellite",
        "description": (
            "Follow-on military reconnaissance satellite to Malligyong-1 (launched November "
            "2023 with reported Russian assistance). Expected to feature improved imaging "
            "resolution and longer operational life. May use improved Chollima-1 SLV or "
            "new solid-fuel variant."
        ),
        "timeline": "2025-2026",
        "status": STATUS_ANNOUNCED,
        "domain": DOMAIN_ISR,
        "strategic_impact": (
            "Provides DPRK with indigenous ISR capability to monitor ROK/US military "
            "activities on the Korean Peninsula. Even limited-quality imagery gives DPRK "
            "strategic warning. Russian technical assistance accelerating capability."
        ),
        "source_reference": "KCNA announcements; Kim Jong Un public statements; ROK intelligence assessments",
    },
    {
        "nation": "DPRK",
        "program_name": "Solid-Fuel SLV Development",
        "description": (
            "Development of solid-fuel space launch vehicle leveraging solid ICBM technology "
            "(Hwasong-18). Solid-fuel SLV would enable rapid-response military satellite "
            "launches without the hours-long fueling process required by liquid-fuel Chollima-1. "
            "Follows solid ICBM testing success."
        ),
        "timeline": "2026-2028",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_LAUNCH,
        "strategic_impact": (
            "Solid-fuel SLV enables tactically responsive space launch, potentially from "
            "mobile platforms. Complicates preemptive strike options by reducing launch "
            "preparation time. Technology directly applicable to solid ICBM improvements."
        ),
        "source_reference": "38 North analysis; Hwasong-18 test observations; CSIS Missile Threat Project",
    },
    {
        "nation": "DPRK",
        "program_name": "Sohae Launch Pad Upgrades",
        "description": (
            "Ongoing upgrades to the Sohae (Tongchang-ri) satellite launching station. "
            "Satellite imagery shows construction of new facilities, expanded engine test "
            "stands, and modernized launch infrastructure. May include preparations for "
            "larger SLVs and increased launch cadence."
        ),
        "timeline": "2024-2027",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_LAUNCH,
        "strategic_impact": (
            "Enhanced launch infrastructure supports both satellite and ICBM programs. "
            "Larger facilities suggest pursuit of heavier payloads. Increased cadence "
            "capability enables constellation building."
        ),
        "source_reference": "38 North satellite imagery analysis; Planet Labs commercial imagery; CSIS Beyond Parallel",
    },
]

# ---------------------------------------------------------------------------
# Iran Future Plans
# ---------------------------------------------------------------------------

_IRAN_FUTURES: List[dict] = [
    {
        "nation": "Iran",
        "program_name": "Soroush / Qaem-100 SLV Development",
        "description": (
            "Development of the Qaem-100 solid-fuel space launch vehicle by the IRGC "
            "Aerospace Force. First suborbital test conducted in November 2022. Three-stage "
            "solid-fuel design capable of placing small payloads in LEO. Represents "
            "evolution beyond the partially-solid Qased SLV. Soroush is a related larger "
            "SLV program for heavier payloads."
        ),
        "timeline": "2025-2027",
        "status": STATUS_TESTING,
        "domain": DOMAIN_LAUNCH,
        "strategic_impact": (
            "All-solid SLV eliminates fueling time, enabling rapid-response military "
            "satellite launches. IRGC development (separate from civilian ISA) confirms "
            "military space program. Solid-fuel technology applicable to longer-range "
            "ballistic missiles. Increases Iranian launch cadence potential."
        ),
        "source_reference": "IRGC announcements; Qaem-100 test imagery; CSIS Missile Threat; Middlebury MIIS analysis",
    },
    {
        "nation": "Iran",
        "program_name": "Khayyam-2 Follow-On Satellite",
        "description": (
            "Follow-on to the Russian-built Khayyam earth observation satellite launched in "
            "August 2022 on a Soyuz from Baikonur. Khayyam-2 expected to feature improved "
            "resolution and potentially indigenous Iranian components. May include additional "
            "SIGINT or military-relevant sensors. Cooperation with Russia continues to "
            "expand Iranian space capabilities."
        ),
        "timeline": "2025-2027",
        "status": STATUS_ANNOUNCED,
        "domain": DOMAIN_ISR,
        "strategic_impact": (
            "Provides Iran with improved EO/ISR capability from space. Russian assistance "
            "accelerates Iranian satellite technology. Even moderate-resolution imagery "
            "useful for monitoring regional adversaries (Israel, Saudi Arabia, US bases)."
        ),
        "source_reference": "ISA/IRGC announcements; Iran-Russia space cooperation agreements; news reporting",
    },
    {
        "nation": "Iran",
        "program_name": "IRGC Space Launch Cadence Expansion",
        "description": (
            "IRGC Aerospace Force planning increased space launch frequency from current "
            "rate of 1-2 per year to potentially quarterly launches. Leveraging Shahrud "
            "launch site with mobile Qased/Qaem infrastructure. Building inventory of "
            "Noor-series military satellites for rapid deployment. Aims to establish "
            "persistent ISR constellation."
        ),
        "timeline": "2025-2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_LAUNCH,
        "strategic_impact": (
            "Higher launch cadence enables constellation building for persistent ISR. "
            "IRGC control (vs civilian ISA) ensures military prioritization. Mobile "
            "launch capability from Shahrud complicates preemption. Growing partnership "
            "with Russia for technology transfer."
        ),
        "source_reference": "IRGC public statements; Shahrud imagery analysis; Iran Space Observer tracking",
    },
    {
        "nation": "Iran",
        "program_name": "Russia-Iran Satellite Technology Transfer",
        "description": (
            "Expanding cooperation between Russia and Iran on satellite technology, "
            "including: Russian-built satellites for Iranian operation (Khayyam model), "
            "technology transfer for indigenous Iranian satellite manufacturing, potential "
            "Iranian access to Russian ground station network, and cooperation on remote "
            "sensing data sharing."
        ),
        "timeline": "2024-2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_ISR,
        "strategic_impact": (
            "Rapidly accelerates Iranian space capabilities beyond indigenous development "
            "pace. Russia benefits from Iranian drone/munitions cooperation (quid pro quo). "
            "Complicates Western sanctions enforcement. Could enable Iranian ISR capability "
            "leap comparable to DPRK's Russian-assisted Malligyong program."
        ),
        "source_reference": "US intelligence community assessments (DNI reports); bilateral agreement reporting; SWF analysis",
    },
]

# ---------------------------------------------------------------------------
# FVEY & Allied Future Plans
# ---------------------------------------------------------------------------

_FVEY_FUTURES: List[dict] = [
    {
        "nation": "US",
        "program_name": "Proliferated Warfighter Space Architecture (PWSA)",
        "description": (
            "Department of Defense architecture of 300-500+ satellites in LEO providing "
            "missile tracking, missile warning, data transport, and battle management. "
            "Designed to be resilient through proliferation — too many targets for adversary "
            "ASAT to defeat. Replaces traditional exquisite/vulnerable GEO-based architecture. "
            "Satellites are smaller, cheaper, and more quickly replaceable."
        ),
        "timeline": "2024-2030 (phased deployment)",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_SDA,
        "strategic_impact": (
            "Fundamental shift in US military space architecture from few exquisite assets "
            "to many distributed assets. Dramatically improves resilience against ASAT attack. "
            "Provides hypersonic missile tracking capability that legacy systems lack. "
            "Changes adversary ASAT calculus by making attacks uneconomical."
        ),
        "source_reference": "SDA budget documents; SDA Director Derek Tournear public statements; GAO assessments",
    },
    {
        "nation": "US",
        "program_name": "SDA Tranche Deployments (Tranche 0, 1, 2)",
        "description": (
            "Space Development Agency phased constellation deployment: Tranche 0 (28 sats, "
            "deployed 2023-2024, demo capability), Tranche 1 (150+ sats, 2024-2025, initial "
            "operational), Tranche 2 (200+ sats, 2026-2027, enhanced). Each tranche includes "
            "Transport Layer (optical mesh comms) and Tracking Layer (missile tracking). "
            "Built by multiple vendors (L3Harris, Northrop Grumman, Lockheed Martin, York)."
        ),
        "timeline": "2023-2028",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_SDA,
        "strategic_impact": (
            "Progressive capability buildout from demo to operational. Optical inter-satellite "
            "links create a mesh network resistant to jamming. Tranche 1 provides initial "
            "hypersonic tracking. Tranche 2 achieves persistent global coverage. Multi-vendor "
            "approach ensures supply chain resilience."
        ),
        "source_reference": "SDA contract announcements; DoD budget requests; SDA Tranche delivery schedules",
    },
    {
        "nation": "US",
        "program_name": "Next-Gen OPIR (SBIRS Follow-On)",
        "description": (
            "Next-Generation Overhead Persistent Infrared system replacing SBIRS (Space-Based "
            "Infrared System) for missile warning and missile defense. Includes GEO satellites "
            "(3 planned, built by Lockheed Martin) and polar-orbit satellites (2 planned, "
            "built by Northrop Grumman). Improved sensors for detecting dimmer targets "
            "including hypersonic glide vehicles."
        ),
        "timeline": "2025-2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_SDA,
        "strategic_impact": (
            "Critical for maintaining US missile warning capability against evolving threats "
            "including hypersonic weapons. GEO component provides persistent staring coverage; "
            "polar component covers high-latitude approaches. Combined with PWSA Tracking "
            "Layer, creates layered missile detection architecture."
        ),
        "source_reference": "USAF/USSF budget documents; Lockheed Martin/Northrop Grumman contracts; GAO reports",
    },
    {
        "nation": "US",
        "program_name": "GPS III Follow-On (GPS IIIF)",
        "description": (
            "Follow-on generation of GPS satellites adding regional military protection "
            "(anti-jam) capability, search-and-rescue payload, and enhanced accuracy. "
            "22 GPS IIIF satellites planned, built by Lockheed Martin. Introduces new "
            "M-code military signal with significantly improved anti-jamming. First "
            "launch expected mid-2020s."
        ),
        "timeline": "2026-2035",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_PNT,
        "strategic_impact": (
            "Ensures GPS constellation modernization against evolving EW threats. Regional "
            "military protection dramatically increases jamming resistance in contested "
            "areas. M-code provides encrypted, high-power military signal. Essential for "
            "maintaining PNT advantage over adversary GNSS."
        ),
        "source_reference": "USSF GPS Directorate; Lockheed Martin GPS IIIF contract; DoD budget documents",
    },
    {
        "nation": "US",
        "program_name": "GSSAP Expansion (Geosynchronous Space Situational Awareness Program)",
        "description": (
            "Expansion of the GSSAP constellation of inspector/SSA satellites operating near "
            "GEO. Current constellation of 6+ satellites conducts proximity operations to "
            "characterize objects in the GEO belt. Additional satellites planned to increase "
            "coverage and reduce revisit times. Operated by 4th Space Control Squadron."
        ),
        "timeline": "2025-2028",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_SDA,
        "strategic_impact": (
            "Provides close-up characterization of adversary GEO satellites. Can detect "
            "covert operations, verify satellite capabilities, and monitor suspicious "
            "maneuvers in GEO. Essential for attributing adversary counterspace activities. "
            "Dual-use for US counterspace demonstration."
        ),
        "source_reference": "USSF fact sheets; CSpOC statements; SWF reports on GSSAP operations",
    },
    {
        "nation": "US",
        "program_name": "Tactically Responsive Space (TacRS)",
        "description": (
            "Capability to rapidly launch and deploy satellites in response to combatant "
            "commander needs within hours to days (vs months/years). Leverages commercial "
            "small launch vehicles (Rocket Lab, Firefly, etc.), pre-built satellite buses, "
            "and streamlined operations. Victus Nox demonstration (2023) achieved launch "
            "within 27 hours of activation order."
        ),
        "timeline": "2024-2030",
        "status": STATUS_TESTING,
        "domain": DOMAIN_LAUNCH,
        "strategic_impact": (
            "Enables rapid reconstitution of degraded space capabilities during conflict. "
            "Counters adversary ASAT strategy by demonstrating ability to replace destroyed "
            "assets quickly. Changes adversary cost calculus — destroyed satellites can be "
            "replaced faster than ASAT weapons can be produced."
        ),
        "source_reference": "USSF Victus Nox mission (Sep 2023); SSC TacRS program; Rocket Lab/Firefly contracts",
    },
    {
        "nation": "US",
        "program_name": "Commercial Augmentation (Starshield / Commercial ISR)",
        "description": (
            "Systematic integration of commercial space capabilities into DoD architecture. "
            "Includes: SpaceX Starshield (military Starlink variant with enhanced encryption "
            "and sensor hosting), commercial ISR procurement (BlackSky, Planet, Maxar imagery "
            "under NRO contracts), and commercial SATCOM augmentation. CASINO (Commercial "
            "Augmentation Space Inter-Networking Operations) program."
        ),
        "timeline": "2024-2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_COMMS,
        "strategic_impact": (
            "Massively increases the number of US-aligned space assets, complicating "
            "adversary targeting. Commercial ISR provides persistent global coverage. "
            "Starshield extends resilient comms to contested environments. Commercial "
            "augmentation provides surge capacity and rapid technology refresh."
        ),
        "source_reference": "NRO commercial imagery contracts; SpaceX Starshield announcements; SDA CASINO program",
    },
    {
        "nation": "UK",
        "program_name": "Skynet 6A / 6B Military Communications Satellites",
        "description": (
            "Next-generation UK military SATCOM replacing Skynet 5 series. Skynet 6A is a "
            "dedicated military communications satellite built by Airbus Defence and Space. "
            "Enhanced anti-jam capability, cyber resilience, and interoperability with FVEY "
            "partners. Skynet 6B may be a commercial-hosted payload approach."
        ),
        "timeline": "2025-2029",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_COMMS,
        "strategic_impact": (
            "Maintains UK sovereign military SATCOM capability. Enhanced resilience against "
            "jamming critical for NATO/FVEY operations. Ensures UK maintains independent "
            "strategic communications for nuclear deterrent and deployed forces. "
            "Interoperability with FVEY MILSATCOM architecture."
        ),
        "source_reference": "UK MOD Defence Command Paper; Airbus Defence contracts; UK Defence Equipment Plan",
    },
    {
        "nation": "Australia",
        "program_name": "JP 9102 Military Satellite Communications",
        "description": (
            "Australian Defence Force military satellite communications program. Acquiring "
            "sovereign MILSATCOM capability through a combination of dedicated military "
            "payload on a hosted commercial satellite and potential dedicated military "
            "satellite. Will provide UHF and above MILSATCOM services across the Indo-Pacific. "
            "Contract awarded to Lockheed Martin Australia."
        ),
        "timeline": "2027-2032",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_COMMS,
        "strategic_impact": (
            "Provides Australia with sovereign MILSATCOM for the first time, reducing "
            "dependence on US/UK satellite systems. Critical for ADF operations in the "
            "Indo-Pacific. Supports AUKUS alliance communications. Enhances FVEY "
            "regional communications resilience."
        ),
        "source_reference": "Australian DoD Integrated Investment Program; Lockheed Martin Australia contract; ASPI analysis",
    },
    {
        "nation": "Australia",
        "program_name": "DEF 799 Space Domain Awareness",
        "description": (
            "Australian Defence program for enhanced space domain awareness capability. "
            "Includes optical and radar sensors for space surveillance, data fusion with "
            "FVEY SSA networks, and development of a national space operations centre. "
            "Builds on existing SSA cooperation (Space Surveillance Telescope at Exmouth, "
            "C-band radar at Woomera)."
        ),
        "timeline": "2025-2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_SDA,
        "strategic_impact": (
            "Enhances southern hemisphere SSA coverage — critical gap in global space "
            "surveillance network. Australian geographic position provides unique viewing "
            "geometry for GEO belt monitoring. Strengthens FVEY combined SSA picture. "
            "Supports attribution of adversary space activities."
        ),
        "source_reference": "Australian DoD Space Division; DSTG publications; ASPI Space Conference papers",
    },
    {
        "nation": "NATO",
        "program_name": "NATO Space Centre of Excellence (Toulouse)",
        "description": (
            "NATO-accredited Centre of Excellence for Space in Toulouse, France. Established "
            "to develop space doctrine, education, training, and interoperability standards "
            "for NATO allied space operations. Will provide space expertise and analysis to "
            "NATO command structure. Focuses on SSA, space support to operations, and "
            "counterspace threat analysis."
        ),
        "timeline": "2024-2026 (full operational capability)",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_SDA,
        "strategic_impact": (
            "Institutionalizes space as a NATO operational domain. Standardizes allied "
            "space operations and interoperability. Provides doctrinal framework for "
            "collective space defense. Enhances NATO ability to integrate space effects "
            "into allied military operations."
        ),
        "source_reference": "NATO summit communiques; French MOD announcements; NATO Space Centre establishment documents",
    },
    {
        "nation": "Japan",
        "program_name": "Quasi-Zenith Satellite System (QZSS) Expansion",
        "description": (
            "Expansion of Japan's regional satellite navigation augmentation system from 4 "
            "to 7 satellites, providing standalone PNT capability over the Asia-Pacific "
            "independent of GPS. Enhanced signals include centimeter-level positioning "
            "and authentication features to defeat spoofing. Operated by the Cabinet Office "
            "with JAXA support."
        ),
        "timeline": "2025-2027",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_PNT,
        "strategic_impact": (
            "Provides Japan and regional allies with GPS-independent PNT. Critical for "
            "military operations if GPS is jammed/spoofed by adversaries. Enhanced accuracy "
            "supports precision-guided munitions. Spoofing authentication is a direct "
            "counter to PRC/Russia GPS warfare."
        ),
        "source_reference": "Cabinet Office QZSS roadmap; JAXA documentation; Japan National Defense Strategy 2022",
    },
    {
        "nation": "Japan",
        "program_name": "Japan SSA Contributions and Space Operations Squadron",
        "description": (
            "Japan Air Self-Defense Force (JASDF, now Japan Air and Space Self-Defense Force) "
            "established a Space Operations Squadron in 2022 and expanding to a Space "
            "Operations Group. Building SSA capabilities including a space surveillance "
            "radar at Kamisaibara and optical telescope network. Contributing SSA data "
            "to FVEY/allied space surveillance sharing."
        ),
        "timeline": "2024-2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_SDA,
        "strategic_impact": (
            "Adds Japanese SSA sensors to the allied space surveillance network. Geographic "
            "position provides coverage of Chinese and DPRK launch activities. Japanese "
            "space force maturation strengthens the allied space coalition in the "
            "Indo-Pacific. Supports US-Japan alliance interoperability."
        ),
        "source_reference": "Japan MOD National Defense Strategy; JASDF Space Operations announcements; US-Japan SSA agreement",
    },
    {
        "nation": "South Korea",
        "program_name": "ROK Indigenous Military Satellite Program Expansion",
        "description": (
            "South Korea expanding indigenous military satellite capabilities including: "
            "425 Project military reconnaissance satellites (SAR and EO, 5 satellites), "
            "next-generation ISR satellite constellation, indigenous military SATCOM, and "
            "development of an SSA capability. KARI/DAPA working on follow-on programs "
            "beyond the initial 425 Project."
        ),
        "timeline": "2024-2030",
        "status": STATUS_DEVELOPMENT,
        "domain": DOMAIN_ISR,
        "strategic_impact": (
            "Provides ROK with sovereign ISR capability for Korean Peninsula monitoring, "
            "reducing dependence on US intelligence sharing. Critical for detecting DPRK "
            "missile launch preparations. Supports kill chain and KAMD missile defense "
            "decision timelines. Strengthens allied ISR coverage."
        ),
        "source_reference": "DAPA 425 Project announcements; ROK MOD budget documents; KARI roadmap",
    },
]

# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

_ALL_FUTURES: List[dict] = (
    _PRC_FUTURES + _RUSSIA_FUTURES + _DPRK_FUTURES + _IRAN_FUTURES + _FVEY_FUTURES
)

_NATION_ALIAS: Dict[str, str] = {
    "CHINA": "PRC",
    "RUSSIA": "Russia",
    "CIS": "Russia",
    "NORTHKOREA": "DPRK",
    "NKOR": "DPRK",
    "IRAN": "Iran",
    "UNITEDSTATES": "US",
    "USA": "US",
    "UNITEDKINGDOM": "UK",
    "AUSTRALIA": "Australia",
    "AU": "Australia",
    "JAPAN": "Japan",
    "JP": "Japan",
    "SOUTHKOREA": "South Korea",
    "ROK": "South Korea",
    "KR": "South Korea",
}


def _resolve_nation(nation: str) -> str:
    """Normalize nation name for lookup."""
    key = nation.strip().upper().replace(" ", "")
    return _NATION_ALIAS.get(key, nation.strip())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_all_futures() -> dict:
    """Return all future space program entries."""
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total_programs": len(_ALL_FUTURES),
        "programs": _ALL_FUTURES,
    }


def get_futures_by_nation(nation: str) -> dict:
    """Filter future programs by nation."""
    resolved = _resolve_nation(nation)
    programs = [p for p in _ALL_FUTURES if p["nation"] == resolved]
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "filter": {"nation": resolved},
        "total_programs": len(programs),
        "programs": programs,
    }


def get_futures_by_domain(domain: str) -> dict:
    """Filter future programs by domain (ISR, comms, PNT, launch, etc.)."""
    d = domain.strip()
    programs = [p for p in _ALL_FUTURES if p["domain"].lower() == d.lower()]
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "filter": {"domain": d},
        "total_programs": len(programs),
        "programs": programs,
    }


def get_futures_by_timeline(year: int) -> dict:
    """Return programs expected to be active/complete by the given year.

    Matches entries whose timeline string contains a year <= the given year.
    """
    programs = []
    for p in _ALL_FUTURES:
        tl = p["timeline"]
        # Extract all 4-digit years from the timeline string
        years_in_tl = [int(y) for y in re.findall(r"\b(20\d{2})\b", tl)]
        if years_in_tl and min(years_in_tl) <= year:
            programs.append(p)
    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "filter": {"by_year": year},
        "total_programs": len(programs),
        "programs": programs,
    }


def get_futures_summary() -> dict:
    """Summary statistics across all future space programs."""
    by_nation: Dict[str, int] = {}
    by_domain: Dict[str, int] = {}
    by_status: Dict[str, int] = {}

    for p in _ALL_FUTURES:
        n = p["nation"]
        by_nation[n] = by_nation.get(n, 0) + 1
        d = p["domain"]
        by_domain[d] = by_domain.get(d, 0) + 1
        s = p["status"]
        by_status[s] = by_status.get(s, 0) + 1

    adversary_count = sum(
        by_nation.get(n, 0) for n in ("PRC", "Russia", "DPRK", "Iran")
    )
    fvey_allied_count = len(_ALL_FUTURES) - adversary_count

    return {
        "classification": "UNCLASSIFIED // OSINT",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total_programs": len(_ALL_FUTURES),
        "adversary_programs": adversary_count,
        "fvey_allied_programs": fvey_allied_count,
        "by_nation": by_nation,
        "by_domain": by_domain,
        "by_status": by_status,
        "key_milestones": [
            {"year": 2025, "event": "Xuntian space telescope launch (PRC)"},
            {"year": 2026, "event": "Chang'e-7 lunar south pole (PRC)"},
            {"year": 2026, "event": "GPS IIIF first launch (US)"},
            {"year": 2027, "event": "ROSS first module (Russia, if on schedule)"},
            {"year": 2027, "event": "QZSS 7-satellite constellation complete (Japan)"},
            {"year": 2028, "event": "Chang'e-8 ISRU test (PRC)"},
            {"year": 2028, "event": "SDA Tranche 2 operational (US)"},
            {"year": 2030, "event": "PRC crewed lunar landing target"},
            {"year": 2030, "event": "300+ Yaogan ISR sats (PRC target)"},
            {"year": 2030, "event": "Long March 9 first flight (PRC target)"},
            {"year": 2030, "event": "ILRS initial construction (PRC-Russia target)"},
        ],
        "assessment": (
            "The global space competition is accelerating across all domains. PRC is executing "
            "the most comprehensive and well-funded space expansion program, with particular "
            "emphasis on lunar presence, ISR proliferation, and broadband constellation. Russia's "
            "programs are severely constrained by sanctions and funding, with most timelines "
            "slipping. FVEY is shifting toward resilient, proliferated architectures (PWSA/SDA) "
            "to counter adversary ASAT threats. The cislunar domain is emerging as the next "
            "contested space with competing PRC-Russia (ILRS) and US-led (Artemis) frameworks."
        ),
    }
