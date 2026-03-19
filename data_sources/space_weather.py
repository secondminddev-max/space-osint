"""
Space Weather data from NOAA SWPC
- Kp Index (planetary geomagnetic)
- Solar wind plasma (speed, density, temp)
- Solar wind magnetic field (Bt, Bz)
- NOAA R/S/G scales
- Active alerts
- 10.7cm solar flux
"""
from __future__ import annotations
import time
from typing import Optional, Union, List, Dict
import httpx
from config import CACHE_TTL_WEATHER, CACHE_TTL_KP

_cache = {}
_BASE = "https://services.swpc.noaa.gov"


async def _fetch_json(client: httpx.AsyncClient, url: str) -> dict | list | None:
    try:
        r = await client.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


async def fetch_weather_composite(client: httpx.AsyncClient) -> dict:
    """Fetch all space weather data into a single composite."""
    now = time.time()
    cached = _cache.get("weather")
    if cached and (now - cached["ts"]) < CACHE_TTL_WEATHER:
        return cached["data"]

    # Fetch all endpoints concurrently via httpx
    import asyncio
    kp_raw, wind_speed, wind_mag, flux, scales, alerts_raw = await asyncio.gather(
        _fetch_json(client, f"{_BASE}/products/noaa-planetary-k-index.json"),
        _fetch_json(client, f"{_BASE}/products/summary/solar-wind-speed.json"),
        _fetch_json(client, f"{_BASE}/products/summary/solar-wind-mag-field.json"),
        _fetch_json(client, f"{_BASE}/products/summary/10cm-flux.json"),
        _fetch_json(client, f"{_BASE}/products/noaa-scales.json"),
        _fetch_json(client, f"{_BASE}/products/alerts.json"),
    )

    # Parse Kp index — last entry is most recent
    kp_current = None
    kp_history = []
    if kp_raw and len(kp_raw) > 1:
        for row in kp_raw[1:]:  # skip header
            try:
                kp_history.append({
                    "time": row[0],
                    "kp": float(row[1]),
                    "a_running": row[2],
                    "station_count": row[3],
                })
            except (ValueError, IndexError):
                continue
        if kp_history:
            kp_current = kp_history[-1]["kp"]

    # Parse solar wind speed
    solar_wind_speed = None
    if wind_speed and "WindSpeed" in wind_speed:
        try:
            solar_wind_speed = float(wind_speed["WindSpeed"])
        except (ValueError, TypeError):
            pass

    # Parse magnetic field
    bt = None
    bz = None
    if wind_mag:
        try:
            bt = float(wind_mag.get("Bt", 0))
            bz = float(wind_mag.get("Bz", 0))
        except (ValueError, TypeError):
            pass

    # Parse solar flux
    sfi = None
    if flux and "Flux" in flux:
        try:
            sfi = float(flux["Flux"])
        except (ValueError, TypeError):
            pass

    # Parse NOAA scales (R/S/G)
    scale_data = {"R": {"Scale": 0}, "S": {"Scale": 0}, "G": {"Scale": 0}}
    if scales and "0" in scales:
        current = scales["0"]
        for key in ["R", "S", "G"]:
            if key in current:
                scale_data[key] = current[key]

    # Parse alerts
    alerts = []
    if alerts_raw and isinstance(alerts_raw, list):
        for alert in alerts_raw[-20:]:  # last 20
            if isinstance(alert, dict):
                alerts.append({
                    "product_id": alert.get("product_id", ""),
                    "issue_datetime": alert.get("issue_datetime", ""),
                    "message": alert.get("message", "")[:500],
                })

    data = {
        "kp_current": kp_current,
        "kp_history": kp_history[-24:],  # last 24 entries (72h)
        "solar_wind_speed": solar_wind_speed,
        "bt": bt,
        "bz": bz,
        "sfi": sfi,
        "scales": scale_data,
        "alerts": alerts,
        "fetched_at": now,
    }

    _cache["weather"] = {"data": data, "ts": now}
    return data


async def fetch_kp_history(client: httpx.AsyncClient) -> list:
    """Full Kp history for charting."""
    now = time.time()
    cached = _cache.get("kp_history")
    if cached and (now - cached["ts"]) < CACHE_TTL_KP:
        return cached["data"]

    raw = await _fetch_json(client, f"{_BASE}/products/noaa-planetary-k-index.json")
    history = []
    if raw and len(raw) > 1:
        for row in raw[1:]:
            try:
                history.append({"time": row[0], "kp": float(row[1])})
            except (ValueError, IndexError):
                continue

    _cache["kp_history"] = {"data": history, "ts": now}
    return history
