"""
Enhanced Space Environment Feeds — NOAA SWPC + GOES + SUVI/SDO/LASCO Imagery
================================================================================
New data sources for Echelon Vantage that extend beyond the base space_weather
module.  All endpoints are free, public, and require NO API keys.

Data feeds integrated:
  - NOAA SWPC Aurora Ovation (probability grid + imagery)
  - NOAA SWPC Solar Wind Plasma 7-day history
  - NOAA SWPC Solar Wind Mag-field 7-day history
  - NOAA SWPC Geospace Propagated Solar Wind (1-hour)
  - NOAA SWPC ENLIL solar-wind model (time-series + animation frames)
  - NOAA SWPC Solar Flare Probabilities (C/M/X class)
  - NOAA SWPC Active Solar Regions (sunspots)
  - NOAA SWPC Kp Index Forecast (predicted Kp)
  - NOAA SWPC 45-day Forecast (Ap + F10.7)
  - NOAA SWPC ICAO Space Weather Advisories (aviation impact)
  - NOAA SWPC Electron Fluence Forecast (radiation belt)
  - NOAA SWPC GOES X-ray Flux (1-day, primary satellite)
  - NOAA SWPC GOES Proton Flux (1-day, primary satellite)
  - NOAA SWPC GOES Magnetometer (1-day, primary satellite)
  - NOAA SWPC SUVI Solar Imagery (6 EUV wavelengths, latest)
  - NOAA SWPC SDO/HMI Magnetogram (latest image)
  - NOAA SWPC LASCO C2/C3 Coronagraph (latest images)
  - NOAA SWPC D-RAP (HF radio absorption imagery)
  - CelesTrak SOCRATES conjunction data (satellite close approaches)

Intelligence value for FVEY space domain awareness:
  - Aurora probability affects HF comms and radar at high latitudes
  - Solar wind history enables trend analysis for geomagnetic storm prediction
  - Geospace propagated data shows real-time magnetosphere driving conditions
  - ENLIL model predicts CME arrival and solar-wind structure
  - Solar flare probabilities inform comms/GPS degradation risk assessment
  - Active regions identify sources of future flare/CME threats
  - GOES particle data detects radiation hazards for crewed missions & satellites
  - GOES X-ray flux indicates current solar flare intensity
  - ICAO advisories flag GPS/HF impact to military aviation
  - Electron fluence forecasts assess internal charging risk to satellites
  - Solar imagery enables visual confirmation of CME launches & coronal holes
  - LASCO coronagraphs detect Earth-directed CMEs before arrival
  - Conjunction data supports space debris threat tracking
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

import httpx

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache: Dict[str, Dict[str, Any]] = {}

_SWPC_BASE = "https://services.swpc.noaa.gov"

# Cache TTLs (seconds)
_TTL_AURORA       = 300      # 5 min  — aurora updates every ~5 min
_TTL_PLASMA_7D    = 600      # 10 min — 7-day bulk data
_TTL_MAG_7D       = 600      # 10 min
_TTL_GEOSPACE     = 120      # 2 min  — near real-time
_TTL_IMAGERY      = 300      # 5 min  — image URLs don't change that fast
_TTL_ENLIL        = 3600     # 1 hr   — model runs infrequently
_TTL_FLARE_PROB   = 900      # 15 min
_TTL_SOLAR_REGION = 900      # 15 min
_TTL_KP_FORECAST  = 900      # 15 min
_TTL_FORECAST_45D = 3600     # 1 hr
_TTL_ICAO         = 600      # 10 min
_TTL_ELECTRON     = 3600     # 1 hr
_TTL_GOES         = 300      # 5 min
_TTL_DEBRIS       = 900      # 15 min
_TTL_ENHANCED     = 300      # 5 min


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _fetch_json(
    client: httpx.AsyncClient,
    url: str,
    timeout: int = 20,
) -> Optional[Any]:
    """Fetch JSON from *url*, returning None on any error."""
    try:
        r = await client.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except (httpx.HTTPError, ValueError, TypeError):
        return None


def _cached(key: str, ttl: int) -> Optional[Any]:
    """Return cached data if still fresh, else None."""
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < ttl:
        return entry["data"]
    return None


def _store(key: str, data: Any) -> Any:
    """Store *data* in cache under *key* and return it."""
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# ---------------------------------------------------------------------------
# 1. Solar Imagery — SUVI, SDO/HMI, LASCO, D-RAP, ENLIL
# ---------------------------------------------------------------------------

async def fetch_solar_imagery(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Return URLs to the latest solar images from multiple instruments.

    Sources:
      - SUVI (Solar Ultraviolet Imager) on GOES-19: 6 EUV wavelengths
        094 A — Fe XVIII  (flaring regions, ~6.3 MK)
        131 A — Fe VIII / XXI  (flare plasma, ~10 MK & 0.4 MK)
        171 A — Fe IX  (quiet corona, ~0.6 MK)
        195 A — Fe XII  (corona, ~1.6 MK)
        284 A — Fe XV  (active regions, ~2.0 MK)
        304 A — He II  (chromosphere/transition region, ~0.05 MK)
      - SDO/HMI magnetogram (photospheric magnetic field)
      - LASCO C2/C3 coronagraphs (inner / outer corona — CME detection)
      - D-RAP HF absorption map
      - ENLIL solar-wind model animation frames (latest URL list)
    """
    cached = _cached("solar_imagery", _TTL_IMAGERY)
    if cached is not None:
        return cached

    suvi_base = f"{_SWPC_BASE}/images/animations/suvi/primary"
    wavelengths = ["094", "131", "171", "195", "284", "304"]

    suvi_images = {
        wl: f"{suvi_base}/{wl}/latest.png"
        for wl in wavelengths
    }

    # Also fetch the ENLIL animation frame list (so the front-end can animate)
    enlil_frames = await _fetch_json(
        client,
        f"{_SWPC_BASE}/products/animations/enlil.json",
        timeout=15,
    )
    enlil_urls: List[str] = []
    if isinstance(enlil_frames, list):
        for frame in enlil_frames[-48:]:  # last 48 frames (~2 days)
            url = frame.get("url", "")
            if url:
                enlil_urls.append(f"{_SWPC_BASE}{url}")

    # Fetch LASCO C2/C3 animation lists for latest frame URLs
    lasco_c2_frames = await _fetch_json(
        client,
        f"{_SWPC_BASE}/products/animations/lasco-c2.json",
        timeout=15,
    )
    lasco_c3_frames = await _fetch_json(
        client,
        f"{_SWPC_BASE}/products/animations/lasco-c3.json",
        timeout=15,
    )

    lasco_c2_latest = ""
    lasco_c3_latest = ""
    if isinstance(lasco_c2_frames, list) and lasco_c2_frames:
        last = lasco_c2_frames[-1].get("url", "")
        if last:
            lasco_c2_latest = f"{_SWPC_BASE}{last}"
    if isinstance(lasco_c3_frames, list) and lasco_c3_frames:
        last = lasco_c3_frames[-1].get("url", "")
        if last:
            lasco_c3_latest = f"{_SWPC_BASE}{last}"

    data: Dict[str, Any] = {
        "suvi": {
            "description": "GOES-19 SUVI EUV solar images (latest per wavelength)",
            "wavelengths": suvi_images,
        },
        "sdo_hmi": {
            "description": "SDO/HMI photospheric magnetogram",
            "url": f"{_SWPC_BASE}/images/animations/sdo-hmii/latest.jpg",
        },
        "lasco_c2": {
            "description": "SOHO LASCO C2 coronagraph — inner corona (2-6 Rs)",
            "url": lasco_c2_latest or f"{_SWPC_BASE}/images/animations/lasco-c2/latest.jpg",
        },
        "lasco_c3": {
            "description": "SOHO LASCO C3 coronagraph — outer corona (3.7-30 Rs)",
            "url": lasco_c3_latest or f"{_SWPC_BASE}/images/animations/lasco-c3/latest.jpg",
        },
        "drap": {
            "description": "D-Region Absorption Prediction — HF radio blackout map",
            "url": f"{_SWPC_BASE}/images/animations/d-rap/global/d-rap/latest.png",
        },
        "enlil": {
            "description": "WSA-ENLIL solar wind model animation (latest 48 frames)",
            "frame_count": len(enlil_urls),
            "frames": enlil_urls[-6:],  # last 6 for preview
            "all_frames_endpoint": f"{_SWPC_BASE}/products/animations/enlil.json",
        },
        "aurora_north": {
            "description": "Aurora forecast — Northern hemisphere",
            "url": f"{_SWPC_BASE}/images/animations/ovation/north/latest.jpg",
        },
        "aurora_south": {
            "description": "Aurora forecast — Southern hemisphere",
            "url": f"{_SWPC_BASE}/images/animations/ovation/south/latest.jpg",
        },
        "synoptic_map": {
            "description": "Full-disk synoptic map of solar activity",
            "url": f"{_SWPC_BASE}/images/synoptic-map.jpg",
        },
        "fetched_at": time.time(),
    }

    return _store("solar_imagery", data)


# ---------------------------------------------------------------------------
# 2. Aurora Data — probability grid + forecast imagery
# ---------------------------------------------------------------------------

async def fetch_aurora_data(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    NOAA OVATION Aurora Model — probability grid + hemisphere images.

    The grid gives aurora probability at each (lon, lat) cell.
    Values 0-100 indicate estimated probability of visible aurora.
    Intel use: high-latitude HF comms disruption, radar interference
    assessment, GPS scintillation risk at polar routes.
    """
    cached = _cached("aurora", _TTL_AURORA)
    if cached is not None:
        return cached

    raw = await _fetch_json(
        client,
        f"{_SWPC_BASE}/json/ovation_aurora_latest.json",
    )

    if not raw or not isinstance(raw, dict):
        prev = _cache.get("aurora", {}).get("data")
        return prev if prev else {"error": "Aurora data unavailable"}

    coordinates = raw.get("coordinates", [])

    # Build summary — max probability, high-activity zones
    max_prob = 0
    high_zones: List[Dict[str, Any]] = []
    for coord in coordinates:
        if not isinstance(coord, (list, tuple)) or len(coord) < 3:
            continue
        try:
            lon, lat, prob = float(coord[0]), float(coord[1]), int(coord[2])
        except (ValueError, TypeError):
            continue
        if prob > max_prob:
            max_prob = prob
        if prob >= 50:
            high_zones.append({"lon": lon, "lat": lat, "probability": prob})

    # Sort high zones by probability descending, keep top 50
    high_zones.sort(key=lambda z: z["probability"], reverse=True)
    high_zones = high_zones[:50]

    data: Dict[str, Any] = {
        "observation_time": raw.get("Observation Time", ""),
        "forecast_time": raw.get("Forecast Time", ""),
        "max_probability": max_prob,
        "high_activity_zones": high_zones,
        "grid_points_total": len(coordinates),
        "imagery": {
            "north": f"{_SWPC_BASE}/images/animations/ovation/north/latest.jpg",
            "south": f"{_SWPC_BASE}/images/animations/ovation/south/latest.jpg",
            "north_static": f"{_SWPC_BASE}/images/aurora-forecast-northern-hemisphere.jpg",
            "south_static": f"{_SWPC_BASE}/images/aurora-forecast-southern-hemisphere.jpg",
        },
        "intel_note": (
            "Aurora probability above 50% indicates significant geomagnetic "
            "activity.  Expect HF comms degradation at high latitudes, increased "
            "GPS scintillation on polar routes, and potential GIC impact to "
            "ground infrastructure."
        ),
        "fetched_at": time.time(),
    }

    return _store("aurora", data)


# ---------------------------------------------------------------------------
# 3. Solar Wind 7-day History — plasma + magnetic field
# ---------------------------------------------------------------------------

async def fetch_solar_wind_history(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    7-day solar wind plasma (density, speed, temperature) and magnetic field
    (Bt, Bz, Bx, By) history from NOAA SWPC DSCOVR/ACE measurements.

    Intel use: trend analysis for predicting geomagnetic storms;
    Bz persistently southward + elevated speed = storm driver.
    """
    cached = _cached("solar_wind_7d", _TTL_PLASMA_7D)
    if cached is not None:
        return cached

    plasma_raw, mag_raw = await asyncio.gather(
        _fetch_json(client, f"{_SWPC_BASE}/products/solar-wind/plasma-7-day.json"),
        _fetch_json(client, f"{_SWPC_BASE}/products/solar-wind/mag-7-day.json"),
    )

    # --- Parse plasma ---
    plasma: List[Dict[str, Any]] = []
    if isinstance(plasma_raw, list) and len(plasma_raw) > 1:
        # Header: ["time_tag", "density", "speed", "temperature"]
        for row in plasma_raw[1:]:
            if not isinstance(row, (list, tuple)) or len(row) < 4:
                continue
            try:
                entry: Dict[str, Any] = {"time": row[0]}
                entry["density"] = float(row[1]) if row[1] is not None else None
                entry["speed"] = float(row[2]) if row[2] is not None else None
                entry["temperature"] = float(row[3]) if row[3] is not None else None
                plasma.append(entry)
            except (ValueError, TypeError):
                continue

    # Downsample plasma to ~hourly for manageable payload
    # raw is ~1-min cadence = ~10080 rows; take every 60th
    if len(plasma) > 300:
        plasma = plasma[::60]

    # --- Parse mag ---
    mag: List[Dict[str, Any]] = []
    if isinstance(mag_raw, list) and len(mag_raw) > 1:
        # Header: ["time_tag","bx_gsm","by_gsm","bz_gsm","lon_gsm","lat_gsm","bt"]
        for row in mag_raw[1:]:
            if not isinstance(row, (list, tuple)) or len(row) < 7:
                continue
            try:
                mentry: Dict[str, Any] = {"time": row[0]}
                mentry["bx"] = float(row[1]) if row[1] is not None else None
                mentry["by"] = float(row[2]) if row[2] is not None else None
                mentry["bz"] = float(row[3]) if row[3] is not None else None
                mentry["bt"] = float(row[6]) if row[6] is not None else None
                mag.append(mentry)
            except (ValueError, TypeError, IndexError):
                continue

    if len(mag) > 300:
        mag = mag[::60]

    # Latest values
    latest_plasma = plasma[-1] if plasma else {}
    latest_mag = mag[-1] if mag else {}

    data: Dict[str, Any] = {
        "plasma": {
            "count": len(plasma),
            "latest": latest_plasma,
            "history": plasma,
        },
        "magnetic_field": {
            "count": len(mag),
            "latest": latest_mag,
            "history": mag,
        },
        "intel_note": (
            "Sustained Bz < -10 nT with speed > 500 km/s drives G2+ geomagnetic "
            "storms.  Monitor density spikes for CME shock arrivals."
        ),
        "fetched_at": time.time(),
    }

    return _store("solar_wind_7d", data)


# ---------------------------------------------------------------------------
# 4. Geospace Propagated Solar Wind
# ---------------------------------------------------------------------------

async def fetch_geospace_data(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    NOAA SWPC geospace propagated solar-wind — real-time conditions at the
    magnetopause, propagated from L1 monitoring spacecraft.

    Fields: speed, density, temperature, bx/by/bz/bt, vx/vy/vz,
    propagated_time_tag (when the parcel hits the magnetosphere).

    Intel use: indicates actual driving conditions of the magnetosphere
    RIGHT NOW.  Critical for real-time assessment of GPS/comms disruption.
    """
    cached = _cached("geospace", _TTL_GEOSPACE)
    if cached is not None:
        return cached

    raw = await _fetch_json(
        client,
        f"{_SWPC_BASE}/products/geospace/propagated-solar-wind-1-hour.json",
    )

    entries: List[Dict[str, Any]] = []
    if isinstance(raw, list) and len(raw) > 1:
        # Header row then data rows
        for row in raw[1:]:
            if not isinstance(row, (list, tuple)) or len(row) < 12:
                continue
            try:
                entries.append({
                    "time": row[0],
                    "speed": _safe_float(row[1]),
                    "density": _safe_float(row[2]),
                    "temperature": _safe_float(row[3]),
                    "bx": _safe_float(row[4]),
                    "by": _safe_float(row[5]),
                    "bz": _safe_float(row[6]),
                    "bt": _safe_float(row[7]),
                    "vx": _safe_float(row[8]),
                    "vy": _safe_float(row[9]),
                    "vz": _safe_float(row[10]),
                    "propagated_time": row[11],
                })
            except (IndexError, TypeError):
                continue

    latest = entries[-1] if entries else {}

    data: Dict[str, Any] = {
        "description": "Propagated solar wind at Earth's magnetopause (1-hour window)",
        "entries": entries,
        "latest": latest,
        "intel_note": (
            "Propagated solar wind shows actual driving of the magnetosphere.  "
            "Bz strongly southward (< -10 nT) = active reconnection = storm.  "
            "Speed > 700 km/s with density > 10/cm3 = CME shock front arrival."
        ),
        "fetched_at": time.time(),
    }

    return _store("geospace", data)


# ---------------------------------------------------------------------------
# 5. Debris / Conjunction Alerts — multi-source
# ---------------------------------------------------------------------------

async def fetch_debris_alerts(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Space debris and conjunction awareness from multiple free sources.

    Sources:
      1. CelesTrak SOCRATES (Satellite Orbital Conjunction Reports Assessing
         Threatening Encounters in Space) — CSV of close approaches.
         NOTE: This is a best-effort scrape; CelesTrak may rate-limit.
      2. NOAA SWPC alerts filtered for radiation-belt / particle events
         (indirect debris risk indicator — high-energy particle environment
         causes anomalies in LEO satellites that can generate debris).
      3. Recently-launched objects from CelesTrak (new objects = potential
         debris source or adversary deployment).

    For full conjunction data, Space-Track.org (requires free account) provides
    CDM (Conjunction Data Messages).  That integration is noted here for
    future implementation.
    """
    cached = _cached("debris_alerts", _TTL_DEBRIS)
    if cached is not None:
        return cached

    # 1) CelesTrak last-30-days catalog — newly catalogued objects
    new_objects_raw = await _fetch_json(
        client,
        "https://celestrak.org/NORAD/elements/gp.php?GROUP=last-30-days&FORMAT=json",
        timeout=30,
    )
    new_objects: List[Dict[str, Any]] = []
    if isinstance(new_objects_raw, list):
        for obj in new_objects_raw[:100]:  # limit to 100
            new_objects.append({
                "norad_id": obj.get("NORAD_CAT_ID"),
                "name": obj.get("OBJECT_NAME", ""),
                "intl_designator": obj.get("OBJECT_ID", ""),
                "epoch": obj.get("EPOCH", ""),
                "mean_motion": obj.get("MEAN_MOTION"),
                "eccentricity": obj.get("ECCENTRICITY"),
                "inclination": obj.get("INCLINATION"),
                "period_min": obj.get("PERIOD"),
                "object_type": obj.get("OBJECT_TYPE", ""),
                "rcs_size": obj.get("RCS_SIZE", ""),
                "country": obj.get("COUNTRY_CODE", ""),
                "launch_date": obj.get("LAUNCH_DATE", ""),
            })

    # 2) SWPC alerts — filter for particle/radiation events that affect LEO
    alerts_raw = await _fetch_json(
        client,
        f"{_SWPC_BASE}/products/alerts.json",
    )
    particle_alerts: List[Dict[str, str]] = []
    if isinstance(alerts_raw, list):
        keywords = ["proton", "electron", "radiation", "particle", "SEP", "S1", "S2", "S3", "S4", "S5"]
        for alert in alerts_raw[-50:]:
            if not isinstance(alert, dict):
                continue
            msg = alert.get("message", "")
            if any(kw.lower() in msg.lower() for kw in keywords):
                particle_alerts.append({
                    "product_id": alert.get("product_id", ""),
                    "issue_datetime": alert.get("issue_datetime", ""),
                    "message": msg[:500],
                })

    # 3) ICAO advisories — GNSS degradation can indicate debris-related anomalies
    icao_raw = await _fetch_json(
        client,
        f"{_SWPC_BASE}/json/icao-space-weather-advisories.json",
    )
    icao_advisories: List[Dict[str, str]] = []
    if isinstance(icao_raw, list):
        for adv in icao_raw[-10:]:
            if not isinstance(adv, dict):
                continue
            icao_advisories.append({
                "dtg": adv.get("DTG", ""),
                "advisory_number": adv.get("Advisory Number", ""),
                "effect": adv.get("SWX Effect", ""),
                "severity": adv.get("Severity", ""),
                "status": adv.get("Status", ""),
            })

    data: Dict[str, Any] = {
        "new_catalog_objects": {
            "description": "Newly catalogued space objects (last 30 days) — CelesTrak",
            "count": len(new_objects),
            "objects": new_objects,
        },
        "particle_environment_alerts": {
            "description": "SWPC particle/radiation alerts — LEO satellite anomaly risk",
            "count": len(particle_alerts),
            "alerts": particle_alerts,
        },
        "icao_space_weather": {
            "description": "ICAO aviation space weather advisories — GNSS/HF impact",
            "count": len(icao_advisories),
            "advisories": icao_advisories,
        },
        "conjunction_sources": {
            "note": (
                "Full conjunction data (CDM) requires a free Space-Track.org "
                "account.  CelesTrak SOCRATES provides close-approach reports "
                "but may be rate-limited.  These sources are flagged for future "
                "integration with API key support."
            ),
            "space_track_url": "https://www.space-track.org/basicspacedata/query/class/cdm_public/",
            "socrates_url": "https://celestrak.org/SOCRATES/",
        },
        "intel_note": (
            "New catalog objects in the last 30 days may include adversary "
            "deployments, breakup debris, or covert payloads.  Cross-reference "
            "country codes (PRC, CIS) with launch dates for attribution.  "
            "Particle alerts indicate elevated single-event upset (SEU) risk "
            "that can cause satellite malfunctions and potential debris generation."
        ),
        "fetched_at": time.time(),
    }

    return _store("debris_alerts", data)


# ---------------------------------------------------------------------------
# 6. GOES Satellite Instrument Data
# ---------------------------------------------------------------------------

async def fetch_goes_data(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    GOES primary satellite instrument data:
      - X-ray flux (solar flare detection)
      - Proton flux (radiation storm detection)
      - Magnetometer (geomagnetic field at GEO)

    Intel use: X-ray flux spikes = solar flare in progress (comms blackout).
    Proton flux elevation = radiation storm (S-scale event, satellite damage
    risk).  Magnetometer disturbance at GEO = geomagnetic storm compressing
    the magnetosphere.
    """
    cached = _cached("goes", _TTL_GOES)
    if cached is not None:
        return cached

    goes_base = f"{_SWPC_BASE}/json/goes/primary"

    xray_raw, proton_raw, mag_raw = await asyncio.gather(
        _fetch_json(client, f"{goes_base}/xrays-1-day.json"),
        _fetch_json(client, f"{goes_base}/integral-protons-1-day.json"),
        _fetch_json(client, f"{goes_base}/magnetometers-1-day.json"),
    )

    # --- X-ray: latest reading per energy band ---
    xray_latest: Dict[str, Any] = {}
    if isinstance(xray_raw, list):
        for entry in reversed(xray_raw):
            if not isinstance(entry, dict):
                continue
            energy = entry.get("energy", "")
            if energy and energy not in xray_latest:
                xray_latest[energy] = {
                    "time": entry.get("time_tag", ""),
                    "flux": entry.get("flux"),
                    "satellite": entry.get("satellite"),
                }
            if len(xray_latest) >= 2:
                break

    # --- Proton: latest >10 MeV reading ---
    proton_latest: Dict[str, Any] = {}
    if isinstance(proton_raw, list):
        for entry in reversed(proton_raw):
            if not isinstance(entry, dict):
                continue
            energy = entry.get("energy", "")
            if energy and energy not in proton_latest:
                proton_latest[energy] = {
                    "time": entry.get("time_tag", ""),
                    "flux": entry.get("flux"),
                    "satellite": entry.get("satellite"),
                }
            if len(proton_latest) >= 6:
                break

    # --- Magnetometer: latest He reading ---
    mag_latest: Dict[str, Any] = {}
    if isinstance(mag_raw, list) and mag_raw:
        last_mag = mag_raw[-1]
        if isinstance(last_mag, dict):
            mag_latest = {
                "time": last_mag.get("time_tag", ""),
                "he": last_mag.get("He"),
                "hp": last_mag.get("Hp"),
                "hn": last_mag.get("Hn"),
                "total": last_mag.get("total"),
                "satellite": last_mag.get("satellite"),
            }

    data: Dict[str, Any] = {
        "xray": {
            "description": "GOES X-ray flux — solar flare indicator",
            "latest": xray_latest,
        },
        "protons": {
            "description": "GOES integral proton flux — radiation storm indicator",
            "latest": proton_latest,
        },
        "magnetometer": {
            "description": "GOES magnetometer — geomagnetic field at GEO orbit",
            "latest": mag_latest,
        },
        "intel_note": (
            "X-ray flux > 1e-4 W/m2 = X-class flare (R3+ radio blackout).  "
            "Proton flux > 10 pfu at >10 MeV = S1 radiation storm.  "
            "Magnetometer He perturbation > 50 nT = geomagnetic storm "
            "compressing magnetosphere toward GEO assets."
        ),
        "fetched_at": time.time(),
    }

    return _store("goes", data)


# ---------------------------------------------------------------------------
# 7. Solar Flare Probabilities & Active Regions
# ---------------------------------------------------------------------------

async def fetch_solar_activity(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Solar flare probabilities (C/M/X class) and active sunspot regions.
    """
    cached = _cached("solar_activity", _TTL_FLARE_PROB)
    if cached is not None:
        return cached

    probs_raw, regions_raw = await asyncio.gather(
        _fetch_json(client, f"{_SWPC_BASE}/json/solar_probabilities.json"),
        _fetch_json(client, f"{_SWPC_BASE}/json/solar_regions.json"),
    )

    # Latest probability entry
    latest_prob: Dict[str, Any] = {}
    if isinstance(probs_raw, list) and probs_raw:
        lp = probs_raw[-1]
        if isinstance(lp, dict):
            latest_prob = {
                "date": lp.get("date", ""),
                "c_class_1d": lp.get("c_class_1_day"),
                "m_class_1d": lp.get("m_class_1_day"),
                "x_class_1d": lp.get("x_class_1_day"),
                "proton_1d": lp.get("10mev_protons_1_day"),
                "polar_cap": lp.get("polar_cap_absorption", ""),
            }

    # Active regions
    regions: List[Dict[str, Any]] = []
    if isinstance(regions_raw, list):
        for reg in regions_raw[-30:]:  # recent entries
            if not isinstance(reg, dict):
                continue
            regions.append({
                "region": reg.get("region"),
                "location": reg.get("location", ""),
                "area": reg.get("area"),
                "num_spots": reg.get("number_spots"),
                "mag_class": reg.get("mag_class", ""),
                "spot_class": reg.get("spot_class", ""),
                "c_prob": reg.get("c_flare_probability"),
                "m_prob": reg.get("m_flare_probability"),
                "x_prob": reg.get("x_flare_probability"),
                "proton_prob": reg.get("proton_probability"),
            })

    data: Dict[str, Any] = {
        "flare_probabilities": {
            "description": "SWPC solar flare probability forecast (C/M/X class)",
            "latest": latest_prob,
        },
        "active_regions": {
            "description": "Active sunspot regions with flare potential",
            "count": len(regions),
            "regions": regions,
        },
        "intel_note": (
            "X-class probability > 10% warrants pre-positioning comms fallback.  "
            "M-class > 50% expect degraded HF.  Watch regions with delta-class "
            "magnetic configuration — highest flare potential."
        ),
        "fetched_at": time.time(),
    }

    return _store("solar_activity", data)


# ---------------------------------------------------------------------------
# 8. Kp Forecast & 45-day Outlook
# ---------------------------------------------------------------------------

async def fetch_forecasts(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Kp index forecast (3-hour intervals, ~10 days) and 45-day Ap/F10.7
    outlook.  Also includes electron fluence forecast for radiation belt
    assessment.
    """
    cached = _cached("forecasts", _TTL_KP_FORECAST)
    if cached is not None:
        return cached

    kp_raw, f45_raw, electron_raw = await asyncio.gather(
        _fetch_json(client, f"{_SWPC_BASE}/products/noaa-planetary-k-index-forecast.json"),
        _fetch_json(client, f"{_SWPC_BASE}/json/45-day-forecast.json"),
        _fetch_json(client, f"{_SWPC_BASE}/json/electron_fluence_forecast.json"),
    )

    # Kp forecast
    kp_forecast: List[Dict[str, Any]] = []
    if isinstance(kp_raw, list):
        for entry in kp_raw:
            if not isinstance(entry, dict):
                continue
            kp_forecast.append({
                "time": entry.get("time_tag", ""),
                "kp": entry.get("kp"),
                "observed": entry.get("observed", ""),
                "noaa_scale": entry.get("noaa_scale"),
            })

    # 45-day forecast — split into Ap and F10.7 series
    ap_forecast: List[Dict[str, Any]] = []
    f107_forecast: List[Dict[str, Any]] = []
    if isinstance(f45_raw, list):
        for entry in f45_raw:
            if not isinstance(entry, (list, tuple)) or len(entry) < 3:
                continue
            date_str, metric, value = entry[0], entry[1], entry[2]
            try:
                val = float(value)
            except (ValueError, TypeError):
                continue
            if metric == "ap":
                ap_forecast.append({"date": date_str, "ap": val})
            elif metric == "f107":
                f107_forecast.append({"date": date_str, "f107": val})

    # Electron fluence
    electron_forecast: List[Dict[str, Any]] = []
    if isinstance(electron_raw, list):
        for entry in electron_raw[-14:]:  # last 14 days
            if not isinstance(entry, dict):
                continue
            electron_forecast.append({
                "date": entry.get("date", ""),
                "fluence": entry.get("fluence"),
                "fluence_day2": entry.get("fluence_day_two"),
                "fluence_day3": entry.get("fluence_day_three"),
                "speed": entry.get("speed"),
            })

    data: Dict[str, Any] = {
        "kp_forecast": {
            "description": "Kp index forecast — 3-hour intervals with NOAA G-scale",
            "entries": kp_forecast,
        },
        "ap_45day": {
            "description": "45-day Ap geomagnetic index forecast",
            "entries": ap_forecast,
        },
        "f107_45day": {
            "description": "45-day F10.7 solar radio flux forecast",
            "entries": f107_forecast,
        },
        "electron_fluence": {
            "description": "Relativistic electron fluence forecast — internal charging risk",
            "entries": electron_forecast,
        },
        "intel_note": (
            "Kp >= 5 forecast = G1 storm expected; Kp >= 7 = G3 strong storm.  "
            "Elevated electron fluence = internal charging risk for GEO satellites "
            "(Milstar, AEHF, WGS, SBIRS).  F10.7 > 200 = elevated ionospheric "
            "density affecting OTH radar and satellite drag."
        ),
        "fetched_at": time.time(),
    }

    return _store("forecasts", data)


# ---------------------------------------------------------------------------
# 9. ENLIL Solar Wind Model — time series
# ---------------------------------------------------------------------------

async def fetch_enlil_model(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    WSA-ENLIL solar wind model — predicted conditions at Earth.
    Includes radial velocity, density, temperature, magnetic field vectors,
    polarity, and CME cloud parameter.
    """
    cached = _cached("enlil", _TTL_ENLIL)
    if cached is not None:
        return cached

    raw = await _fetch_json(
        client,
        f"{_SWPC_BASE}/json/enlil_time_series.json",
        timeout=30,
    )

    entries: List[Dict[str, Any]] = []
    if isinstance(raw, list):
        for row in raw:
            if not isinstance(row, dict):
                continue
            entries.append({
                "time": row.get("time_tag", ""),
                "density": row.get("earth_particles_per_cm3"),
                "temperature": row.get("temperature"),
                "v_r": row.get("v_r"),
                "b_r": row.get("b_r"),
                "b_theta": row.get("b_theta"),
                "b_phi": row.get("b_phi"),
                "polarity": row.get("polarity"),
                "cloud": row.get("cloud"),
            })

    # Downsample if large (2-min cadence over ~7 days = ~5000 entries)
    if len(entries) > 500:
        entries = entries[::10]  # every 20 min

    # Detect CME arrivals — cloud parameter spikes
    cme_arrivals: List[Dict[str, Any]] = []
    for e in entries:
        cloud_val = e.get("cloud")
        if cloud_val is not None:
            try:
                if float(cloud_val) > 1e-10:
                    cme_arrivals.append({
                        "time": e["time"],
                        "cloud": cloud_val,
                        "speed": e.get("v_r"),
                    })
            except (ValueError, TypeError):
                pass

    data: Dict[str, Any] = {
        "description": "WSA-ENLIL solar wind model — predicted Earth conditions",
        "entry_count": len(entries),
        "entries": entries,
        "cme_arrivals_detected": len(cme_arrivals),
        "cme_arrivals": cme_arrivals[:20],
        "animation_endpoint": f"{_SWPC_BASE}/products/animations/enlil.json",
        "intel_note": (
            "ENLIL predicts solar wind structure 1-4 days ahead.  "
            "Non-zero 'cloud' parameter = modeled CME passage at Earth.  "
            "Use with LASCO coronagraph imagery for confirmation."
        ),
        "fetched_at": time.time(),
    }

    return _store("enlil", data)


# ---------------------------------------------------------------------------
# 10. Composite Environment — everything in one call
# ---------------------------------------------------------------------------

async def get_enhanced_environment(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Master composite of all enhanced environmental data.
    Single endpoint for the dashboard to consume.
    """
    cached = _cached("enhanced_env", _TTL_ENHANCED)
    if cached is not None:
        return cached

    # Use asyncio.wait_for with 8s timeout per sub-fetch
    # If any sub-fetch is slow, return empty dict instead of blocking everything
    async def _safe_fetch(coro):
        try:
            return await asyncio.wait_for(coro, timeout=8.0)
        except Exception:
            return {}

    (
        imagery,
        aurora,
        solar_wind,
        geospace,
        debris,
        goes,
        solar_activity,
        forecasts,
        enlil,
    ) = await asyncio.gather(
        _safe_fetch(fetch_solar_imagery(client)),
        _safe_fetch(fetch_aurora_data(client)),
        _safe_fetch(fetch_solar_wind_history(client)),
        _safe_fetch(fetch_geospace_data(client)),
        _safe_fetch(fetch_debris_alerts(client)),
        _safe_fetch(fetch_goes_data(client)),
        _safe_fetch(fetch_solar_activity(client)),
        _safe_fetch(fetch_forecasts(client)),
        _safe_fetch(fetch_enlil_model(client)),
    )

    data: Dict[str, Any] = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "solar_imagery": imagery,
        "aurora": aurora,
        "solar_wind_7day": solar_wind,
        "geospace": geospace,
        "debris_awareness": debris,
        "goes_instruments": goes,
        "solar_activity": solar_activity,
        "forecasts": forecasts,
        "enlil_model": enlil,
        "source_catalog": {
            "noaa_swpc": {
                "base": _SWPC_BASE,
                "endpoints_used": [
                    "/json/ovation_aurora_latest.json",
                    "/products/solar-wind/plasma-7-day.json",
                    "/products/solar-wind/mag-7-day.json",
                    "/products/geospace/propagated-solar-wind-1-hour.json",
                    "/json/goes/primary/xrays-1-day.json",
                    "/json/goes/primary/integral-protons-1-day.json",
                    "/json/goes/primary/magnetometers-1-day.json",
                    "/json/solar_probabilities.json",
                    "/json/solar_regions.json",
                    "/products/noaa-planetary-k-index-forecast.json",
                    "/json/45-day-forecast.json",
                    "/json/electron_fluence_forecast.json",
                    "/json/enlil_time_series.json",
                    "/json/icao-space-weather-advisories.json",
                    "/products/animations/enlil.json",
                    "/products/animations/lasco-c2.json",
                    "/products/animations/lasco-c3.json",
                    "/images/animations/suvi/primary/*/latest.png",
                    "/images/animations/sdo-hmii/latest.jpg",
                    "/images/animations/ovation/north/latest.jpg",
                    "/images/animations/ovation/south/latest.jpg",
                    "/images/synoptic-map.jpg",
                ],
            },
            "celestrak": {
                "base": "https://celestrak.org",
                "endpoints_used": [
                    "/NORAD/elements/gp.php?GROUP=last-30-days&FORMAT=json",
                ],
            },
            "future_integration": [
                "Space-Track.org CDM (free account required)",
                "ESA DISCOS (free account required)",
                "USGS Earthquake API (nuclear test / ASAT correlation)",
                "USCG NAVCEN GPS NANU (GPS outage notices)",
                "FAA NOTAM API (space launch TFRs)",
            ],
        },
        "fetched_at": time.time(),
    }

    return _store("enhanced_env", data)


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _safe_float(val: Any) -> Optional[float]:
    """Convert to float or return None."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
