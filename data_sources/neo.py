"""
NASA Near-Earth Object API
https://api.nasa.gov/neo/
"""
import time
from datetime import datetime, timedelta
import httpx
from config import CACHE_TTL_NEO, NASA_API_KEY

_cache = {}


async def fetch_neo(client: httpx.AsyncClient) -> list:
    now = time.time()
    cached = _cache.get("neo")
    if cached and (now - cached["ts"]) < CACHE_TTL_NEO:
        return cached["data"]

    today = datetime.utcnow().strftime("%Y-%m-%d")
    end = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={end}&api_key={NASA_API_KEY}"

    try:
        r = await client.get(url, timeout=30)
        r.raise_for_status()
        raw = r.json()
    except Exception:
        return _cache.get("neo", {}).get("data", [])

    objects = []
    for date_str, neos in raw.get("near_earth_objects", {}).items():
        for neo in neos:
            approach = neo.get("close_approach_data", [{}])[0] if neo.get("close_approach_data") else {}
            diameter = neo.get("estimated_diameter", {}).get("meters", {})

            objects.append({
                "id": neo.get("id", ""),
                "name": neo.get("name", "").strip("()"),
                "is_hazardous": neo.get("is_potentially_hazardous_asteroid", False),
                "close_approach_date": approach.get("close_approach_date_full", date_str),
                "miss_distance_km": float(approach.get("miss_distance", {}).get("kilometers", 0)),
                "miss_distance_lunar": float(approach.get("miss_distance", {}).get("lunar", 0)),
                "velocity_kms": float(approach.get("relative_velocity", {}).get("kilometers_per_second", 0)),
                "diameter_min_m": diameter.get("estimated_diameter_min", 0),
                "diameter_max_m": diameter.get("estimated_diameter_max", 0),
                "nasa_url": neo.get("nasa_jpl_url", ""),
            })

    objects.sort(key=lambda x: x["close_approach_date"])
    _cache["neo"] = {"data": objects, "ts": now}
    return objects
