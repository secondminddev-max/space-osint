"""
Launch Library 2 — upcoming launches
https://ll.thespacedevs.com/2.2.0/
Rate limit: 15 req/hr (free tier)
"""
import time
import httpx
from config import CACHE_TTL_LAUNCHES

_cache = {}
_URL = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=15&format=json"


async def fetch_launches(client: httpx.AsyncClient) -> list:
    now = time.time()
    cached = _cache.get("launches")
    if cached and (now - cached["ts"]) < CACHE_TTL_LAUNCHES:
        return cached["data"]

    try:
        r = await client.get(_URL, timeout=20)
        r.raise_for_status()
        raw = r.json()
    except Exception:
        return _cache.get("launches", {}).get("data", [])

    launches = []
    for item in raw.get("results", []):
        pad = item.get("pad", {})
        rocket = item.get("rocket", {})
        rocket_config = rocket.get("configuration", {}) if rocket else {}
        provider = item.get("launch_service_provider", {})
        status = item.get("status", {})

        launches.append({
            "id": item.get("id", ""),
            "name": item.get("name", ""),
            "net": item.get("net", ""),
            "window_start": item.get("window_start", ""),
            "window_end": item.get("window_end", ""),
            "status": {
                "id": status.get("id"),
                "name": status.get("name", ""),
                "abbrev": status.get("abbrev", ""),
            },
            "provider": provider.get("name", "Unknown"),
            "rocket": rocket_config.get("full_name", rocket_config.get("name", "Unknown")),
            "mission": item.get("mission", {}).get("name", "") if item.get("mission") else "",
            "mission_type": item.get("mission", {}).get("type", "") if item.get("mission") else "",
            "pad_name": pad.get("name", ""),
            "pad_location": pad.get("location", {}).get("name", "") if pad.get("location") else "",
            "image": item.get("image", ""),
            "probability": item.get("probability"),
            "webcast_live": item.get("webcast_live", False),
        })

    _cache["launches"] = {"data": launches, "ts": now}
    return launches
