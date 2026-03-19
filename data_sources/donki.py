"""
NASA DONKI — Space Weather Events
Coronal Mass Ejections (CME) and Solar Flares (FLR)
https://api.nasa.gov/DONKI/
"""
import time
from datetime import datetime, timedelta
import httpx
from config import CACHE_TTL_DONKI, NASA_API_KEY

_cache = {}
_BASE = "https://api.nasa.gov/DONKI"


async def fetch_cme(client: httpx.AsyncClient) -> list:
    now = time.time()
    cached = _cache.get("cme")
    if cached and (now - cached["ts"]) < CACHE_TTL_DONKI:
        return cached["data"]

    start = (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d")
    url = f"{_BASE}/CME?startDate={start}&api_key={NASA_API_KEY}"

    try:
        r = await client.get(url, timeout=20)
        r.raise_for_status()
        raw = r.json()
    except Exception:
        return _cache.get("cme", {}).get("data", [])

    events = []
    if isinstance(raw, list):
        for cme in raw[-20:]:
            analysis = cme.get("cmeAnalyses", [{}])
            latest = analysis[-1] if analysis else {}
            events.append({
                "id": cme.get("activityID", ""),
                "time": cme.get("startTime", ""),
                "source_location": cme.get("sourceLocation", ""),
                "note": cme.get("note", "")[:300],
                "speed": latest.get("speed", None),
                "type": latest.get("type", ""),
                "is_earth_directed": latest.get("isMostAccurate", False),
            })

    _cache["cme"] = {"data": events, "ts": now}
    return events


async def fetch_flares(client: httpx.AsyncClient) -> list:
    now = time.time()
    cached = _cache.get("flr")
    if cached and (now - cached["ts"]) < CACHE_TTL_DONKI:
        return cached["data"]

    start = (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d")
    url = f"{_BASE}/FLR?startDate={start}&api_key={NASA_API_KEY}"

    try:
        r = await client.get(url, timeout=20)
        r.raise_for_status()
        raw = r.json()
    except Exception:
        return _cache.get("flr", {}).get("data", [])

    flares = []
    if isinstance(raw, list):
        for flr in raw[-20:]:
            flares.append({
                "id": flr.get("flrID", ""),
                "begin_time": flr.get("beginTime", ""),
                "peak_time": flr.get("peakTime", ""),
                "end_time": flr.get("endTime", ""),
                "class_type": flr.get("classType", ""),
                "source_location": flr.get("sourceLocation", ""),
            })

    _cache["flr"] = {"data": flares, "ts": now}
    return flares
