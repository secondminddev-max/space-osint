"""
Strategic threat assessment engine — the analytical "brain" of the Space OSINT Centre.
Combines live satellite/launch data with structured intelligence databases to produce
actionable threat assessments, vulnerability analyses, and policy recommendations.

All assessments are based on publicly available open-source analysis.
Classification: UNCLASSIFIED // OSINT

Sources framework:
- Secure World Foundation "Global Counterspace Capabilities" (annual)
- CSIS Aerospace Security Project reports
- NASIC "Competing in Space" & "Ballistic and Cruise Missile Threat"
- DIA "Challenges to Security in Space" (2022)
- Congressional Research Service reports on space security
- Todd Harrison (CSIS) space threat assessments
- Brian Weeden (SWF) technical analyses
- Academic literature on space security and deterrence
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx

from data_sources.adversary_sats import get_adversary_stats
from data_sources.ground_stations import (
    get_adversary_stations,
    get_fvey_stations,
    get_stations_summary,
)
from data_sources.missile_intel import (
    get_missile_asat_data,
    get_by_country as get_missiles_by_country,
    get_threat_summary as get_missile_threat_summary,
    THREAT_CRITICAL,
    THREAT_HIGH,
)

# ---------------------------------------------------------------------------
# Severity / priority constants
# ---------------------------------------------------------------------------
SEVERITY_CRITICAL = "critical"
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"
SEVERITY_INFO = "info"

PRIORITY_IMMEDIATE = "immediate"
PRIORITY_SHORT_TERM = "short_term"      # 0-2 years
PRIORITY_MEDIUM_TERM = "medium_term"    # 2-5 years
PRIORITY_LONG_TERM = "long_term"        # 5-10 years


# ---------------------------------------------------------------------------
# generate_threat_overview
# ---------------------------------------------------------------------------

async def generate_threat_overview(client: httpx.AsyncClient) -> dict:
    """Generate a current global space threat level and summary.

    Combines live satellite catalog data (adversary counts, recent activity)
    with structured intelligence context to produce an overall assessment.

    Returns:
        Dict with overall_threat_level, summary, key_concerns, and details.
    """
    # Pull live adversary satellite stats
    try:
        sat_stats = await get_adversary_stats(client)
    except Exception:
        sat_stats = None

    missile_summary = get_missile_threat_summary()
    station_summary = get_stations_summary()

    # Count critical/high-threat systems
    critical_systems = []
    high_systems = []
    for country_data in missile_summary.values():
        critical_systems.extend(country_data.get("critical_systems", []))
        high_count = country_data.get("by_threat_level", {}).get("high", 0)
        high_systems.append(high_count)

    # Determine overall threat level based on indicators
    # In a production system this would incorporate real-time event feeds
    overall_level = SEVERITY_HIGH  # Baseline: elevated due to current geopolitical environment

    now_utc = datetime.now(timezone.utc).isoformat()

    key_concerns = [
        {
            "title": "PRC Rapid Space Expansion",
            "severity": SEVERITY_CRITICAL,
            "detail": (
                "PRC has the most rapidly expanding military space program globally. "
                "Yaogan ISR constellation approaching 100+ satellites providing "
                "near-persistent maritime surveillance of the Western Pacific. BeiDou "
                "constellation fully operational providing PNT independence from GPS. "
                "Multiple demonstrated ASAT capabilities (DA-ASAT, co-orbital RPO, "
                "directed energy, EW, cyber). SJ-21 demonstrated GEO satellite capture "
                "capability — a game-changing threat to FVEY GEO assets."
            ),
            "evidence": (
                "DoD Annual Report on PRC Military Power; SWF Global Counterspace "
                "2023/2024; ExoAnalytic SJ-21 tracking data"
            ),
        },
        {
            "title": "Russian Counter-Space Aggression",
            "severity": SEVERITY_CRITICAL,
            "detail": (
                "Russia conducted destructive DA-ASAT test in November 2021 (Cosmos "
                "1408), creating 1,500+ debris fragments. Cosmos 2542/2543 demonstrated "
                "co-orbital ASAT and in-orbit weapons release near a classified US "
                "satellite. Viasat KA-SAT cyberattack (Feb 2022) demonstrated willingness "
                "to target commercial satellite infrastructure during conflict. Continued "
                "inspector satellite deployments (Cosmos 2558). Peresvet laser system "
                "deployed at ICBM bases."
            ),
            "evidence": (
                "USSPACECOM statements; NSA/CISA Viasat attribution; 18 SDS tracking; "
                "SWF Global Counterspace 2023"
            ),
        },
        {
            "title": "Space Debris Environment Degradation",
            "severity": SEVERITY_HIGH,
            "detail": (
                "The 2007 PRC FY-1C and 2021 Russian Cosmos 1408 ASAT tests created "
                "~5,000+ trackable debris fragments in heavily used LEO bands. This "
                "debris increases collision risk for all space operators and demonstrates "
                "that adversaries are willing to degrade the space environment for "
                "military advantage. A Kessler syndrome cascade remains a long-term risk "
                "that would deny LEO to all nations."
            ),
            "evidence": (
                "18 SDS/CSpOC debris catalog; ESA Space Debris Office; "
                "NASA ODPO conjunction assessments"
            ),
        },
        {
            "title": "Electronic Warfare Against Space Segment",
            "severity": SEVERITY_HIGH,
            "detail": (
                "GPS jamming/spoofing is now routine in multiple theaters (Ukraine, "
                "Syria, Baltic, South China Sea). Military SATCOM jamming systems "
                "(Tirada-2, PRC uplink jammers) are assessed operational. This "
                "threatens FVEY military communications, precision navigation, and "
                "timing-dependent systems (financial networks, power grids)."
            ),
            "evidence": (
                "C4ADS 'Above Us Only Stars'; EUROCONTROL GPS interference database; "
                "DIA 2022 report; DOT&E annual reports"
            ),
        },
        {
            "title": "Cyber Threats to Space Ground Segments",
            "severity": SEVERITY_HIGH,
            "detail": (
                "Ground segments remain the most vulnerable component of space "
                "architecture. The Viasat KA-SAT attack proved that cyber operations "
                "can disable satellite services across an entire continent. APT groups "
                "linked to PRC and Russia continue to target aerospace and satellite "
                "operators. A cyberattack on GPS ground control or SBIRS processing "
                "could have strategic consequences."
            ),
            "evidence": (
                "Viasat incident; Symantec Thrip group; Mandiant APT reports; "
                "CISA space infrastructure advisories"
            ),
        },
        {
            "title": "DPRK-Russia Space Cooperation",
            "severity": SEVERITY_MEDIUM,
            "detail": (
                "Russia reportedly provided technical assistance for DPRK's successful "
                "Malligyong-1 satellite launch (Nov 2023). This represents a new axis "
                "of space technology proliferation. DPRK ICBM technology (Hwasong-17 "
                "reached 6,248 km altitude) provides latent ASAT capability. "
                "Deepening Russia-DPRK cooperation could accelerate DPRK space and "
                "counterspace development."
            ),
            "evidence": (
                "US/ROK/Japan assessments; 38 North analysis; UNSC Panel of Experts; "
                "media reporting on arms cooperation"
            ),
        },
    ]

    overview = {
        "overall_threat_level": overall_level,
        "assessment_time_utc": now_utc,
        "summary": (
            "The global space threat environment is assessed as HIGH. Two peer "
            "adversaries (PRC, Russia) possess operational counterspace capabilities "
            "across all domains — kinetic, co-orbital, directed energy, electronic "
            "warfare, and cyber. Both have conducted destructive ASAT tests generating "
            "persistent orbital debris. PRC is rapidly expanding military space "
            "capabilities with a focus on ISR, PNT independence, and GEO manipulation. "
            "Russia has demonstrated willingness to employ cyber operations against "
            "satellite infrastructure during armed conflict. Regional adversaries "
            "(DPRK, Iran) are developing indigenous space capabilities with increasing "
            "technical sophistication, supported by cooperation with peer adversaries."
        ),
        "key_concerns": key_concerns,
        "adversary_satellite_stats": sat_stats,
        "missile_threat_summary": missile_summary,
        "ground_infrastructure_summary": station_summary,
    }

    return overview


# ---------------------------------------------------------------------------
# get_fvey_vulnerabilities
# ---------------------------------------------------------------------------

def get_fvey_vulnerabilities() -> List[dict]:
    """Return structured assessment of FVEY space architecture vulnerabilities.

    Each vulnerability includes severity, description, and mitigation status.
    Based on publicly available analysis from CSIS, SWF, CRS, and GAO reports.
    """
    return [
        {
            "id": "VULN-001",
            "title": "GPS Dependency — Military and Civilian",
            "severity": SEVERITY_CRITICAL,
            "priority": PRIORITY_IMMEDIATE,
            "description": (
                "FVEY military operations are critically dependent on GPS for precision "
                "navigation, timing, and guided munitions. Civilian infrastructure "
                "(financial transactions, power grid synchronization, telecommunications, "
                "air traffic control) also depends on GPS timing. The GPS constellation "
                "is a single-point-of-failure: loss or degradation of GPS signals would "
                "cascade across military and civilian sectors. Current GPS satellites "
                "broadcast at relatively low power, making them vulnerable to ground-based "
                "jamming from relatively inexpensive equipment."
            ),
            "adversary_capability": (
                "PRC and Russia both operate regional and mobile GPS jamming/spoofing "
                "systems. Russia routinely jams GPS in conflict zones (Ukraine, Syria). "
                "DPRK has jammed GPS across the Korean Peninsula."
            ),
            "mitigation_status": (
                "GPS III satellites with M-code (military signal) improve anti-jam "
                "capability but rollout is slow. Alternative PNT sources (eLoran, LEO "
                "PNT constellations) are in early development. No operational GPS backup "
                "exists at scale."
            ),
            "evidence": "GAO GPS reports; DOT PNT backup studies; DOT&E annual reports",
        },
        {
            "id": "VULN-002",
            "title": "SATCOM Single Points of Failure",
            "severity": SEVERITY_HIGH,
            "priority": PRIORITY_IMMEDIATE,
            "description": (
                "Critical military SATCOM services (AEHF, WGS, MUOS) rely on small "
                "constellations of expensive, exquisite GEO satellites. Loss of even "
                "one satellite would create significant communications gaps. Ground "
                "segments are concentrated at a small number of military installations "
                "(Schriever, Buckley). Increasing reliance on commercial SATCOM (Starlink "
                "in Ukraine) creates dependency on systems not designed for military "
                "resilience."
            ),
            "adversary_capability": (
                "PRC SJ-21 demonstrated ability to physically move GEO satellites. Russia "
                "Tirada-2 can jam SATCOM uplinks. Cyber attacks (Viasat) can disable "
                "commercial SATCOM at scale."
            ),
            "mitigation_status": (
                "Protected Tactical SATCOM (PTS) program in development. Commercial "
                "augmentation (Starlink, SDA mesh) provides partial resilience. JADC2 "
                "architecture requires diverse SATCOM paths."
            ),
            "evidence": "CRS Military SATCOM reports; GAO AEHF/WGS assessments; Ukraine conflict observations",
        },
        {
            "id": "VULN-003",
            "title": "Limited Space Domain Awareness Coverage",
            "severity": SEVERITY_HIGH,
            "priority": PRIORITY_SHORT_TERM,
            "description": (
                "The US Space Surveillance Network (SSN) has significant gaps in coverage, "
                "particularly in the Southern Hemisphere. GEODSS optical sites have "
                "weather dependencies. Space Fence provides excellent LEO coverage but "
                "only from one location (Kwajalein). Deep-space (GEO/HEO) tracking "
                "relies on a small number of sensors. Ability to detect and characterize "
                "small maneuvering objects, especially in GEO, is limited. Cannot "
                "reliably determine intent of RPO activities in real-time."
            ),
            "adversary_capability": (
                "PRC and Russia both conduct RPO missions that may go undetected for "
                "hours/days. Small inspector satellites can approach targets with minimal "
                "observable maneuvers."
            ),
            "mitigation_status": (
                "Space Fence operational (2020). GSSAP satellites provide GEO neighborhood "
                "watch. Commercial SSA providers (LeoLabs, ExoAnalytic) augmenting military "
                "SSA. Allied contributions (UK Fylingdales, AU SST) fill some gaps. But "
                "Southern Hemisphere and deep-space coverage remain inadequate."
            ),
            "evidence": "GAO SSA reports; USSF SSN documentation; CRS Space Force reports",
        },
        {
            "id": "VULN-004",
            "title": "ISR Satellite Constellation Gaps",
            "severity": SEVERITY_HIGH,
            "priority": PRIORITY_SHORT_TERM,
            "description": (
                "FVEY relies heavily on a relatively small number of exquisite NRO ISR "
                "satellites for strategic intelligence. These high-value assets are known "
                "to adversaries (tracked by Russian/PRC SSA networks) and represent "
                "high-value targets. Loss of even 2-3 key ISR satellites would create "
                "significant intelligence gaps. Revisit rates for any single target are "
                "limited. Meanwhile, PRC is deploying massive commercial-style ISR "
                "constellations (Yaogan, Jilin) achieving near-persistent coverage."
            ),
            "adversary_capability": (
                "PRC has demonstrated ability to track NRO satellites. Russia Cosmos "
                "2558 deployed to shadow a classified US satellite. Both possess DA-ASAT "
                "capable of reaching NRO satellite altitudes."
            ),
            "mitigation_status": (
                "NRO proliferated architecture initiative moving toward more numerous, "
                "smaller satellites. SDA Transport and Tracking Layers being deployed. "
                "Commercial imagery (Maxar, Planet, BlackSky) provides augmentation. "
                "Transition is underway but legacy exquisite architecture persists."
            ),
            "evidence": "NRO unclassified strategy documents; SDA programmatic updates; CRS NRO reports",
        },
        {
            "id": "VULN-005",
            "title": "Allied Ground Station Geographic Gaps",
            "severity": SEVERITY_MEDIUM,
            "priority": PRIORITY_MEDIUM_TERM,
            "description": (
                "FVEY ground stations are concentrated in specific geographic regions "
                "with gaps in coverage. Southern Hemisphere and equatorial regions are "
                "underserved. Many ground stations are at fixed, known locations "
                "vulnerable to physical attack or sabotage. Ground station-to-satellite "
                "communications links can be jammed or intercepted. Limited redundancy "
                "for some critical functions (e.g., GPS Master Control at Schriever)."
            ),
            "adversary_capability": (
                "PRC has addressed its own ground station gaps with Yuan Wang tracking "
                "ships and overseas ground stations (Namibia, Argentina, Pakistan). "
                "Russia maintains global ground network through bilateral agreements."
            ),
            "mitigation_status": (
                "Multi-domain relay capabilities (TDRSS, SDA mesh) reduce ground station "
                "dependency. Allied nations expanding ground networks. But physical "
                "security of ground stations in permissive environments remains a concern."
            ),
            "evidence": "USSF ground station inventory; allied MoU documentation; CSIS analysis",
        },
        {
            "id": "VULN-006",
            "title": "Cyber Vulnerabilities in Ground Segments",
            "severity": SEVERITY_CRITICAL,
            "priority": PRIORITY_IMMEDIATE,
            "description": (
                "Space system ground segments — including satellite control software, "
                "data processing pipelines, and user terminals — present the largest "
                "cyber attack surface. Legacy systems may lack modern cybersecurity "
                "controls. Commercial satellite operators supporting military operations "
                "may have weaker security postures. Supply chain compromises (SolarWinds-style) "
                "could affect satellite control systems. The Viasat attack demonstrated "
                "that ground segment cyber attacks can achieve strategic effects."
            ),
            "adversary_capability": (
                "Russia GRU (Sandworm) conducted Viasat KA-SAT attack. PRC APT groups "
                "(APT10, APT41, Thrip) have targeted satellite operators and aerospace "
                "companies. Both possess world-class offensive cyber capabilities."
            ),
            "mitigation_status": (
                "CISA space infrastructure security guidance published. NIST cybersecurity "
                "framework adoption increasing. Zero-trust architectures being implemented. "
                "But legacy systems are difficult to retrofit and supply chain risks persist."
            ),
            "evidence": "Viasat incident; CISA advisories; Mandiant/Symantec APT reports; GAO cybersecurity audits",
        },
        {
            "id": "VULN-007",
            "title": "Supply Chain Dependencies (Rare Earths, Microelectronics)",
            "severity": SEVERITY_HIGH,
            "priority": PRIORITY_MEDIUM_TERM,
            "description": (
                "FVEY space systems depend on supply chains with significant PRC exposure. "
                "Rare earth elements (critical for satellite components, solar cells, "
                "propulsion) are ~60%+ sourced from PRC mining and ~90%+ from PRC "
                "processing. Radiation-hardened microelectronics have limited non-allied "
                "sources. Solar cell manufacturing is concentrated. In a conflict "
                "scenario, PRC could restrict supply of critical materials needed for "
                "satellite manufacturing and constellation reconstitution."
            ),
            "adversary_capability": (
                "PRC controls dominant share of rare earth processing and has previously "
                "restricted exports for geopolitical leverage (Japan 2010). PRC also "
                "dominates solar panel and battery manufacturing supply chains."
            ),
            "mitigation_status": (
                "CHIPS Act and allied rare earth mining initiatives underway but will "
                "take years to diversify supply. DoD trusted foundry program for "
                "microelectronics. Stockpiling strategies being evaluated."
            ),
            "evidence": "USGS mineral commodity summaries; DoD supply chain reviews; CRS rare earth reports",
        },
        {
            "id": "VULN-008",
            "title": "Launch Capacity Constraints",
            "severity": SEVERITY_MEDIUM,
            "priority": PRIORITY_SHORT_TERM,
            "description": (
                "While US commercial launch capacity (SpaceX) has dramatically expanded, "
                "assured access to space for national security payloads depends on a "
                "small number of launch providers (ULA, SpaceX, soon Rocket Lab/Blue "
                "Origin). Allied FVEY nations have very limited or no indigenous launch "
                "capability (UK and AU developing small-lift). In a conflict requiring "
                "rapid reconstitution of lost satellites, launch capacity could become "
                "a bottleneck, especially for medium/heavy-lift payloads."
            ),
            "adversary_capability": (
                "PRC has diverse launch fleet (CZ-2/3/4/5/6/7/8/11) with increasing "
                "cadence. Solid-fuel CZ-11 and commercial Kuaizhou provide rapid-response "
                "capability. Russia has reduced but still functional launch capacity."
            ),
            "mitigation_status": (
                "Tactically Responsive Space (TacRS) program developing rapid-call-up "
                "launch. Rocket Lab Electron and Firefly Alpha provide small-lift "
                "responsive launch. But heavy-lift for large GEO payloads remains "
                "constrained."
            ),
            "evidence": "USSF NSSL program documentation; GAO launch services reports; launch manifest databases",
        },
        {
            "id": "VULN-009",
            "title": "Debris Threat to LEO Assets",
            "severity": SEVERITY_HIGH,
            "priority": PRIORITY_LONG_TERM,
            "description": (
                "The LEO debris environment is deteriorating. Over 30,000 tracked objects "
                "and an estimated 1 million+ untracked fragments >1cm pose collision risk "
                "to operational satellites. The 2007 PRC and 2021 Russian ASAT tests added "
                "~5,000 trackable fragments in heavily used LEO bands. Mega-constellations "
                "(Starlink, OneWeb) increase the number of objects requiring tracking and "
                "conjunction assessment. A cascading collision event (Kessler syndrome) "
                "could render portions of LEO unusable for decades."
            ),
            "adversary_capability": (
                "Deliberate debris generation through ASAT testing. Irresponsible disposal "
                "of rocket bodies (CZ-5B uncontrolled reentries)."
            ),
            "mitigation_status": (
                "Space Fence improves small-debris tracking. Commercial SSA augments "
                "conjunction screening. Active debris removal still R&D (ClearSpace, "
                "Astroscale demos). No binding international debris mitigation rules."
            ),
            "evidence": "ESA Space Debris Office statistics; NASA ODPO; 18 SDS conjunction warnings",
        },
        {
            "id": "VULN-010",
            "title": "Lack of Rapid Reconstitution Capability",
            "severity": SEVERITY_CRITICAL,
            "priority": PRIORITY_IMMEDIATE,
            "description": (
                "If adversaries destroy or disable key FVEY satellites, there is no "
                "rapid reconstitution capability to replace them. Current satellite "
                "manufacturing timelines are 3-5+ years for exquisite systems. Even "
                "small satellites require months of integration and testing. Launch "
                "scheduling is typically planned months to years in advance. There are "
                "no pre-positioned spare satellites ready for rapid launch (except "
                "limited GPS reserves). The inability to quickly replace lost capabilities "
                "undermines deterrence — adversaries may calculate that a first-strike "
                "on FVEY space assets would create an irreversible advantage."
            ),
            "adversary_capability": (
                "PRC CZ-11 solid-fuel SLV can launch within 24 hours. PRC plans rapid "
                "reconstitution capability for its constellations. Russia maintains "
                "some military satellite reserves."
            ),
            "mitigation_status": (
                "SDA proliferated architecture provides inherent resilience through "
                "numbers. Tactically Responsive Space program aims for rapid call-up "
                "launch. Modular satellite buses (SDA Tranche architecture) reduce "
                "manufacturing time. But we are years from having true rapid "
                "reconstitution capability for national security space."
            ),
            "evidence": (
                "CSIS Todd Harrison reports on space resilience; SDA architecture docs; "
                "CRS Space Force reports; GAO satellite acquisition reports"
            ),
        },
    ]


# ---------------------------------------------------------------------------
# get_policy_recommendations
# ---------------------------------------------------------------------------

def get_policy_recommendations() -> List[dict]:
    """Return strategic policy recommendations for FVEY space security.

    Based on publicly available analysis from think tanks, government reports,
    and academic literature.
    """
    return [
        {
            "id": "REC-001",
            "title": "Resilient PNT Architecture Beyond GPS",
            "priority": PRIORITY_IMMEDIATE,
            "category": "resilience",
            "description": (
                "Develop and deploy a multi-layer PNT architecture that does not depend "
                "solely on GPS. This should include: (1) GPS III M-code acceleration to "
                "full capability, (2) LEO PNT augmentation constellation providing "
                "higher-power signals resistant to jamming, (3) ground-based backup "
                "(eLoran modernization), (4) integration of commercial LEO PNT signals "
                "(Xona Space, TrustPoint), (5) inertial navigation advances for GPS-denied "
                "operations, (6) atomic clock miniaturization for extended holdover "
                "during GPS outages."
            ),
            "rationale": (
                "GPS is the single most critical space-enabled capability and the most "
                "frequently targeted by adversary EW. A multi-layer PNT architecture "
                "removes the single point of failure."
            ),
            "estimated_cost": "USD 5-15B over 10 years",
            "evidence": "DoD PNT Strategy 2021; GAO GPS reports; RAND PNT resilience studies",
        },
        {
            "id": "REC-002",
            "title": "Proliferated LEO Satellite Architecture",
            "priority": PRIORITY_SHORT_TERM,
            "category": "resilience",
            "description": (
                "Transition from small numbers of exquisite satellites to large "
                "constellations of smaller, cheaper, rapidly replaceable satellites. "
                "The Space Development Agency (SDA) Transport and Tracking Layer "
                "approach should be expanded and accelerated. Key elements: (1) mesh-"
                "networked LEO communication constellation, (2) distributed ISR sensors "
                "across many satellites, (3) standardized satellite bus enabling rapid "
                "manufacturing, (4) optical inter-satellite links for jam-resistant "
                "data relay, (5) allied participation (UK Skynet successor, AU ISR "
                "contributions)."
            ),
            "rationale": (
                "Proliferation makes the architecture resilient to ASAT attack — "
                "destroying one or several satellites does not degrade overall capability "
                "significantly. This changes the adversary cost calculus for ASAT use."
            ),
            "estimated_cost": "USD 20-40B over 10 years",
            "evidence": "SDA architecture documents; DoD space resilience strategy; CSIS proliferated architecture analysis",
        },
        {
            "id": "REC-003",
            "title": "ASAT Deterrence and Norms Framework",
            "priority": PRIORITY_IMMEDIATE,
            "category": "deterrence",
            "description": (
                "Establish a credible deterrence framework for space: (1) Maintain "
                "ambiguity about US/allied counter-space response options, (2) Pursue "
                "binding or normative agreements against destructive DA-ASAT testing "
                "(build on US 2022 moratorium), (3) Develop attribution capability — "
                "ensure adversary knows any attack on FVEY space assets will be rapidly "
                "attributed, (4) Establish clear redlines and consequences, (5) Develop "
                "response options across the spectrum (diplomatic, economic, cyber, "
                "kinetic) that are proportionate and credible."
            ),
            "rationale": (
                "Deterrence requires adversaries to believe the costs of attacking FVEY "
                "space assets outweigh the benefits. This requires both capability and "
                "clear communication of resolve."
            ),
            "estimated_cost": "Diplomatic effort; USD 1-3B for attribution capabilities",
            "evidence": "VP Harris 2022 DA-ASAT test moratorium; UNGA resolutions; SWF norms analysis",
        },
        {
            "id": "REC-004",
            "title": "Space Traffic Management and Transparency",
            "priority": PRIORITY_MEDIUM_TERM,
            "category": "governance",
            "description": (
                "Develop international space traffic management (STM) framework: "
                "(1) Share SSA data more broadly to build norms and expectations, "
                "(2) Establish keep-out zones and approach notification requirements, "
                "(3) Mandate conjunction assessment participation for all operators, "
                "(4) Create international SSA data fusion centre (building on Combined "
                "Space Operations Centre model), (5) Develop RPO rules of the road — "
                "minimum approach distances, notification requirements."
            ),
            "rationale": (
                "Transparency reduces the risk of miscalculation and establishes norms "
                "that can constrain adversary behavior. Without STM rules, adversary "
                "inspector satellites can approach FVEY assets with impunity."
            ),
            "estimated_cost": "USD 500M-1B; significant diplomatic effort",
            "evidence": "UNOOSA STM discussions; CONFERS RPO standards; IADC guidelines",
        },
        {
            "id": "REC-005",
            "title": "Allied Burden Sharing in Space Domain",
            "priority": PRIORITY_SHORT_TERM,
            "category": "alliance",
            "description": (
                "Expand FVEY space cooperation and burden sharing: (1) UK: invest in "
                "Skynet successor with allied interoperability, expand SSA contribution "
                "(Fylingdales, new sensors), (2) AU: expand Pine Gap cooperation, deploy "
                "sovereign SSA capabilities, participate in SDA architecture, (3) CA: "
                "Sapphire successor program, Arctic SSA coverage, (4) NZ: leverage "
                "Rocket Lab for responsive launch, southern hemisphere SSA contribution, "
                "(5) Establish allied space operations playbook and exercise program."
            ),
            "rationale": (
                "The US cannot shoulder the entire space security burden. Allied geographic "
                "distribution provides natural advantages for SSA and ground station "
                "coverage. Burden sharing increases political cost of adversary attacks."
            ),
            "estimated_cost": "Varies by nation; USD 5-15B aggregate over 10 years",
            "evidence": "CSpO initiative documentation; AUKUS space cooperation announcements; NATO space policy",
        },
        {
            "id": "REC-006",
            "title": "Counter-Space Capability Development Priorities",
            "priority": PRIORITY_SHORT_TERM,
            "category": "capability",
            "description": (
                "Develop a balanced counter-space portfolio: (1) Non-kinetic, reversible "
                "effects (EW jamming, cyber, dazzling) as primary tools — avoids debris "
                "and escalation, (2) Maintain kinetic options as deterrent but avoid "
                "testing to uphold moratorium credibility, (3) Invest in proximity "
                "operations capability for inspection and characterization of adversary "
                "satellites, (4) Develop ground-segment cyber response options, "
                "(5) Ensure counter-space capabilities are integrated into combatant "
                "command warfighting plans."
            ),
            "rationale": (
                "Credible deterrence requires demonstrated capability. Non-kinetic "
                "options provide escalation management while maintaining effects. "
                "Proximity operations provide intelligence on adversary systems."
            ),
            "estimated_cost": "Classified programs; estimated USD 3-8B annually",
            "evidence": "DoD counter-space strategy (unclass summary); CRS Space Force reports; CSIS analysis",
        },
        {
            "id": "REC-007",
            "title": "Space Domain Awareness Sensor Gap Investment",
            "priority": PRIORITY_IMMEDIATE,
            "category": "awareness",
            "description": (
                "Close critical SSA sensor gaps: (1) Southern Hemisphere deep-space "
                "optical coverage (expand SST deployment to Australia, South America), "
                "(2) Second Space Fence site in the Eastern Hemisphere, (3) Commercial "
                "SSA integration — operationalize LeoLabs, ExoAnalytic, Slingshot data "
                "feeds, (4) On-orbit SSA — expand GSSAP constellation and deploy "
                "distributed SSA sensors as hosted payloads, (5) RF SSA — detect and "
                "characterize adversary satellite emissions, (6) AI/ML for anomaly "
                "detection and pattern-of-life analysis of adversary satellite activities."
            ),
            "rationale": (
                "Cannot defend what you cannot see. SSA is the foundation of all space "
                "security operations. Current gaps allow adversary activities to go "
                "undetected."
            ),
            "estimated_cost": "USD 3-7B over 5 years",
            "evidence": "USSF SSA architecture reviews; GAO reports; CSpOC capability gap assessments",
        },
        {
            "id": "REC-008",
            "title": "Norms of Responsible Behavior in Space",
            "priority": PRIORITY_MEDIUM_TERM,
            "category": "governance",
            "description": (
                "Pursue international norms framework: (1) Expand the US-led DA-ASAT "
                "test moratorium — secured commitments from 37+ nations by 2024, "
                "(2) Define irresponsible behaviors (debris generation, dangerous "
                "proximity operations, interference with space objects), (3) Establish "
                "pre-launch notifications for orbital maneuvers near others' assets, "
                "(4) Develop space sustainability guidelines with compliance mechanisms, "
                "(5) Use UNGA and CD forums but also pursue like-minded plurilateral "
                "agreements if consensus is blocked."
            ),
            "rationale": (
                "Norms constrain adversary behavior and provide basis for collective "
                "response when violated. They also protect FVEY assets by establishing "
                "expectations."
            ),
            "estimated_cost": "Primarily diplomatic effort",
            "evidence": "UNGA A/RES/77/41; OEWG on reducing space threats; Woomera Manual; SWF norms analysis",
        },
        {
            "id": "REC-009",
            "title": "Rapid Launch and Reconstitution Investment",
            "priority": PRIORITY_SHORT_TERM,
            "category": "resilience",
            "description": (
                "Develop operational rapid reconstitution capability: (1) Pre-position "
                "satellite reserves (ground spares ready for rapid integration), "
                "(2) Standardize satellite bus/payload interfaces for rapid swap, "
                "(3) Contract for responsive launch capacity (Rocket Lab, Firefly, "
                "SpaceX rideshare, Virgin Orbit successor), (4) Develop on-orbit "
                "sparing — pre-deployed dormant satellites activated when needed, "
                "(5) Exercise the reconstitution timeline — conduct annual end-to-end "
                "exercises from satellite call-up to on-orbit operations within 24-72 hrs."
            ),
            "rationale": (
                "Rapid reconstitution capability changes the adversary calculus: if FVEY "
                "can quickly replace destroyed satellites, the benefit of ASAT use "
                "diminishes significantly."
            ),
            "estimated_cost": "USD 5-10B over 5 years for reserves and infrastructure",
            "evidence": "TacRS/Victus Nox exercise results; USSF responsive space strategy; CSIS reconstitution analysis",
        },
        {
            "id": "REC-010",
            "title": "Hardening Existing Space Assets",
            "priority": PRIORITY_SHORT_TERM,
            "category": "protection",
            "description": (
                "Harden current and future satellites against counterspace threats: "
                "(1) Anti-jam antennas (nulling, frequency hopping) for SATCOM and GPS, "
                "(2) Laser hardening for optical sensors (shutters, filters, warning "
                "systems), (3) Cyber hardening of satellite command links (encryption, "
                "authentication, anomaly detection), (4) Maneuver capability for all "
                "military satellites (fuel reserves for evasion), (5) Radiation hardening "
                "against potential nuclear detonation in space, (6) Autonomous operations "
                "capability if ground link is denied."
            ),
            "rationale": (
                "Hardening existing assets is often more cost-effective than replacement. "
                "Hardened satellites that can survive counterspace attack improve "
                "deterrence and operational resilience."
            ),
            "estimated_cost": "USD 2-5B across portfolio; some measures are design choices with minimal cost",
            "evidence": "DoD space protection strategy; DISA SATCOM security requirements; AFSPC hardening studies",
        },
    ]


# ---------------------------------------------------------------------------
# get_adversary_assessment — per-country strategic assessment
# ---------------------------------------------------------------------------

def get_adversary_assessment(country: str) -> Optional[dict]:
    """Return a per-country strategic assessment of space and counterspace capabilities.

    Args:
        country: "PRC", "Russia", "DPRK", or "Iran"
    """
    assessments: Dict[str, dict] = {
        "PRC": {
            "country": "PRC",
            "formal_name": "People's Republic of China",
            "overall_threat": SEVERITY_CRITICAL,
            "space_doctrine": (
                "PRC views space as a critical domain for modern warfare. PLA doctrine "
                "emphasizes 'informationized warfare' in which space-based ISR, "
                "communications, navigation, and early warning are essential enablers. "
                "Simultaneously, PLA writings emphasize attacking adversary space "
                "capabilities as a means to achieve 'information dominance' early in a "
                "conflict. The 2015 establishment of the Strategic Support Force (SSF, "
                "reorganized as Information Support Force in 2024) consolidated space, "
                "cyber, and EW capabilities under a single command."
            ),
            "key_capabilities": [
                "Full-spectrum counterspace: DA-ASAT (SC-19/DN series), co-orbital RPO "
                "(Shijian series), DEW (ground-based laser), EW (GPS/SATCOM jamming), "
                "and cyber",
                "Largest military satellite constellation outside of the US — Yaogan ISR, "
                "BeiDou PNT, Zhongxing/Fenghuo MILSATCOM",
                "Independent PNT through BeiDou (35 satellites, global coverage)",
                "Growing space surveillance network (optical, radar, laser ranging)",
                "Heavy-lift launch capability (CZ-5, CZ-5B) with increasing cadence",
                "Demonstrated GEO satellite manipulation (SJ-21 towing capability)",
                "Crewed space station (CSS/Tiangong) with permanent human presence",
                "Lunar and Mars exploration programs demonstrating deep space competence",
            ],
            "strategic_assessment": (
                "PRC is the most significant long-term space competitor and threat to FVEY "
                "space superiority. PRC is pursuing a comprehensive approach: building "
                "its own space capabilities while developing means to deny adversary space "
                "advantages. The scale and pace of PRC military space investment exceeds "
                "that of all other adversaries combined. PRC's demonstrated ability to "
                "manipulate satellites in GEO (SJ-21) and conduct RPO near adversary "
                "satellites represents a paradigm shift in the space threat. The integration "
                "of space, cyber, and EW under a single force provides unified counter-space "
                "operations capability."
            ),
            "intelligence_gaps": [
                "Exact number and capability of Yaogan constellation imaging sensors",
                "Operational status and deployment locations of ground-based laser ASAT",
                "True capability of SJ-17/SJ-21 robotic systems against hardened targets",
                "Extent of PRC SSA network capability to track and characterize FVEY satellites",
                "Cyber pre-positioning in FVEY satellite ground networks",
            ],
            "trend": "ESCALATING — Capabilities expanding across all domains annually",
            "evidence": (
                "DoD Annual Report on PRC Military Power (2023); SWF Global Counterspace "
                "2023/2024; DIA Challenges to Security in Space 2022; NASIC Competing in Space"
            ),
        },
        "Russia": {
            "country": "Russia",
            "formal_name": "Russian Federation",
            "overall_threat": SEVERITY_CRITICAL,
            "space_doctrine": (
                "Russia views space as essential for strategic deterrence and conventional "
                "military operations. Russian military doctrine emphasizes aerospace defense "
                "and the ability to deny adversary space capabilities. The Aerospace Forces "
                "(VKS) 15th Aerospace Army is responsible for space operations. Despite "
                "economic constraints, Russia has maintained and modernized counter-space "
                "capabilities as a priority, viewing them as an asymmetric tool to offset "
                "Western conventional military advantages."
            ),
            "key_capabilities": [
                "DA-ASAT: Nudol system tested 10+ times, destructive test against Cosmos 1408 (2021)",
                "Co-orbital ASAT: Inspector satellites (Cosmos 2542/2543, Cosmos 2558) with "
                "demonstrated RPO and in-orbit weapons release",
                "DEW: Peresvet laser system deployed with RVSN for satellite denial",
                "EW: Tirada-2 SATCOM jammer, Tobol counter-space EW, extensive GPS jamming",
                "Cyber: GRU Sandworm conducted Viasat KA-SAT attack at start of Ukraine invasion",
                "SSA: Voronezh radar network, Okno/Krona space surveillance",
                "Legacy but modernizing satellite constellations (GLONASS, EKS early warning, Liana SIGINT)",
            ],
            "strategic_assessment": (
                "Russia poses an immediate and demonstrated counter-space threat. Unlike PRC, "
                "which has shown restraint after the 2007 ASAT test, Russia conducted a "
                "destructive ASAT test in 2021 and cyberattacked a commercial satellite "
                "operator during the 2022 Ukraine invasion. Russia has demonstrated "
                "willingness to use counter-space capabilities in conflict. However, "
                "Russia's broader space program is constrained by economic sanctions, "
                "technology export controls, and the diversion of resources to the Ukraine "
                "conflict. Satellite constellation replenishment rates have slowed. The "
                "long-term trajectory of Russian space power is uncertain, but counter-space "
                "capabilities remain a priority investment."
            ),
            "intelligence_gaps": [
                "Nudol system operational deployment status and additional test site locations",
                "Peresvet deployment locations and actual performance parameters",
                "Extent of cyber pre-positioning in FVEY satellite ground networks",
                "Status of next-generation inspector satellite program",
                "Impact of sanctions on Russian space industrial base and constellation sustainment",
            ],
            "trend": "MAINTAINING — Counter-space prioritized despite broader program constraints",
            "evidence": (
                "SWF Global Counterspace 2023/2024; USSPACECOM public statements; "
                "NSA/CISA Viasat attribution; DIA 2022 report; Bart Hendrickx analyses"
            ),
        },
        "DPRK": {
            "country": "DPRK",
            "formal_name": "Democratic People's Republic of Korea",
            "overall_threat": SEVERITY_MEDIUM,
            "space_doctrine": (
                "DPRK views space launch capability as both a prestige project and a "
                "pathway to ICBM technology. The Malligyong-1 reconnaissance satellite "
                "represents an attempt to develop independent ISR capability for targeting "
                "of US/ROK military assets. DPRK does not have a known counter-space "
                "doctrine but ICBM capabilities provide latent ASAT potential."
            ),
            "key_capabilities": [
                "SLV/ICBM: Hwasong-15/17 ICBMs reaching LEO-relevant altitudes (4,500-6,200 km)",
                "Orbital capability: Chollima-1 SLV successfully orbited Malligyong-1 (Nov 2023)",
                "EW: GPS jamming demonstrated against ROK on multiple occasions",
                "Russian technical assistance accelerating capabilities",
            ],
            "strategic_assessment": (
                "DPRK is a secondary space threat but on an accelerating trajectory. "
                "The successful Malligyong-1 launch, reportedly with Russian assistance, "
                "marks a significant capability milestone. While DPRK satellites are assessed "
                "to be of limited quality, the establishment of an indigenous ISR satellite "
                "capability is strategically significant — it reduces DPRK dependence on "
                "other intelligence sources for military targeting. ICBM technology "
                "provides a latent ASAT capability. The deepening Russia-DPRK cooperation "
                "on space technology is a concerning proliferation vector."
            ),
            "intelligence_gaps": [
                "Extent and nature of Russian technical assistance for space program",
                "Actual imaging capability of Malligyong-1 satellite",
                "Next planned satellite launches and constellation plans",
                "Ground segment capability and data processing capacity",
                "Integration of satellite ISR with military targeting processes",
            ],
            "trend": "ESCALATING — Russian cooperation accelerating development",
            "evidence": (
                "CSIS Missile Threat; 38 North analysis; ROK JCS assessments; "
                "UNSC Panel of Experts reports; KCNA imagery analysis"
            ),
        },
        "Iran": {
            "country": "Iran",
            "formal_name": "Islamic Republic of Iran",
            "overall_threat": SEVERITY_LOW,
            "space_doctrine": (
                "Iran pursues space capability through two parallel programs: the civilian "
                "Iranian Space Agency (ISA) and the IRGC Aerospace Force. The IRGC program "
                "(Qased SLV, Noor satellites) represents the military dimension. Iran views "
                "indigenous space capability as a strategic necessity and a source of "
                "national prestige. Current focus is on achieving reliable orbital access "
                "and basic ISR capability."
            ),
            "key_capabilities": [
                "SLV: Qased (IRGC, solid-fuel first stage, successfully orbited Noor-1/2)",
                "SLV: Simorgh (ISA, liquid-fuel, multiple failures)",
                "Satellites: Noor series (IRGC military imaging), Khayyam (launched on Russian Soyuz)",
                "EW: Basic GPS jamming/spoofing capability (claimed RQ-170 capture)",
                "Growing but unreliable orbital delivery capability",
            ],
            "strategic_assessment": (
                "Iran is the least capable of the four adversaries in the space domain but "
                "is on a slow upward trajectory. The IRGC's successful Qased/Noor program "
                "demonstrates that Iran can achieve orbit with solid-fuel technology, which "
                "is militarily significant (rapid launch preparation). The use of a Russian "
                "Soyuz to launch the Khayyam satellite (2022) suggests Iran may seek "
                "foreign assistance to compensate for domestic SLV limitations. Iran does "
                "not currently pose a meaningful counter-space threat to FVEY satellites, "
                "but the progression from SLV technology to ASAT capability is historically "
                "demonstrated by other nations."
            ),
            "intelligence_gaps": [
                "Actual capability and imagery quality of Noor satellites",
                "Timeline for next-generation Iranian SLV (larger payload to orbit)",
                "Extent of Iranian-Russian space technology cooperation",
                "IRGC plans for military satellite constellation",
                "Electronic warfare capability development against satellite signals",
            ],
            "trend": "SLOWLY ESCALATING — Reliable orbital access being established",
            "evidence": (
                "CSIS Missile Threat; SWF Global Counterspace; IISS Military Balance; "
                "ISA public announcements; IRGC media"
            ),
        },
    }

    return assessments.get(country)


# ---------------------------------------------------------------------------
# get_conflict_scenarios — potential space conflict escalation scenarios
# ---------------------------------------------------------------------------

def get_conflict_scenarios() -> List[dict]:
    """Return potential space conflict escalation scenarios.

    These are analytical constructs based on publicly available strategic analysis,
    wargame findings, and academic literature. They represent plausible pathways,
    not predictions.
    """
    return [
        {
            "id": "SCENARIO-01",
            "title": "Taiwan Strait Crisis — Space Operations",
            "adversary": "PRC",
            "severity": SEVERITY_CRITICAL,
            "probability_assessment": "plausible",
            "description": (
                "In a Taiwan contingency, PRC would likely conduct a comprehensive "
                "counter-space campaign as part of integrated joint operations. The "
                "sequence could include: (1) Pre-conflict: cyber intrusions in ground "
                "segment networks, positioning of inspector satellites near key US "
                "assets, GPS spoofing in the Western Pacific; (2) Onset: ground-based "
                "laser dazzling of ISR satellites over the theater, SATCOM jamming to "
                "degrade US C2, DA-ASAT use against 1-2 high-value ISR satellites to "
                "demonstrate resolve and create intelligence gaps; (3) Sustained: "
                "continued EW against GPS/SATCOM, co-orbital operations against GEO "
                "SIGINT assets, cyber attacks on ground processing."
            ),
            "fvey_impact": (
                "Loss of ISR coverage over the Taiwan Strait during critical early hours. "
                "GPS degradation affecting precision munitions. SATCOM disruption impacting "
                "C2 between INDOPACOM and deployed forces. Potential loss of early warning "
                "coverage creating nuclear escalation ambiguity."
            ),
            "escalation_risks": (
                "DA-ASAT use against US satellites crosses a threshold with unpredictable "
                "consequences. Attack on SBIRS/early warning could be interpreted as "
                "nuclear first-strike preparation. Debris from ASAT use threatens PRC's "
                "own satellite constellation."
            ),
            "key_indicators": [
                "Increased PRC inspector satellite maneuvering near US assets",
                "Unusual Yuan Wang tracking ship deployments",
                "Cyber probing of satellite ground networks (CISA alerts)",
                "PRC ASAT-capable missile movement detected at Plesetsk-equivalent sites",
                "PRC space surveillance radar and optical sensor activation increases",
            ],
            "evidence": "CSIS Taiwan wargame findings (2023); RAND space escalation studies; academic literature",
        },
        {
            "id": "SCENARIO-02",
            "title": "Baltic/NATO Escalation — Russian Counter-Space Operations",
            "adversary": "Russia",
            "severity": SEVERITY_HIGH,
            "probability_assessment": "plausible",
            "description": (
                "In a NATO-Russia confrontation (e.g., Baltic state incursion), Russia "
                "could employ counter-space operations to degrade NATO C4ISR: (1) Immediate: "
                "GPS jamming/spoofing across the Baltic region (already demonstrated in "
                "exercises), SATCOM jamming targeting NATO military frequencies; (2) Escalation: "
                "Peresvet laser deployment to blind ISR satellites during ground operations, "
                "cyberattack against commercial SATCOM supporting NATO (repeat of Viasat "
                "playbook); (3) Maximum: Nudol DA-ASAT use against NATO ISR satellites, "
                "co-orbital attack on GEO SIGINT assets."
            ),
            "fvey_impact": (
                "NATO forces highly dependent on GPS for precision fires and maneuver. "
                "SATCOM disruption would severely impact alliance C2 coordination. "
                "ISR gaps would reduce situational awareness during fast-moving ground "
                "operations."
            ),
            "escalation_risks": (
                "Russian counter-space escalation ladder is unclear — where do they "
                "draw the line between reversible (EW) and irreversible (kinetic) effects? "
                "NATO response to ASAT use is undefined. Risk of nuclear escalation if "
                "early warning systems are targeted."
            ),
            "key_indicators": [
                "Increased GPS interference detected in Baltic/Nordic region",
                "Nudol/Plesetsk test launch activity",
                "Inspector satellite repositioning near NATO space assets",
                "Russian cyber activity targeting NATO satellite operators",
                "Unusual activity at Voronezh radar sites",
            ],
            "evidence": "NATO space policy documents; RAND Russia-NATO scenarios; Baltic air policing data on GPS interference",
        },
        {
            "id": "SCENARIO-03",
            "title": "Grey Zone Counter-Space Campaign (Below Threshold)",
            "adversary": "PRC/Russia",
            "severity": SEVERITY_HIGH,
            "probability_assessment": "likely",
            "description": (
                "An adversary conducts sustained, deniable counter-space operations below "
                "the threshold of armed conflict: (1) Persistent GPS spoofing in contested "
                "areas (South China Sea, Eastern Mediterranean) — already occurring; "
                "(2) Laser dazzling of ISR satellites over sensitive areas with plausible "
                "deniability; (3) Inspector satellite close approaches claimed as 'space "
                "debris avoidance' or 'technology demonstration'; (4) Cyber intrusions "
                "in satellite ground networks for intelligence collection and pre-positioning; "
                "(5) Electromagnetic interference against SATCOM with attribution challenges."
            ),
            "fvey_impact": (
                "Gradual erosion of space-based advantage without triggering a military "
                "response. Intelligence degradation from ISR satellite harassment. "
                "Increased operational costs from continuous maneuvering to avoid "
                "inspector satellites. Diminished confidence in space systems reliability."
            ),
            "escalation_risks": (
                "Primary risk is normalization of hostile space behavior. Each unresponded-to "
                "provocation shifts the baseline of acceptable behavior. May eventually "
                "embolden kinetic action if adversary assesses no red lines exist."
            ),
            "key_indicators": [
                "Pattern of ISR satellite sensor anomalies over specific regions",
                "Increased conjunction warnings involving adversary satellites",
                "GPS interference events correlated with military exercises",
                "Cyber intrusion attempts targeting satellite operators",
                "Adversary SSA sensor activation correlated with FVEY satellite passes",
            ],
            "evidence": "SWF reports on RPO incidents; C4ADS GPS interference data; CSIS grey zone analysis",
        },
        {
            "id": "SCENARIO-04",
            "title": "Cascading Debris Event (Kessler Syndrome)",
            "adversary": "Environmental/All",
            "severity": SEVERITY_HIGH,
            "probability_assessment": "possible_long_term",
            "description": (
                "A collision between large objects in a crowded LEO band triggers a "
                "cascading series of collisions. This could be initiated by: (1) An "
                "ASAT test creating debris in a crowded band (as the 2007 PRC and 2021 "
                "Russian tests did); (2) An accidental collision between a defunct "
                "rocket body and operational satellite; (3) A deliberate attack designed "
                "to trigger cascade. The resulting debris field grows exponentially over "
                "years/decades, rendering specific altitude bands unusable."
            ),
            "fvey_impact": (
                "Loss of LEO satellite capabilities in affected bands — potentially "
                "including ISR, weather, communications. Mega-constellations (Starlink, "
                "SDA) would be severely impacted. Launch windows through debris bands "
                "become restricted. Long-term: decades to centuries before affected "
                "orbits are usable again."
            ),
            "escalation_risks": (
                "A Kessler event would harm all spacefaring nations including the "
                "initiator. However, it would disproportionately harm the nation "
                "most dependent on LEO assets — currently the US/FVEY. An adversary "
                "that calculated it could absorb the losses better than the US might "
                "view deliberate cascade initiation as a strategic option."
            ),
            "key_indicators": [
                "Large conjunction events involving massive debris (rocket bodies, defunct satellites)",
                "Adversary ASAT tests in crowded orbital bands",
                "Failure of debris mitigation (post-mission disposal) compliance",
                "Uncontrolled reentries of large rocket stages through LEO bands",
            ],
            "evidence": "Kessler & Cour-Palais (1978); NASA ODPO models; ESA MASTER model; 18 SDS conjunction data",
        },
        {
            "id": "SCENARIO-05",
            "title": "Electromagnetic Pulse (EMP) / High-Altitude Nuclear Detonation",
            "adversary": "Russia/PRC/DPRK",
            "severity": SEVERITY_CRITICAL,
            "probability_assessment": "unlikely_but_catastrophic",
            "description": (
                "A nuclear detonation at high altitude (100-400 km) would create an "
                "intense electromagnetic pulse (EMP) and a persistent radiation belt "
                "that would degrade or destroy unshielded satellites transiting the "
                "affected region for months to years. The 1962 Starfish Prime test "
                "(400 km, 1.4 MT) disabled multiple satellites. A modern weapon in "
                "LEO could damage hundreds of satellites. This represents the most "
                "extreme counter-space scenario."
            ),
            "fvey_impact": (
                "Potential loss of significant fraction of LEO satellite constellation. "
                "Radiation belt degradation of solar cells and electronics over weeks/months. "
                "GPS and GEO satellites potentially affected depending on detonation altitude. "
                "Civilian infrastructure (EMP ground effects) catastrophically impacted."
            ),
            "escalation_risks": (
                "Nuclear detonation in space would constitute use of nuclear weapons — "
                "extreme escalation. However, an adversary facing conventional defeat "
                "might view space nuclear detonation as less escalatory than nuclear "
                "use against population centres. The 1967 Outer Space Treaty prohibits "
                "nuclear weapons in space but compliance is by agreement only."
            ),
            "key_indicators": [
                "Adversary nuclear posture changes",
                "Statements about nuclear de-escalation or space denial",
                "ICBM/SLBM test flights with unusual lofted trajectories",
                "Intelligence on nuclear warhead modifications for space detonation",
            ],
            "evidence": "Starfish Prime test data (1962); EMP Commission reports; CRS nuclear EMP analysis; OST Article IV",
        },
    ]
