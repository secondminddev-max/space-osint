"""
People currently in space
Primary: Open Notify API (http://api.open-notify.org/astros.json)
Fallback: hardcoded known crew (updated periodically)
"""
import time
import httpx
from config import CACHE_TTL_ASTRONAUTS

_cache = {}
_URL = "http://api.open-notify.org/astros.json"

# Fallback data — updated manually when Open Notify is down
_FALLBACK_CREW = [
    {"name": "Oleg Kononenko", "craft": "ISS"},
    {"name": "Nikolai Chub", "craft": "ISS"},
    {"name": "Tracy Dyson", "craft": "ISS"},
    {"name": "Matthew Dominick", "craft": "ISS"},
    {"name": "Michael Barratt", "craft": "ISS"},
    {"name": "Jeanette Epps", "craft": "ISS"},
    {"name": "Alexander Grebenkin", "craft": "ISS"},
    {"name": "Li Guangsu", "craft": "Tiangong"},
    {"name": "Li Cong", "craft": "Tiangong"},
    {"name": "Ye Guangfu", "craft": "Tiangong"},
]


async def fetch_astronauts(client: httpx.AsyncClient) -> dict:
    now = time.time()
    cached = _cache.get("astronauts")
    if cached and (now - cached["ts"]) < CACHE_TTL_ASTRONAUTS:
        return cached["data"]

    try:
        r = await client.get(_URL, timeout=10)
        r.raise_for_status()
        raw = r.json()
        if raw.get("message") == "success":
            people = [{"name": p["name"], "craft": p["craft"]} for p in raw.get("people", [])]
            data = {"count": raw.get("number", len(people)), "people": people, "source": "open-notify"}
            _cache["astronauts"] = {"data": data, "ts": now}
            return data
    except Exception:
        pass

    # Fallback
    data = {"count": len(_FALLBACK_CREW), "people": _FALLBACK_CREW, "source": "fallback"}
    _cache["astronauts"] = {"data": data, "ts": now}
    return data
