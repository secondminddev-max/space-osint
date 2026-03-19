"""
Global Space OSINT Operating Centre — Server
FastAPI backend serving the dashboard and aggregating space data APIs.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from config import HOST, PORT
from data_sources import space_weather, news, launches, neo, astronauts, donki, celestrak

# Shared HTTP client
_client: httpx.AsyncClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _client
    _client = httpx.AsyncClient(
        headers={"User-Agent": "SpaceOSINT/1.0"},
        follow_redirects=True,
    )
    # Pre-fetch station catalog on startup
    try:
        await celestrak.fetch_catalog(_client, "stations")
        print("[BOOT] Station catalog loaded")
    except Exception as e:
        print(f"[BOOT] Station catalog fetch failed: {e}")
    yield
    await _client.aclose()


app = FastAPI(title="Space OSINT Operating Centre", lifespan=lifespan)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# --- Routes ---

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/api/satellites")
async def api_satellites(group: str = "stations"):
    positions = await celestrak.get_satellite_positions(_client, group)
    return JSONResponse(positions)


@app.get("/api/satellites/stats")
async def api_satellite_stats():
    stats = await celestrak.get_satellite_stats(_client)
    return JSONResponse(stats)


@app.get("/api/satellites/track/{norad_id}")
async def api_satellite_track(norad_id: int):
    catalog = await celestrak.fetch_catalog(_client, "stations")
    for gp in catalog:
        if int(gp.get("NORAD_CAT_ID", 0)) == norad_id:
            track = celestrak.compute_ground_track(gp)
            return JSONResponse(track)
    return JSONResponse([])


@app.get("/api/launches")
async def api_launches():
    data = await launches.fetch_launches(_client)
    return JSONResponse(data)


@app.get("/api/weather")
async def api_weather():
    data = await space_weather.fetch_weather_composite(_client)
    return JSONResponse(data)


@app.get("/api/weather/kp-history")
async def api_kp_history():
    data = await space_weather.fetch_kp_history(_client)
    return JSONResponse(data)


@app.get("/api/neo")
async def api_neo():
    data = await neo.fetch_neo(_client)
    return JSONResponse(data)


@app.get("/api/news")
async def api_news():
    data = await news.fetch_news(_client)
    return JSONResponse(data)


@app.get("/api/astronauts")
async def api_astronauts():
    data = await astronauts.fetch_astronauts(_client)
    return JSONResponse(data)


@app.get("/api/donki/cme")
async def api_donki_cme():
    data = await donki.fetch_cme(_client)
    return JSONResponse(data)


@app.get("/api/donki/flares")
async def api_donki_flares():
    data = await donki.fetch_flares(_client)
    return JSONResponse(data)


@app.get("/api/status")
async def api_status():
    return JSONResponse({
        "service": "Space OSINT Operating Centre",
        "status": "operational",
        "version": "1.0.0",
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)
