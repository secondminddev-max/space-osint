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


# ---- System ----

@app.get("/api/status")
async def api_status():
    return JSONResponse({
        "service": "ECHELON VANTAGE — Space Domain Awareness",
        "status": "operational",
        "version": "4.0.0",
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "operator": "Echelon Vantage Pty Ltd — Australia",
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)
