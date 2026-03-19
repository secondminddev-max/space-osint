"""
CelesTrak satellite catalog + SGP4 propagation
Fetches GP (General Perturbations) element sets and computes real-time positions.
"""
import time
import math
from datetime import datetime, timezone
import httpx
from sgp4.api import Satrec, WGS72
from sgp4 import exporter
from config import CACHE_TTL_TLE_CATALOG, CACHE_TTL_SATELLITES

_cache = {}
_BASE = "https://celestrak.org/NORAD/elements/gp.php"


def _jday(dt: datetime):
    """Julian date from datetime."""
    y, m, d = dt.year, dt.month, dt.day
    h = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    jd = (367 * y
           - int(7 * (y + int((m + 9) / 12)) / 4)
           + int(275 * m / 9)
           + d + 1721013.5
           + h / 24.0)
    return jd, 0.0


def _teme_to_geodetic(x, y, z, gmst):
    """Convert TEME (km) to geodetic lat/lng/alt."""
    # Rotate TEME -> ECEF
    cos_g = math.cos(gmst)
    sin_g = math.sin(gmst)
    xe = x * cos_g + y * sin_g
    ye = -x * sin_g + y * cos_g
    ze = z

    # ECEF to geodetic (WGS84)
    a = 6378.137  # Earth equatorial radius km
    f = 1 / 298.257223563
    e2 = 2 * f - f * f

    lng = math.degrees(math.atan2(ye, xe))
    p = math.sqrt(xe ** 2 + ye ** 2)
    lat = math.degrees(math.atan2(ze, p * (1 - e2)))

    # Iterative
    for _ in range(5):
        lat_rad = math.radians(lat)
        sin_lat = math.sin(lat_rad)
        N = a / math.sqrt(1 - e2 * sin_lat ** 2)
        lat = math.degrees(math.atan2(ze + e2 * N * sin_lat, p))

    lat_rad = math.radians(lat)
    sin_lat = math.sin(lat_rad)
    N = a / math.sqrt(1 - e2 * sin_lat ** 2)
    alt = p / math.cos(lat_rad) - N

    return lat, lng, alt


def _gmst(jd, jd_frac):
    """Greenwich Mean Sidereal Time in radians."""
    T = ((jd - 2451545.0) + jd_frac) / 36525.0
    gmst_sec = (67310.54841
                + (876600 * 3600 + 8640184.812866) * T
                + 0.093104 * T ** 2
                - 6.2e-6 * T ** 3)
    gmst_rad = (gmst_sec % 86400) / 86400.0 * 2 * math.pi
    if gmst_rad < 0:
        gmst_rad += 2 * math.pi
    return gmst_rad


async def fetch_catalog(client: httpx.AsyncClient, group: str = "active") -> list:
    """Fetch GP elements from CelesTrak for a satellite group."""
    cache_key = f"catalog_{group}"
    now = time.time()
    cached = _cache.get(cache_key)
    if cached and (now - cached["ts"]) < CACHE_TTL_TLE_CATALOG:
        return cached["data"]

    url = f"{_BASE}?GROUP={group}&FORMAT=json"
    try:
        r = await client.get(url, timeout=60)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return _cache.get(cache_key, {}).get("data", [])

    _cache[cache_key] = {"data": data, "ts": now}
    return data


def _build_satrec(gp: dict) -> Satrec | None:
    """Build SGP4 Satrec from CelesTrak GP JSON element."""
    try:
        sat = Satrec()
        sat.sgp4init(
            WGS72,
            'i',  # improved mode
            int(gp.get("NORAD_CAT_ID", 0)),
            _epoch_to_jdsatepoch(gp.get("EPOCH", "")),
            float(gp.get("BSTAR", 0)),
            0.0,  # ndot (not used in sgp4init)
            0.0,  # nddot (not used)
            float(gp.get("ECCENTRICITY", 0)),
            math.radians(float(gp.get("ARG_OF_PERICENTER", 0))),
            math.radians(float(gp.get("INCLINATION", 0))),
            math.radians(float(gp.get("MEAN_ANOMALY", 0))),
            float(gp.get("MEAN_MOTION", 0)) * (2 * math.pi / 1440.0),  # rev/day -> rad/min
            math.radians(float(gp.get("RA_OF_ASC_NODE", 0))),
        )
        return sat
    except Exception:
        return None


def _epoch_to_jdsatepoch(epoch_str: str) -> float:
    """Convert ISO epoch string to days since 1949-12-31 (sgp4 epoch)."""
    try:
        dt = datetime.fromisoformat(epoch_str.replace("Z", "+00:00"))
        # SGP4 epoch is in days since 1949 Dec 31 00:00 UT
        ref = datetime(1949, 12, 31, 0, 0, 0, tzinfo=timezone.utc)
        return (dt - ref).total_seconds() / 86400.0
    except Exception:
        return 0.0


def propagate_satellite(gp: dict, dt: datetime = None) -> dict | None:
    """Propagate a single satellite to given time, return position."""
    if dt is None:
        dt = datetime.now(timezone.utc)

    sat = _build_satrec(gp)
    if sat is None:
        return None

    jd, jd_frac = _jday(dt)
    e, r, v = sat.sgp4(jd, jd_frac)
    if e != 0 or r is None:
        return None

    g = _gmst(jd, jd_frac)
    lat, lng, alt = _teme_to_geodetic(r[0], r[1], r[2], g)

    return {
        "norad_id": int(gp.get("NORAD_CAT_ID", 0)),
        "name": gp.get("OBJECT_NAME", "UNKNOWN"),
        "lat": round(lat, 4),
        "lng": round(lng, 4),
        "alt_km": round(alt, 1),
        "inclination": float(gp.get("INCLINATION", 0)),
        "period_min": round(1440.0 / float(gp.get("MEAN_MOTION", 1)), 1),
        "object_type": gp.get("OBJECT_TYPE", ""),
    }


async def get_satellite_positions(client: httpx.AsyncClient, group: str = "stations") -> list:
    """Get current positions of all satellites in a group."""
    now = time.time()
    cache_key = f"positions_{group}"
    cached = _cache.get(cache_key)
    if cached and (now - cached["ts"]) < CACHE_TTL_SATELLITES:
        return cached["data"]

    catalog = await fetch_catalog(client, group)
    dt = datetime.now(timezone.utc)
    positions = []

    for gp in catalog:
        pos = propagate_satellite(gp, dt)
        if pos:
            positions.append(pos)

    _cache[cache_key] = {"data": positions, "ts": now}
    return positions


async def get_satellite_stats(client: httpx.AsyncClient) -> dict:
    """Get satellite catalog statistics."""
    now = time.time()
    cached = _cache.get("stats")
    if cached and (now - cached["ts"]) < CACHE_TTL_SATELLITES:
        return cached["data"]

    catalog = await fetch_catalog(client, "active")
    total = len(catalog)
    payloads = sum(1 for s in catalog if s.get("OBJECT_TYPE") == "PAYLOAD")
    debris = sum(1 for s in catalog if s.get("OBJECT_TYPE") == "DEBRIS")
    rocket_bodies = sum(1 for s in catalog if s.get("OBJECT_TYPE") == "ROCKET BODY")

    data = {
        "total_tracked": total,
        "active_payloads": payloads,
        "debris": debris,
        "rocket_bodies": rocket_bodies,
        "fetched_at": now,
    }
    _cache["stats"] = {"data": data, "ts": now}
    return data


def compute_ground_track(gp: dict, minutes: int = 90, step_sec: int = 30) -> list:
    """Compute future ground track for a satellite."""
    sat = _build_satrec(gp)
    if sat is None:
        return []

    now = datetime.now(timezone.utc)
    track = []

    for s in range(0, minutes * 60, step_sec):
        dt = datetime(
            now.year, now.month, now.day, now.hour, now.minute, now.second,
            tzinfo=timezone.utc
        )
        from datetime import timedelta
        dt = dt + timedelta(seconds=s)
        jd, jd_frac = _jday(dt)
        e, r, v = sat.sgp4(jd, jd_frac)
        if e != 0 or r is None:
            continue
        g = _gmst(jd, jd_frac)
        lat, lng, alt = _teme_to_geodetic(r[0], r[1], r[2], g)
        track.append({"lat": round(lat, 3), "lng": round(lng, 3)})

    return track
