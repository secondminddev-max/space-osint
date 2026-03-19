"""
Global Space OSINT Operating Centre — Server
FastAPI backend: live API aggregation + structured intelligence databases.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from config import HOST, PORT
from data_sources import (
    space_weather, news, launches, neo, astronauts, donki, celestrak,
    adversary_sats, ground_stations, missile_intel, threat_assessment,
    researcher, live_intel, social_monitor,
    proximity_alert, threat_timeline, incident_db,
    overmatch, wargame,
    futures, conferences, architecture,
    enhanced_feeds,
    deep_analysis,
    advanced_intel,
    deduction_engine,
    final_features,
    global_feeds,
    sigint_feeds,
)

_client: httpx.AsyncClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _client
    _client = httpx.AsyncClient(
        headers={"User-Agent": "SpaceOSINT/1.0"},
        follow_redirects=True,
        timeout=60,
    )
    try:
        await celestrak.fetch_catalog(_client, "stations")
        print("[BOOT] Station catalog loaded")
    except Exception as e:
        print(f"[BOOT] Station catalog failed: {e}")
    yield
    await _client.aclose()


app = FastAPI(title="Space OSINT Operating Centre", lifespan=lifespan)

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ---- Core Routes ----

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "landing.html"))

@app.get("/app")
async def dashboard():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/landing")
async def landing():
    return FileResponse(os.path.join(static_dir, "landing.html"))


# ---- Catalog Proxy (allows instances with blocked CelesTrak to fetch via this server) ----

@app.get("/api/catalog-proxy")
async def api_catalog_proxy(group: str = "active"):
    """Proxy CelesTrak GP data for instances where CelesTrak is blocked."""
    data = await celestrak.fetch_catalog(_client, group)
    return JSONResponse(data)


# ---- Live Data APIs ----

@app.get("/api/satellites")
async def api_satellites(group: str = "stations"):
    return JSONResponse(await celestrak.get_satellite_positions(_client, group))

@app.get("/api/satellites/stats")
async def api_satellite_stats():
    return JSONResponse(await celestrak.get_satellite_stats(_client))

@app.get("/api/satellites/track/{norad_id}")
async def api_satellite_track(norad_id: int):
    for group in ["stations", "active"]:
        catalog = await celestrak.fetch_catalog(_client, group)
        for gp in catalog:
            if int(gp.get("NORAD_CAT_ID", 0)) == norad_id:
                return JSONResponse(celestrak.compute_ground_track(gp))
    return JSONResponse([])

@app.get("/api/launches")
async def api_launches():
    return JSONResponse(await launches.fetch_launches(_client))

@app.get("/api/weather")
async def api_weather():
    return JSONResponse(await space_weather.fetch_weather_composite(_client))

@app.get("/api/weather/kp-history")
async def api_kp_history():
    return JSONResponse(await space_weather.fetch_kp_history(_client))

@app.get("/api/neo")
async def api_neo():
    return JSONResponse(await neo.fetch_neo(_client))

@app.get("/api/news")
async def api_news():
    return JSONResponse(await news.fetch_news(_client))

@app.get("/api/astronauts")
async def api_astronauts():
    return JSONResponse(await astronauts.fetch_astronauts(_client))

@app.get("/api/donki/cme")
async def api_donki_cme():
    return JSONResponse(await donki.fetch_cme(_client))

@app.get("/api/donki/flares")
async def api_donki_flares():
    return JSONResponse(await donki.fetch_flares(_client))


# ---- Adversary Intelligence APIs ----

@app.get("/api/adversary/satellites")
async def api_adversary_sats(country: str = "all"):
    if country == "all":
        data = {}
        for c in ["PRC", "CIS", "NKOR", "IRAN"]:
            data[c] = await adversary_sats.get_adversary_satellites(_client, c)
        return JSONResponse(data)
    return JSONResponse(await adversary_sats.get_adversary_satellites(_client, country.upper()))

@app.get("/api/adversary/stats")
async def api_adversary_stats():
    return JSONResponse(await adversary_sats.get_adversary_stats(_client))

@app.get("/api/fvey/satellites")
async def api_fvey_sats(country: str = "all"):
    if country == "all":
        data = {}
        for c in ["US", "UK", "CA", "AU", "NZ"]:
            data[c] = await adversary_sats.get_fvey_satellites(_client, c)
        return JSONResponse(data)
    return JSONResponse(await adversary_sats.get_fvey_satellites(_client, country.upper()))


# ---- Ground Stations / Infrastructure ----

@app.get("/api/ground-stations")
async def api_ground_stations(scope: str = "all"):
    if scope == "adversary":
        return JSONResponse(ground_stations.get_adversary_stations())
    elif scope == "fvey":
        return JSONResponse(ground_stations.get_fvey_stations())
    elif scope != "all":
        return JSONResponse(ground_stations.get_stations_by_country(scope.upper()))
    return JSONResponse(ground_stations.get_all_stations())

@app.get("/api/ground-stations/summary")
async def api_ground_stations_summary():
    return JSONResponse(ground_stations.get_stations_summary())


# ---- Missile & ASAT Intelligence ----

@app.get("/api/missile-asat")
async def api_missile_asat(country: str = "", threat: str = "", type: str = ""):
    if country:
        return JSONResponse(missile_intel.get_by_country(country.upper()))
    if threat:
        return JSONResponse(missile_intel.get_by_threat_level(threat.lower()))
    if type:
        return JSONResponse(missile_intel.get_by_type(type.lower()))
    return JSONResponse(missile_intel.get_missile_asat_data())

@app.get("/api/missile-asat/summary")
async def api_missile_summary():
    return JSONResponse(missile_intel.get_threat_summary())


# ---- Strategic Assessments ----

@app.get("/api/threat/overview")
async def api_threat_overview():
    return JSONResponse(await threat_assessment.generate_threat_overview(_client))

@app.get("/api/threat/vulnerabilities")
async def api_vulnerabilities():
    return JSONResponse(threat_assessment.get_fvey_vulnerabilities())

@app.get("/api/threat/recommendations")
async def api_recommendations():
    return JSONResponse(threat_assessment.get_policy_recommendations())

@app.get("/api/threat/adversary/{country}")
async def api_adversary_assessment(country: str):
    return JSONResponse(threat_assessment.get_adversary_assessment(country.upper()))

@app.get("/api/threat/scenarios")
async def api_conflict_scenarios():
    return JSONResponse(threat_assessment.get_conflict_scenarios())


# ---- Intelligence Research & Analysis ----

@app.get("/api/intel/research")
async def api_intel_research():
    """Aggregated research feed from all open intelligence sources."""
    return JSONResponse(await researcher.fetch_research_feed(_client))

@app.get("/api/intel/arxiv")
async def api_intel_arxiv():
    """Academic research papers on space security from ArXiv."""
    return JSONResponse(await researcher.fetch_arxiv_papers(_client))

@app.get("/api/intel/sitrep")
async def api_intel_sitrep():
    """Live situation report — real-time threat assessment."""
    return JSONResponse(await live_intel.generate_situation_report(_client))

@app.get("/api/intel/brief")
async def api_intel_brief():
    """Daily intelligence brief — comprehensive daily assessment."""
    return JSONResponse(await live_intel.generate_daily_brief(_client))

@app.get("/api/intel/hotspots")
async def api_intel_hotspots():
    """Strategic area coverage analysis — adversary ISR over key hotspots."""
    return JSONResponse(await live_intel.get_hotspot_analysis(_client))

@app.get("/api/intel/coverage")
async def api_intel_coverage(
    lat: float = Query(23.5, description="Latitude of area of interest"),
    lng: float = Query(120.5, description="Longitude of area of interest"),
    radius: float = Query(1500, description="Detection radius in km"),
):
    """Check adversary ISR satellite coverage over a specific area."""
    return JSONResponse(
        await live_intel.get_area_of_interest_coverage(_client, lat, lng, radius)
    )

@app.get("/api/intel/social")
async def api_intel_social():
    """Social media intelligence feed — Bluesky and Reddit."""
    return JSONResponse(await social_monitor.fetch_social_intel(_client))


# ---- FVEY Proximity Alerting ----

@app.get("/api/intel/proximity")
async def api_proximity_alerts(threshold: float = Query(500, description="Alert threshold in km")):
    """FVEY asset proximity alerting — adversary sats near FVEY military sats."""
    return JSONResponse(await proximity_alert.check_proximity_alerts(_client, threshold))

@app.get("/api/intel/proximity/history")
async def api_proximity_history():
    """Rolling history of close-approach events."""
    return JSONResponse(await proximity_alert.get_proximity_history(_client))


# ---- Predictive Threat Timelines ----

@app.get("/api/intel/predict")
async def api_predict_timeline(
    lat: float = Query(23.5, description="Latitude of area of interest"),
    lng: float = Query(120.5, description="Longitude of area of interest"),
    name: str = Query("Custom AOI", description="Name of the area"),
    hours: int = Query(72, description="Prediction window in hours (max 72)"),
):
    """72-hour predictive adversary ISR coverage timeline for an area of interest."""
    hours = min(hours, 72)
    return JSONResponse(
        await threat_timeline.predict_coverage_timeline(_client, lat, lng, name, hours)
    )

@app.get("/api/intel/predict/hotspots")
async def api_predict_hotspots():
    """72-hour predictive coverage timelines for all strategic hotspots."""
    return JSONResponse(await threat_timeline.predict_all_hotspot_timelines(_client))

@app.get("/api/intel/coverage-density")
async def api_coverage_density(
    lat: float = Query(23.5, description="Latitude of area of interest"),
    lng: float = Query(120.5, description="Longitude of area of interest"),
    hours: int = Query(24, description="Analysis window in hours (max 72)"),
):
    """Hourly adversary ISR satellite coverage density over an area."""
    hours = min(hours, 72)
    return JSONResponse(
        await threat_timeline.get_coverage_density(_client, lat, lng, hours)
    )


# ---- Space Security Incident Database ----

@app.get("/api/incidents/stats")
async def api_incident_stats():
    """Space security incident summary statistics."""
    return JSONResponse(incident_db.get_incident_stats())

@app.get("/api/incidents")
async def api_incidents(
    type: str = Query("", description="Filter by type: DA-ASAT, co-orbital, cyber, collision, EW, test"),
    actor: str = Query("", description="Filter by actor: PRC, CIS, US, India, Iran"),
    year: int = Query(0, description="Filter by year"),
):
    """Historical space security incident database — all documented events."""
    if type:
        return JSONResponse(incident_db.get_incidents_by_type(type))
    if actor:
        return JSONResponse(incident_db.get_incidents_by_actor(actor))
    if year > 0:
        return JSONResponse(incident_db.get_incidents_by_year(year))
    return JSONResponse(incident_db.get_all_incidents())


# ---- Overmatch Calculator ----

@app.get("/api/overmatch")
async def api_overmatch():
    """Real-time overmatch calculation for all strategic zones."""
    return JSONResponse(await overmatch.calculate_all_overmatches(_client))

@app.get("/api/overmatch/zone")
async def api_overmatch_zone(
    lat: float = Query(23.5, description="Zone center latitude"),
    lng: float = Query(120.5, description="Zone center longitude"),
    name: str = Query("Custom Zone", description="Zone name"),
):
    """Overmatch calculation for a single zone by coordinates."""
    return JSONResponse(
        await overmatch.calculate_zone_overmatch(_client, lat, lng, name)
    )

@app.get("/api/overmatch/summary")
async def api_overmatch_summary():
    """Global overmatch summary — aggregate score across all zones."""
    return JSONResponse(await overmatch.get_global_overmatch_summary(_client))


# ---- Wargame Simulator ----

@app.get("/api/wargame/scenarios")
async def api_wargame_scenarios():
    """List all available wargame scenarios."""
    return JSONResponse(wargame.get_all_scenarios())

@app.get("/api/wargame/run/{scenario_id}")
async def api_wargame_run(scenario_id: str):
    """Execute a specific wargame scenario."""
    result = wargame.run_scenario(scenario_id)
    if result is None:
        return JSONResponse(
            {"error": f"Scenario '{scenario_id}' not found", "available": list(wargame._SCENARIOS.keys())},
            status_code=404,
        )
    return JSONResponse(result)

@app.get("/api/wargame/full-spectrum")
async def api_wargame_full_spectrum():
    """Worst-case full spectrum counter-space attack scenario."""
    return JSONResponse(wargame.run_full_spectrum_assessment())

@app.get("/api/wargame/resilience")
async def api_wargame_resilience():
    """FVEY reconstitution and resilience assessment."""
    return JSONResponse(wargame.assess_fvey_resilience())


# ---- Future Space Programs ----

@app.get("/api/futures/summary")
async def api_futures_summary():
    """Summary statistics of all future space programs."""
    return JSONResponse(futures.get_futures_summary())

@app.get("/api/futures")
async def api_futures(nation: str = "", domain: str = "", year: int = 0):
    """Future space programs — all nations, filterable by nation, domain, or year."""
    if nation:
        return JSONResponse(futures.get_futures_by_nation(nation))
    if domain:
        return JSONResponse(futures.get_futures_by_domain(domain))
    if year > 0:
        return JSONResponse(futures.get_futures_by_timeline(year))
    return JSONResponse(futures.get_all_futures())


# ---- Space Conferences & Events ----

@app.get("/api/conferences/upcoming")
async def api_conferences_upcoming():
    """Upcoming space conferences in the next 12 months."""
    return JSONResponse(conferences.get_upcoming_conferences())

@app.get("/api/conferences/calendar")
async def api_conferences_calendar():
    """Month-by-month conference calendar."""
    return JSONResponse(conferences.get_conference_calendar())

@app.get("/api/conferences/live")
async def api_conferences_live():
    """Live events from Spaceflight News API."""
    return JSONResponse(await conferences.fetch_live_events(_client))

@app.get("/api/conferences")
async def api_conferences(relevance: str = ""):
    """All space conferences and events, optionally filtered by FVEY relevance."""
    if relevance:
        return JSONResponse(conferences.get_conferences_by_relevance(relevance))
    return JSONResponse(conferences.get_all_conferences())


# ---- Ground Architecture Analysis ----

@app.get("/api/architecture/prc")
async def api_architecture_prc():
    """Detailed PRC space ground segment architecture analysis."""
    return JSONResponse(architecture.get_prc_architecture())

@app.get("/api/architecture/russia")
async def api_architecture_russia():
    """Detailed Russian space ground segment architecture analysis."""
    return JSONResponse(architecture.get_russia_architecture())

@app.get("/api/architecture/fvey")
async def api_architecture_fvey():
    """Detailed FVEY space ground segment architecture analysis."""
    return JSONResponse(architecture.get_fvey_architecture())

@app.get("/api/architecture/comparison")
async def api_architecture_comparison():
    """Side-by-side comparison of adversary vs FVEY ground capabilities."""
    return JSONResponse(architecture.get_architecture_comparison())


# ---- Enhanced Space Environment ----

@app.get("/api/environment/solar-images")
async def api_solar_images():
    """Latest solar imagery — SUVI EUV, SDO/HMI, LASCO coronagraph, ENLIL model."""
    return JSONResponse(await enhanced_feeds.fetch_solar_imagery(_client))

@app.get("/api/environment/aurora")
async def api_aurora():
    """Aurora probability grid + forecast imagery (NOAA OVATION model)."""
    return JSONResponse(await enhanced_feeds.fetch_aurora_data(_client))

@app.get("/api/environment/solar-wind-history")
async def api_solar_wind_history():
    """7-day solar wind plasma + magnetic field history."""
    return JSONResponse(await enhanced_feeds.fetch_solar_wind_history(_client))

@app.get("/api/environment/geospace")
async def api_geospace():
    """Propagated solar wind at Earth's magnetopause — real-time driving conditions."""
    return JSONResponse(await enhanced_feeds.fetch_geospace_data(_client))

@app.get("/api/environment/debris-alerts")
async def api_debris_alerts():
    """Space debris awareness — new catalog objects, particle alerts, ICAO advisories."""
    return JSONResponse(await enhanced_feeds.fetch_debris_alerts(_client))

@app.get("/api/environment/goes")
async def api_goes_instruments():
    """GOES satellite instrument data — X-ray, proton flux, magnetometer."""
    return JSONResponse(await enhanced_feeds.fetch_goes_data(_client))

@app.get("/api/environment/solar-activity")
async def api_solar_activity():
    """Solar flare probabilities + active sunspot regions."""
    return JSONResponse(await enhanced_feeds.fetch_solar_activity(_client))

@app.get("/api/environment/forecasts")
async def api_forecasts():
    """Kp forecast, 45-day Ap/F10.7 outlook, electron fluence forecast."""
    return JSONResponse(await enhanced_feeds.fetch_forecasts(_client))

@app.get("/api/environment/enlil")
async def api_enlil():
    """WSA-ENLIL solar wind model — predicted conditions and CME arrivals."""
    return JSONResponse(await enhanced_feeds.fetch_enlil_model(_client))

@app.get("/api/environment/enhanced")
async def api_enhanced_environment():
    """Master composite of ALL enhanced environmental data in one call."""
    return JSONResponse(await enhanced_feeds.get_enhanced_environment(_client))


# ---- Deep Intelligence Analysis ----

@app.get("/api/analysis/constellation/{name}")
async def api_analysis_constellation(name: str):
    """In-depth adversary constellation analysis — coverage, capability, countermeasures."""
    result = await deep_analysis.analyze_constellation(_client, name)
    if result is None:
        return JSONResponse(
            {
                "error": f"Unknown constellation '{name}'",
                "available": deep_analysis.get_available_constellations(),
            },
            status_code=404,
        )
    return JSONResponse(result)

@app.get("/api/analysis/correlations")
async def api_analysis_correlations():
    """Threat correlation engine — cross-source intelligence notes."""
    return JSONResponse(await deep_analysis.correlate_threats(_client))

@app.get("/api/analysis/orbat")
async def api_analysis_orbat():
    """Space Order of Battle — formal ORBAT for all adversary nations."""
    return JSONResponse(await deep_analysis.generate_orbat(_client))

@app.get("/api/analysis/daily-summary")
async def api_analysis_daily_summary():
    """Daily intelligence summary — structured morning brief."""
    return JSONResponse(await deep_analysis.generate_daily_summary(_client))


# ---- Advanced Space Intelligence ----

@app.get("/api/analysis/rpo-risks")
async def api_rpo_risks():
    """RPO Risk Monitor — adversary satellites in similar orbits to FVEY military assets."""
    return JSONResponse(await advanced_intel.check_rpo_risks(_client))

@app.get("/api/analysis/debris-cascade")
async def api_debris_cascade(
    altitude: float = Query(800, description="Intercept altitude in km"),
    mass: float = Query(1000, description="Target satellite mass in kg"),
):
    """Debris Cascade Risk Calculator — ASAT event debris modeling and FVEY impact."""
    return JSONResponse(advanced_intel.calculate_debris_cascade(altitude, mass))

@app.get("/api/analysis/weather-impact")
async def api_weather_impact():
    """Space Weather Operational Impact — translates weather to FVEY ops impact."""
    return JSONResponse(await advanced_intel.assess_space_weather_impact(_client))

@app.get("/api/analysis/launch-windows")
async def api_launch_windows(
    site_lat: float = Query(40.96, description="Launch site latitude"),
    site_lng: float = Query(100.28, description="Launch site longitude"),
    target_orbit: str = Query("SSO", description="Target orbit: SSO, LEO, GEO, MEO, Molniya"),
):
    """Launch Window Predictor — adversary launch site orbital mechanics constraints."""
    return JSONResponse(advanced_intel.predict_launch_windows(site_lat, site_lng, target_orbit))

@app.get("/api/analysis/treaties")
async def api_treaties():
    """Treaty & Norms Tracker — space governance frameworks and FVEY positions."""
    return JSONResponse(advanced_intel.get_treaty_status())

@app.get("/api/analysis/spectrum")
async def api_spectrum():
    """Electromagnetic Spectrum Assessment — EW threats and natural environment."""
    return JSONResponse(await advanced_intel.get_spectrum_assessment(_client))


# ---- AI Deduction Engine ----

@app.get("/api/deductions")
async def api_deductions(category: str = ""):
    """AI Deduction Engine — all deductions, optionally filtered by category."""
    if category:
        return JSONResponse(
            await deduction_engine.get_deductions_by_category(_client, category)
        )
    return JSONResponse(await deduction_engine.generate_deductions(_client))

@app.get("/api/deductions/priority")
async def api_deductions_priority():
    """AI Deduction Engine — top 10 highest-priority deductions."""
    return JSONResponse(await deduction_engine.get_priority_deductions(_client))

@app.get("/api/deductions/narrative")
async def api_deductions_narrative():
    """AI Deduction Engine — cohesive analytical threat narrative document."""
    return JSONResponse(await deduction_engine.generate_threat_narrative(_client))


# ---- Final Features: Alliance / IPOE / SIGINT / Debris / Cislunar ----

@app.get("/api/analysis/alliances")
async def api_alliances():
    """AUKUS/FVEY/CSpO/NATO/Quad space cooperation status and allied ground segment."""
    return JSONResponse(final_features.get_alliance_status())

@app.get("/api/analysis/ipoe")
async def api_ipoe():
    """Space Intelligence Preparation of the Operating Environment (IPOE) — JP 2-01.3 format."""
    return JSONResponse(await final_features.generate_space_ipoe(_client))

@app.get("/api/analysis/maneuver-indicators")
async def api_maneuver_indicators():
    """Satellite maneuver detection indicators — intelligence analyst watchlist."""
    return JSONResponse(final_features.get_maneuver_indicators())

@app.get("/api/analysis/sigint-mapping")
async def api_sigint_mapping():
    """Adversary SIGINT/ELINT constellation intelligence map — PRC and Russia."""
    return JSONResponse(final_features.get_sigint_mapping())

@app.get("/api/analysis/debris-environment")
async def api_debris_environment():
    """Comprehensive space debris environment assessment — catalog, trends, FVEY impact."""
    return JSONResponse(final_features.get_debris_environment())

@app.get("/api/analysis/cislunar")
async def api_cislunar():
    """Cislunar space domain awareness — beyond-GEO objects, lunar missions, surveillance gaps."""
    return JSONResponse(final_features.get_cislunar_status())


# ---- Global Space Environment Feeds ----

@app.get("/api/global/ionosphere")
async def api_global_ionosphere():
    """Global ionospheric TEC map — GPS scintillation and comms impact assessment."""
    return JSONResponse(await global_feeds.fetch_ionosphere_data(_client))

@app.get("/api/global/dscovr")
async def api_global_dscovr():
    """DSCOVR/ACE real-time solar wind at L1 — 15-45 min advance warning for storms."""
    return JSONResponse(await global_feeds.fetch_dscovr_data(_client))

@app.get("/api/global/earth-events")
async def api_global_earth_events():
    """NASA EONET natural events — volcanoes, storms, wildfires affecting ops."""
    return JSONResponse(await global_feeds.fetch_earth_events(_client))

@app.get("/api/global/radiation")
async def api_global_radiation():
    """Van Allen radiation belt conditions + Dst magnetosphere index."""
    return JSONResponse(await global_feeds.fetch_radiation_belts(_client))

@app.get("/api/global/earthquakes")
async def api_global_earthquakes():
    """USGS seismic events M4+ — nuclear test site proximity alerting."""
    return JSONResponse(await global_feeds.fetch_earthquakes(_client))

@app.get("/api/global/solar-radio")
async def api_global_solar_radio():
    """Multi-frequency solar radio flux — RF interference in military bands."""
    return JSONResponse(await global_feeds.fetch_solar_radio(_client))

@app.get("/api/global/epic")
async def api_global_epic():
    """NASA EPIC — DSCOVR full-disk Earth imagery from L1 Lagrange point."""
    return JSONResponse(await global_feeds.fetch_epic_imagery(_client))

@app.get("/api/global/satnogs")
async def api_global_satnogs():
    """SatNOGS community satellite database — amateur radio observations."""
    return JSONResponse(await global_feeds.fetch_satnogs_satellites(_client))

@app.get("/api/global/all")
async def api_global_all():
    """Master composite of ALL global environment feeds in one call."""
    return JSONResponse(await global_feeds.fetch_global_composite(_client))


# ---- Multi-Source SIGINT & Advanced Intelligence ----

@app.get("/api/sigint/satnogs")
async def api_sigint_satnogs():
    """SatNOGS satellite RF observations — global amateur ground station network."""
    return JSONResponse(await sigint_feeds.fetch_satnogs_observations(_client))

@app.get("/api/sigint/thermal")
async def api_sigint_thermal():
    """NASA FIRMS thermal anomaly detection — rocket launch site monitoring."""
    return JSONResponse(await sigint_feeds.fetch_thermal_anomalies(_client))

@app.get("/api/sigint/seismic")
async def api_sigint_seismic():
    """USGS seismic events — nuclear test and ASAT test site correlation."""
    return JSONResponse(await sigint_feeds.fetch_seismic_events(_client))

@app.get("/api/sigint/ionosphere")
async def api_sigint_ionosphere():
    """Ionospheric TEC monitoring — GPS degradation and HEMP detection."""
    return JSONResponse(await sigint_feeds.fetch_ionospheric_tec(_client))

@app.get("/api/sigint/events")
async def api_sigint_events():
    """NASA EONET natural events — operational impact on space infrastructure."""
    return JSONResponse(await sigint_feeds.fetch_natural_events(_client))

@app.get("/api/sigint/composite")
async def api_sigint_composite():
    """Multi-source SIGINT composite — cross-correlated intelligence from all feeds."""
    return JSONResponse(await sigint_feeds.get_multi_source_intel(_client))


# ---- System ----

@app.get("/api/status")
async def api_status():
    return JSONResponse({
        "service": "ECHELON VANTAGE — Space Domain Awareness",
        "status": "operational",
        "version": "7.0.0",
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "operator": "Echelon Vantage Pty Ltd — Australia",
        "capabilities": 83,
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)
