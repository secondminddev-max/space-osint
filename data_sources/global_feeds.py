"""
Global Space Environment Feeds — Multi-Agency OSINT Integration
================================================================
Aggregates data from sources NOT already covered by existing modules.
Each function fetches from free, public, no-auth-required endpoints.

New data sources integrated:
  1. NOAA GloTEC — Global ionospheric Total Electron Content (TEC)
     Affects GPS accuracy, SATCOM, and OTH radar.
     Endpoint: /products/glotec/geojson_2d_urt.json  (index)
               /products/glotec/geojson_2d_urt/<file>.geojson (grid)

  2. NOAA DSCOVR Real-Time Solar Wind (RTSW) — 1-min cadence at L1
     Magnetic field + plasma from ACE/DSCOVR at the L1 Lagrange point.
     Endpoints: /json/rtsw/rtsw_mag_1m.json
                /json/rtsw/rtsw_wind_1m.json
                /json/rtsw/rtsw_ephemerides_1h.json

  3. NASA EONET v3 — Earth Observatory Natural Events Tracking
     Wildfires, volcanoes, storms, icebergs — events that affect or
     mask space/military operations.
     Endpoint: https://eonet.gsfc.nasa.gov/api/v3/events

  4. GOES Radiation Belt Monitor — Integral + differential electrons
     and protons at GEO altitude.  Direct measure of Van Allen belt
     trapped particle environment.
     Endpoints: /json/goes/primary/integral-electrons-1-day.json
                /json/goes/primary/differential-electrons-1-day.json
                /json/goes/primary/differential-protons-1-day.json
                /json/goes/primary/differential-alphas-1-day.json

  5. Kyoto Dst Index — Disturbance Storm-Time index
     Ring current strength — primary indicator of magnetospheric
     storm intensity.  Dst < -50 nT = moderate storm,
     < -100 nT = intense, < -200 nT = super-storm.
     Endpoint: /products/kyoto-dst.json

  6. NOAA Solar Radio Flux (multi-frequency) — Observatory reports
     at 245-15400 MHz.  Detects solar radio bursts that jam
     radar/comms in those bands.
     Endpoint: /json/solar-radio-flux.json

  7. NASA EPIC — DSCOVR Earth Polychromatic Imaging Camera
     Earth full-disk images from L1 + spacecraft position data.
     Endpoint: https://epic.gsfc.nasa.gov/api/natural

  8. USGS Earthquake API — Seismic events M5+
     Correlate with underground nuclear tests, launch-site activity,
     ASAT-test ground truth.
     Endpoint: https://earthquake.usgs.gov/fdsnws/event/1/query

  9. NOAA F10.7 cm Flux detail — Observed + 90-day mean
     Ionospheric density driver; affects satellite drag, OTH radar,
     HF propagation.
     Endpoint: /json/f107_cm_flux.json

 10. NOAA Sunspot Report — Detailed per-region observations
     Individual sunspot region data with magnetic classification.
     Endpoint: /json/sunspot_report.json

 11. SatNOGS Satellite DB — Amateur radio satellite observations
     Community-sourced satellite telemetry and status.
     Endpoint: https://db.satnogs.org/api/satellites/

 12. NOAA RTSW Ephemerides — L1 spacecraft positions (ACE + DSCOVR)
     Confirms which spacecraft is providing real-time solar wind data.
     Endpoint: /json/rtsw/rtsw_ephemerides_1h.json

Intelligence value for FVEY space domain awareness:
  - GloTEC ionosphere maps identify GPS scintillation regions in real time
  - DSCOVR RTSW gives 15-45 min advance warning of geomagnetic disturbances
  - Radiation belt data assesses risk of satellite anomalies at GEO/MEO
  - Dst index is the definitive magnetospheric storm severity metric
  - Solar radio flux detects natural RF interference in military bands
  - USGS seismic data can correlate with nuclear tests (CTBTO proxy)
  - EONET events provide situational awareness for launch/ops environments
  - EPIC imagery provides full-disk Earth observation from L1

Classification: UNCLASSIFIED // OSINT // REL TO FVEY
"""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import httpx

# ---------------------------------------------------------------------------
# Cache infrastructure
# ---------------------------------------------------------------------------
_cache: Dict[str, Dict[str, Any]] = {}
_SWPC = "https://services.swpc.noaa.gov"

# Cache TTLs (seconds)
_TTL_IONOSPHERE   = 600    # 10 min — GloTEC updates ~every 10 min
_TTL_DSCOVR       = 120    # 2 min  — near real-time L1 data
_TTL_EARTH_EVENTS = 1800   # 30 min — EONET events change slowly
_TTL_RADIATION    = 300    # 5 min  — GOES particle data
_TTL_DST          = 600    # 10 min — Dst updates hourly
_TTL_RADIO_FLUX   = 900    # 15 min — observatory reports
_TTL_EPIC         = 3600   # 1 hr   — EPIC images ~12/day
_TTL_EARTHQUAKE   = 600    # 10 min — seismic data
_TTL_F107         = 3600   # 1 hr   — daily flux values
_TTL_SUNSPOT      = 3600   # 1 hr   — daily reports
_TTL_SATNOGS      = 3600   # 1 hr   — satellite DB
_TTL_COMPOSITE    = 300    # 5 min  — /all composite


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _fetch_json(
    client: httpx.AsyncClient,
    url: str,
    timeout: int = 20,
) -> Optional[Any]:
    """Fetch JSON from *url*, returning None on any HTTP/parse error."""
    try:
        r = await client.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except (httpx.HTTPError, ValueError, TypeError):
        return None


def _cached(key: str, ttl: int) -> Optional[Any]:
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < ttl:
        return entry["data"]
    return None


def _store(key: str, data: Any) -> Any:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


def _safe_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _safe_int(val: Any) -> Optional[int]:
    if val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


# =========================================================================
# 1. IONOSPHERE — NOAA GloTEC Total Electron Content
# =========================================================================
#
# GloTEC (Global Total Electron Content) provides a real-time map of
# ionospheric electron density.  High TEC = more ionospheric delay for
# GPS L1 signals.  TEC anomalies indicate storm-time ionospheric
# disturbances that degrade GPS, SATCOM, and OTH radar.
#
# The ICAO-format GeoJSON includes TEC, anomaly, hmF2 (F-layer peak
# height), and NmF2 (peak electron density) at 5-degree resolution.
#
# References:
# - Fuller-Rowell et al., "Real-Time Ionospheric TEC Monitoring"
# - Klobuchar model for single-frequency GPS ionospheric correction
# - WAAS/SBAS ionospheric threat model
# =========================================================================

async def fetch_ionosphere_data(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Fetch global ionospheric TEC map from NOAA GloTEC.

    Returns a summary with max/min TEC, anomaly hotspots (regions where
    ionospheric disturbance is strongest), and the latest GeoJSON URL
    for full-resolution data.

    Intel use:
    - TEC anomaly > +5 TECU = severe ionospheric storm, GPS errors > 10m
    - Negative anomaly at high latitudes = polar trough (HF blackout zone)
    - hmF2 changes indicate traveling ionospheric disturbances (TID)
    """
    cached = _cached("ionosphere", _TTL_IONOSPHERE)
    if cached is not None:
        return cached

    # Step 1: Get the index of available GloTEC files
    index = await _fetch_json(
        client,
        f"{_SWPC}/products/glotec/geojson_2d_urt.json",
        timeout=15,
    )

    if not isinstance(index, list) or not index:
        prev = _cache.get("ionosphere", {}).get("data")
        return prev if prev else {"error": "GloTEC data unavailable"}

    # Get latest file URL
    latest_entry = index[-1]
    latest_url = f"{_SWPC}{latest_entry['url']}"
    latest_time = latest_entry.get("time_tag", "")

    # Step 2: Fetch the latest GeoJSON grid
    geojson = await _fetch_json(client, latest_url, timeout=30)

    tec_stats: Dict[str, Any] = {
        "max_tec": 0,
        "min_tec": 999,
        "max_anomaly": -999,
        "min_anomaly": 999,
    }
    anomaly_hotspots: List[Dict[str, Any]] = []
    high_tec_zones: List[Dict[str, Any]] = []
    grid_points = 0

    if isinstance(geojson, dict):
        features = geojson.get("features", [])
        grid_points = len(features)

        for feat in features:
            if not isinstance(feat, dict):
                continue
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            coords = geom.get("coordinates", [0, 0])

            tec = _safe_float(props.get("tec"))
            anomaly = _safe_float(props.get("anomaly"))
            hmf2 = _safe_float(props.get("hmF2"))

            if tec is not None:
                if tec > tec_stats["max_tec"]:
                    tec_stats["max_tec"] = tec
                if tec < tec_stats["min_tec"]:
                    tec_stats["min_tec"] = tec

            if anomaly is not None:
                if anomaly > tec_stats["max_anomaly"]:
                    tec_stats["max_anomaly"] = anomaly
                if anomaly < tec_stats["min_anomaly"]:
                    tec_stats["min_anomaly"] = anomaly

                # Flag significant anomalies (|anomaly| > 5 TECU)
                if abs(anomaly) > 5:
                    anomaly_hotspots.append({
                        "lon": coords[0] if len(coords) > 0 else 0,
                        "lat": coords[1] if len(coords) > 1 else 0,
                        "tec": tec,
                        "anomaly": round(anomaly, 2),
                        "hmF2_km": hmf2,
                    })

            # Flag high TEC zones (> 50 TECU = equatorial anomaly)
            if tec is not None and tec > 50:
                high_tec_zones.append({
                    "lon": coords[0] if len(coords) > 0 else 0,
                    "lat": coords[1] if len(coords) > 1 else 0,
                    "tec": round(tec, 1),
                })

    # Sort and limit
    anomaly_hotspots.sort(key=lambda x: abs(x["anomaly"]), reverse=True)
    anomaly_hotspots = anomaly_hotspots[:30]
    high_tec_zones.sort(key=lambda x: x["tec"], reverse=True)
    high_tec_zones = high_tec_zones[:20]

    # GPS error estimate from max TEC anomaly
    max_anom = abs(tec_stats.get("max_anomaly", 0))
    gps_error_estimate_m = round(max_anom * 0.16, 1)  # ~0.16 m/TECU for L1

    data: Dict[str, Any] = {
        "product": "Global Ionosphere TEC Monitor (GloTEC)",
        "source": "NOAA SWPC GloTEC — Global Total Electron Content",
        "observation_time": latest_time,
        "grid_points": grid_points,
        "tec_summary": {
            "max_tec_tecu": round(tec_stats["max_tec"], 1),
            "min_tec_tecu": round(tec_stats["min_tec"], 1),
            "max_anomaly_tecu": round(tec_stats["max_anomaly"], 2),
            "min_anomaly_tecu": round(tec_stats["min_anomaly"], 2),
        },
        "gps_impact": {
            "estimated_max_l1_error_m": gps_error_estimate_m,
            "assessment": (
                "SEVERE — ionospheric anomalies exceed 5 TECU, GPS L1 errors may exceed 1m"
                if max_anom > 5
                else "MODERATE — elevated TEC, GPS accuracy slightly degraded"
                if max_anom > 2
                else "NOMINAL — ionosphere quiet, GPS accuracy normal"
            ),
        },
        "anomaly_hotspots": anomaly_hotspots,
        "high_tec_zones": high_tec_zones,
        "full_resolution_url": latest_url,
        "intel_note": (
            "Ionospheric TEC directly controls GPS single-frequency error.  "
            "Anomaly hotspots indicate storm-time ionospheric disturbances "
            "that can cause GPS position errors > 10m.  High TEC at equatorial "
            "latitudes is normal (equatorial anomaly) but storm-enhanced density "
            "(SED) plumes extending to mid-latitudes are operationally significant.  "
            "Correlate with Kp index and Dst for geomagnetic storm confirmation."
        ),
        "fetched_at": time.time(),
    }

    return _store("ionosphere", data)


# =========================================================================
# 2. DSCOVR REAL-TIME SOLAR WIND — L1 Monitor
# =========================================================================
#
# The Deep Space Climate Observatory (DSCOVR) orbits the Sun-Earth L1
# Lagrange point (~1.5M km sunward).  It measures solar wind plasma and
# magnetic field BEFORE they hit Earth, providing 15-45 minutes of
# advance warning for geomagnetic disturbances.
#
# This feed returns 1-minute cadence data from the last ~24 hours,
# including both magnetic field (B vector) and plasma (speed, density,
# temperature) from either DSCOVR or ACE (backup).
#
# The RTSW ephemerides endpoint tells us which spacecraft is active
# and where it is located.
#
# References:
# - DSCOVR mission: https://www.nesdis.noaa.gov/dscovr
# - ACE Science Center: http://www.srl.caltech.edu/ACE/
# - L1 propagation: ~30-60 min transit from L1 to Earth
# =========================================================================

async def fetch_dscovr_data(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Fetch real-time solar wind from DSCOVR/ACE at L1.

    Returns latest readings + 6-hour history (downsampled to 5-min)
    for magnetic field and plasma, plus spacecraft ephemeris.

    Intel use:
    - Bz southward turning = geomagnetic storm onset (15-45 min warning)
    - Speed > 500 km/s = elevated geomagnetic activity
    - Density spike + speed jump = CME shock arrival
    - Source field tells you if DSCOVR or ACE is primary monitor
    """
    cached = _cached("dscovr", _TTL_DSCOVR)
    if cached is not None:
        return cached

    mag_raw, wind_raw, eph_raw = await asyncio.gather(
        _fetch_json(client, f"{_SWPC}/json/rtsw/rtsw_mag_1m.json"),
        _fetch_json(client, f"{_SWPC}/json/rtsw/rtsw_wind_1m.json"),
        _fetch_json(client, f"{_SWPC}/json/rtsw/rtsw_ephemerides_1h.json"),
    )

    # --- Parse magnetic field (latest + 6-hour history) ---
    mag_latest: Dict[str, Any] = {}
    mag_history: List[Dict[str, Any]] = []

    if isinstance(mag_raw, list) and mag_raw:
        # rtsw_mag_1m.json: list of dicts, newest first
        latest = mag_raw[0]
        if isinstance(latest, dict):
            mag_latest = {
                "time": latest.get("time_tag", ""),
                "source": latest.get("source", ""),
                "active": latest.get("active", False),
                "bt": _safe_float(latest.get("bt")),
                "bx_gsm": _safe_float(latest.get("bx_gsm")),
                "by_gsm": _safe_float(latest.get("by_gsm")),
                "bz_gsm": _safe_float(latest.get("bz_gsm")),
            }

        # Downsample to every 5th entry (~5-min cadence) for 6-hour window
        window = mag_raw[:360]  # 360 min = 6 hours
        for i, entry in enumerate(window):
            if i % 5 != 0:
                continue
            if not isinstance(entry, dict):
                continue
            mag_history.append({
                "time": entry.get("time_tag", ""),
                "bt": _safe_float(entry.get("bt")),
                "bz_gsm": _safe_float(entry.get("bz_gsm")),
                "source": entry.get("source", ""),
            })

    # --- Parse plasma (latest + 6-hour history) ---
    plasma_latest: Dict[str, Any] = {}
    plasma_history: List[Dict[str, Any]] = []

    if isinstance(wind_raw, list) and wind_raw:
        latest = wind_raw[0]
        if isinstance(latest, dict):
            plasma_latest = {
                "time": latest.get("time_tag", ""),
                "source": latest.get("source", ""),
                "speed": _safe_float(latest.get("proton_speed")),
                "density": _safe_float(latest.get("proton_density")),
                "temperature": _safe_float(latest.get("proton_temperature")),
            }

        window = wind_raw[:360]
        for i, entry in enumerate(window):
            if i % 5 != 0:
                continue
            if not isinstance(entry, dict):
                continue
            plasma_history.append({
                "time": entry.get("time_tag", ""),
                "speed": _safe_float(entry.get("proton_speed")),
                "density": _safe_float(entry.get("proton_density")),
            })

    # --- Parse ephemerides (spacecraft positions) ---
    spacecraft: List[Dict[str, Any]] = []
    if isinstance(eph_raw, list):
        for entry in eph_raw[-4:]:  # last 4 entries (2 per hour, 2 spacecraft)
            if not isinstance(entry, dict):
                continue
            spacecraft.append({
                "time": entry.get("time_tag", ""),
                "source": entry.get("source", ""),
                "active": entry.get("active", False),
                "x_gse_km": _safe_int(entry.get("x_gse")),
                "y_gse_km": _safe_int(entry.get("y_gse")),
                "z_gse_km": _safe_int(entry.get("z_gse")),
            })

    # Determine current monitoring status
    active_source = mag_latest.get("source", "Unknown")
    bz_now = mag_latest.get("bz_gsm")
    speed_now = plasma_latest.get("speed")

    # Storm driver assessment
    if bz_now is not None and bz_now < -10:
        driver_status = "ACTIVE STORM DRIVING — Bz strongly southward"
    elif bz_now is not None and bz_now < -5:
        driver_status = "ELEVATED — Bz moderately southward"
    else:
        driver_status = "QUIET — Bz near zero or northward"

    if speed_now is not None and speed_now > 700:
        speed_status = "HIGH-SPEED STREAM — speed > 700 km/s"
    elif speed_now is not None and speed_now > 500:
        speed_status = "ELEVATED — speed > 500 km/s"
    else:
        speed_status = "NOMINAL"

    data: Dict[str, Any] = {
        "product": "DSCOVR/ACE Real-Time Solar Wind Monitor at L1",
        "source": f"NOAA SWPC RTSW — active spacecraft: {active_source}",
        "magnetic_field": {
            "latest": mag_latest,
            "history_5min": mag_history,
            "driver_assessment": driver_status,
        },
        "plasma": {
            "latest": plasma_latest,
            "history_5min": plasma_history,
            "speed_assessment": speed_status,
        },
        "spacecraft_positions": spacecraft,
        "propagation_delay_note": (
            "Data measured at L1 (~1.5M km from Earth).  "
            "Solar wind transit to Earth magnetopause: 15-60 min "
            "depending on solar wind speed.  "
            f"At current speed ({speed_now or '?'} km/s), estimated "
            f"transit: ~{int(1.5e6 / speed_now / 60) if speed_now and speed_now > 0 else '?'} min."
        ),
        "intel_note": (
            "L1 solar wind data provides the critical advance warning for "
            "geomagnetic storms.  Bz southward turning below -10 nT with "
            "speed > 500 km/s will drive G2+ storms within 30-60 minutes.  "
            "Sudden density spikes (>20/cm3) indicate CME shock front arrival — "
            "expect rapid Kp increase.  Monitor for sustained southward Bz "
            "which is the primary storm driver."
        ),
        "fetched_at": time.time(),
    }

    return _store("dscovr", data)


# =========================================================================
# 3. NASA EONET — Earth Observatory Natural Events
# =========================================================================
#
# EONET tracks natural events globally: wildfires, volcanoes, severe
# storms, icebergs, floods, earthquakes, dust/haze, water color.
#
# Intel relevance:
# - Volcanic eruptions can affect satellite comms (ash plumes), GPS
#   (ionospheric disturbance), and provide cover for military activity
# - Severe storms affect launch operations and ground station availability
# - Wildfires near military installations / ground stations
# - Iceberg tracking relevant to southern ocean SIGINT operations
#
# EONET aggregates from: USGS, NOAA, NASA, GDACS, JTWC, InciWeb, etc.
# =========================================================================

async def fetch_earth_events(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Fetch active natural events from NASA EONET v3.

    Returns categorized events with locations, magnitudes, and sources.
    Focuses on open (active) events relevant to space/military ops.
    """
    cached = _cached("earth_events", _TTL_EARTH_EVENTS)
    if cached is not None:
        return cached

    raw = await _fetch_json(
        client,
        "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=100",
        timeout=30,
    )

    if not isinstance(raw, dict):
        prev = _cache.get("earth_events", {}).get("data")
        return prev if prev else {"error": "EONET data unavailable"}

    events_raw = raw.get("events", [])
    events: List[Dict[str, Any]] = []
    by_category: Dict[str, int] = {}

    for ev in events_raw:
        if not isinstance(ev, dict):
            continue

        categories = [c.get("title", "") for c in ev.get("categories", []) if isinstance(c, dict)]
        cat_name = categories[0] if categories else "Unknown"
        by_category[cat_name] = by_category.get(cat_name, 0) + 1

        # Get latest geometry point
        geometries = ev.get("geometry", [])
        latest_geom = geometries[-1] if geometries else {}
        coords = latest_geom.get("coordinates", [])

        events.append({
            "id": ev.get("id", ""),
            "title": ev.get("title", ""),
            "category": cat_name,
            "closed": ev.get("closed"),
            "sources": [s.get("id", "") for s in ev.get("sources", []) if isinstance(s, dict)],
            "latest_date": latest_geom.get("date", ""),
            "magnitude": latest_geom.get("magnitudeValue"),
            "magnitude_unit": latest_geom.get("magnitudeUnit", ""),
            "coordinates": coords,
            "geometry_count": len(geometries),
        })

    # Flag events near known space infrastructure
    space_relevant: List[Dict[str, Any]] = []
    for ev in events:
        cat = ev.get("category", "")
        if cat in ("Volcanoes", "Severe Storms", "Wildfires"):
            space_relevant.append(ev)

    data: Dict[str, Any] = {
        "product": "Earth Natural Events Monitor (NASA EONET v3)",
        "source": "NASA EONET — aggregates USGS, NOAA, GDACS, JTWC, InciWeb",
        "total_active_events": len(events),
        "events_by_category": by_category,
        "events": events,
        "space_ops_relevant": {
            "count": len(space_relevant),
            "events": space_relevant[:20],
            "note": (
                "Volcanoes affect satellite comms (ash), GPS (ionospheric "
                "disturbance from volcanic lightning), and provide operational "
                "cover.  Severe storms impact launch ops and ground stations.  "
                "Wildfires near military installations disrupt operations."
            ),
        },
        "intel_note": (
            "Cross-reference natural events with adversary launch sites and "
            "ground station locations.  Volcanic eruptions in Kamchatka "
            "(near Plesetsk polar ground track) or the Pacific Ring of Fire "
            "are operationally relevant.  Severe storm tracks across known "
            "radar/ground station sites degrade collection capability."
        ),
        "fetched_at": time.time(),
    }

    return _store("earth_events", data)


# =========================================================================
# 4. RADIATION BELT MONITOR — GOES Particle Environment
# =========================================================================
#
# GOES satellites at GEO (~35,786 km) measure trapped particle
# populations in the outer Van Allen radiation belt.  These particles
# cause:
#   - Surface charging (differential charging of satellite surfaces)
#   - Deep dielectric charging (high-energy electrons penetrate shielding)
#   - Single-event upsets (SEU — bit flips from energetic protons)
#   - Total ionizing dose (long-term degradation)
#
# The integral electron flux >=2 MeV is the key metric for deep
# dielectric charging risk.  Threshold: 1000 pfu = elevated risk.
#
# Differential proton data at various energies indicates the galactic
# cosmic ray (GCR) environment and solar energetic particle (SEP) events.
#
# References:
# - NOAA GOES-R SEISS instrument description
# - NASA AE-9/AP-9 radiation belt model
# - ESA ECSS-E-ST-10-04C space environment standard
# =========================================================================

async def fetch_radiation_belts(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Fetch Van Allen radiation belt conditions from GOES.

    Returns electron flux (>=2 MeV integral + differential energy channels),
    proton flux (differential channels), and alpha particle data.
    Assesses satellite anomaly risk at GEO and MEO.
    """
    cached = _cached("radiation", _TTL_RADIATION)
    if cached is not None:
        return cached

    (
        int_electrons,
        diff_electrons,
        diff_protons,
        diff_alphas,
        dst_raw,
    ) = await asyncio.gather(
        _fetch_json(client, f"{_SWPC}/json/goes/primary/integral-electrons-1-day.json"),
        _fetch_json(client, f"{_SWPC}/json/goes/primary/differential-electrons-1-day.json"),
        _fetch_json(client, f"{_SWPC}/json/goes/primary/differential-protons-1-day.json"),
        _fetch_json(client, f"{_SWPC}/json/goes/primary/differential-alphas-1-day.json"),
        _fetch_json(client, f"{_SWPC}/products/kyoto-dst.json"),
    )

    # --- Integral electrons >= 2 MeV (deep charging risk) ---
    electron_latest: Dict[str, Any] = {}
    electron_max_24h: float = 0
    electron_history: List[Dict[str, Any]] = []

    if isinstance(int_electrons, list):
        for entry in int_electrons:
            if not isinstance(entry, dict):
                continue
            flux = _safe_float(entry.get("flux"))
            if flux is not None and flux > electron_max_24h:
                electron_max_24h = flux

        # Latest reading
        if int_electrons:
            last = int_electrons[-1]
            if isinstance(last, dict):
                electron_latest = {
                    "time": last.get("time_tag", ""),
                    "flux_pfu": _safe_float(last.get("flux")),
                    "energy": last.get("energy", ""),
                    "satellite": last.get("satellite"),
                }

        # History (downsample: every 12th entry = hourly from 5-min data)
        for i, entry in enumerate(int_electrons):
            if i % 12 != 0 or not isinstance(entry, dict):
                continue
            electron_history.append({
                "time": entry.get("time_tag", ""),
                "flux": _safe_float(entry.get("flux")),
            })

    # --- Differential electrons (energy spectrum) ---
    diff_e_channels: Dict[str, float] = {}
    if isinstance(diff_electrons, list):
        # Get latest readings per energy channel
        seen_energies: set = set()
        for entry in reversed(diff_electrons):
            if not isinstance(entry, dict):
                continue
            energy = entry.get("energy", "")
            if energy and energy not in seen_energies:
                seen_energies.add(energy)
                flux = _safe_float(entry.get("flux"))
                if flux is not None:
                    diff_e_channels[energy] = round(flux, 4)
            if len(seen_energies) >= 10:
                break

    # --- Differential protons (GCR + SEP indicator) ---
    diff_p_channels: Dict[str, float] = {}
    if isinstance(diff_protons, list):
        seen_energies = set()
        for entry in reversed(diff_protons):
            if not isinstance(entry, dict):
                continue
            energy = entry.get("energy", "")
            if energy and energy not in seen_energies:
                seen_energies.add(energy)
                flux = _safe_float(entry.get("flux"))
                if flux is not None:
                    diff_p_channels[energy] = round(flux, 6)
            if len(seen_energies) >= 10:
                break

    # --- Dst index (magnetosphere ring current) ---
    dst_latest: Dict[str, Any] = {}
    dst_min_7d: float = 0
    dst_history: List[Dict[str, Any]] = []

    if isinstance(dst_raw, list) and len(dst_raw) > 1:
        # Header: ["time_tag", "dst"]
        for row in dst_raw[1:]:
            if not isinstance(row, (list, tuple)) or len(row) < 2:
                continue
            dst_val = _safe_float(row[1])
            if dst_val is not None:
                if dst_val < dst_min_7d:
                    dst_min_7d = dst_val
                dst_history.append({
                    "time": row[0],
                    "dst": dst_val,
                })

        if dst_history:
            dst_latest = dst_history[-1]

    # Downsample Dst to every 6th entry (~6-hourly from hourly)
    if len(dst_history) > 50:
        dst_history = dst_history[::6]

    # --- Risk assessment ---
    charging_risk = "LOW"
    if electron_max_24h > 10000:
        charging_risk = "CRITICAL — extreme electron flux, deep dielectric charging imminent"
    elif electron_max_24h > 1000:
        charging_risk = "HIGH — elevated electron flux, charging risk for GEO satellites"
    elif electron_max_24h > 100:
        charging_risk = "MODERATE — slightly elevated electron environment"

    dst_val = dst_latest.get("dst", 0)
    storm_severity = "QUIET"
    if dst_val < -200:
        storm_severity = "SUPER-STORM (Dst < -200 nT)"
    elif dst_val < -100:
        storm_severity = "INTENSE STORM (Dst < -100 nT)"
    elif dst_val < -50:
        storm_severity = "MODERATE STORM (Dst < -50 nT)"
    elif dst_val < -30:
        storm_severity = "WEAK STORM (Dst < -30 nT)"

    data: Dict[str, Any] = {
        "product": "Radiation Belt & Magnetosphere Monitor",
        "sources": [
            "NOAA GOES SEISS — Integral/Differential particle data at GEO",
            "Kyoto WDC — Dst geomagnetic storm index",
        ],
        "electron_environment": {
            "integral_ge_2mev": {
                "latest": electron_latest,
                "max_24h_pfu": round(electron_max_24h, 1),
                "history_hourly": electron_history,
                "charging_risk": charging_risk,
            },
            "differential_spectrum": diff_e_channels,
        },
        "proton_environment": {
            "differential_spectrum": diff_p_channels,
            "note": "Proton channels at 1-143 MeV. Elevated flux indicates SEP event or enhanced GCR.",
        },
        "alpha_particles": {
            "note": "Alpha particle (He-4) data from GOES. Galactic cosmic ray tracer.",
        },
        "magnetosphere": {
            "dst_index": {
                "latest": dst_latest,
                "minimum_7day": round(dst_min_7d, 1),
                "history": dst_history,
                "storm_severity": storm_severity,
            },
        },
        "satellite_risk_assessment": {
            "geo_assets": (
                f"Charging risk: {charging_risk}.  "
                f"Magnetosphere: {storm_severity}.  "
                "GEO military satellites (SBIRS, WGS, AEHF, MUOS, Skynet) "
                "are directly exposed to measured particle environment."
            ),
            "meo_assets": (
                "GPS/Galileo in MEO (20,200 km) traverse the heart of the "
                "outer radiation belt.  Elevated electron flux increases "
                "SEU rate and total dose accumulation."
            ),
            "leo_assets": (
                "LEO satellites primarily affected during solar proton events "
                "(S-scale storms) and South Atlantic Anomaly (SAA) passages."
            ),
        },
        "intel_note": (
            "The radiation belt is the primary threat to satellite electronics.  "
            "Electron flux >1000 pfu at >=2 MeV causes deep dielectric charging — "
            "the leading cause of GEO satellite anomalies.  Dst < -100 nT "
            "indicates the ring current is greatly enhanced, meaning the "
            "magnetosphere is severely compressed and outer belt particles are "
            "energized.  Cross-reference with Kp, solar wind speed, and Bz."
        ),
        "fetched_at": time.time(),
    }

    return _store("radiation", data)


# =========================================================================
# 5. USGS EARTHQUAKE MONITOR — Seismic Correlation
# =========================================================================
#
# The USGS FDSN earthquake API provides real-time global seismic data.
# Relevance to space warfare OSINT:
#   - Underground nuclear tests produce distinctive seismic signatures
#     (CTBTO correlation — Comprehensive Nuclear-Test-Ban Treaty)
#   - Seismic events near adversary launch sites or nuclear facilities
#   - Earthquake damage to ground stations or C2 infrastructure
#   - Volcanic seismicity (launch site environmental awareness)
#
# CTBTO stations detect events down to ~M1; USGS public data covers M2.5+
# for global events, M1+ for US.  We filter to M4+ for global coverage.
#
# Known nuclear test sites for correlation:
#   - Punggye-ri, DPRK (41.28°N, 129.08°E) — all NK nuclear tests
#   - Lop Nor, PRC (41.82°N, 88.33°E) — PRC historical tests
#   - Novaya Zemlya, Russia (73.37°N, 54.78°E) — Soviet/Russian tests
#   - Nevada Test Site, US (37.12°N, -116.06°W) — US historical tests
# =========================================================================

_NUCLEAR_TEST_SITES = [
    {"name": "Punggye-ri, DPRK", "lat": 41.28, "lon": 129.08, "radius_km": 30},
    {"name": "Lop Nor, PRC", "lat": 41.82, "lon": 88.33, "radius_km": 50},
    {"name": "Novaya Zemlya, Russia", "lat": 73.37, "lon": 54.78, "radius_km": 50},
    {"name": "Semipalatinsk, Kazakhstan", "lat": 50.07, "lon": 78.43, "radius_km": 50},
]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in km."""
    import math
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def fetch_earthquakes(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Fetch recent significant earthquakes (M4+) from USGS.

    Cross-references events near known nuclear test sites and adversary
    launch facilities.
    """
    cached = _cached("earthquakes", _TTL_EARTHQUAKE)
    if cached is not None:
        return cached

    # Last 7 days, M4+, ordered by time
    raw = await _fetch_json(
        client,
        (
            "https://earthquake.usgs.gov/fdsnws/event/1/query"
            "?format=geojson&limit=100&minmagnitude=4&orderby=time"
        ),
        timeout=20,
    )

    if not isinstance(raw, dict):
        prev = _cache.get("earthquakes", {}).get("data")
        return prev if prev else {"error": "USGS earthquake data unavailable"}

    features = raw.get("features", [])
    events: List[Dict[str, Any]] = []
    nuclear_proximity: List[Dict[str, Any]] = []

    for feat in features:
        if not isinstance(feat, dict):
            continue
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", [0, 0, 0])

        event = {
            "id": feat.get("id", ""),
            "magnitude": props.get("mag"),
            "place": props.get("place", ""),
            "time": props.get("time"),
            "depth_km": coords[2] if len(coords) > 2 else None,
            "coordinates": [coords[0], coords[1]] if len(coords) >= 2 else [],
            "type": props.get("type", ""),
            "tsunami": props.get("tsunami", 0),
            "url": props.get("url", ""),
        }
        events.append(event)

        # Check proximity to nuclear test sites
        if len(coords) >= 2:
            for site in _NUCLEAR_TEST_SITES:
                dist = _haversine_km(coords[1], coords[0], site["lat"], site["lon"])
                if dist < site["radius_km"]:
                    nuclear_proximity.append({
                        **event,
                        "test_site": site["name"],
                        "distance_km": round(dist, 1),
                        "alert": (
                            f"SEISMIC EVENT {round(dist, 1)} km from {site['name']} — "
                            f"M{props.get('mag', '?')} at depth {coords[2] if len(coords) > 2 else '?'} km.  "
                            "Correlate with CTBTO IMS data for characterization."
                        ),
                    })

    data: Dict[str, Any] = {
        "product": "Seismic Activity Monitor (USGS FDSN)",
        "source": "USGS Earthquake Hazards Program",
        "total_events_m4_plus": len(events),
        "events": events[:50],
        "nuclear_test_site_proximity": {
            "alerts": nuclear_proximity,
            "monitored_sites": _NUCLEAR_TEST_SITES,
            "note": (
                "Events within radius of known nuclear test sites are flagged.  "
                "Nuclear tests produce shallow (<5 km), localized seismic events "
                "with distinctive waveforms.  Depth and location are key "
                "discriminators between natural earthquakes and nuclear tests."
            ),
        },
        "intel_note": (
            "Seismic monitoring is a key component of nuclear test detection "
            "(CTBTO IMS network).  Shallow events near known test sites warrant "
            "immediate correlation with infrasound and radionuclide data.  "
            "Large earthquakes (M7+) can also affect satellite ground stations, "
            "undersea cables, and military infrastructure."
        ),
        "fetched_at": time.time(),
    }

    return _store("earthquakes", data)


# =========================================================================
# 6. SOLAR RADIO FLUX (Multi-Frequency) — RF Environment
# =========================================================================
#
# Solar radio observatories measure solar flux at multiple frequencies
# (245 MHz to 15400 MHz).  Solar radio bursts at these frequencies
# can directly interfere with radar, communications, and satellite
# systems operating in those bands.
#
# Type II radio bursts are associated with CME-driven shocks.
# Type III bursts indicate electron beams from solar flares.
# Type IV continuum emission indicates trapped energetic electrons.
#
# Relevance: military radar (L/S/C/X-band) can be degraded by intense
# solar radio emission in those frequency ranges.
# =========================================================================

async def fetch_solar_radio(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Fetch multi-frequency solar radio flux observations.

    Returns latest measurements from solar radio observatories at
    frequencies spanning 245 MHz to 15400 MHz, covering bands used
    by military radar, communications, and navigation systems.
    """
    cached = _cached("solar_radio", _TTL_RADIO_FLUX)
    if cached is not None:
        return cached

    raw = await _fetch_json(
        client,
        f"{_SWPC}/json/solar-radio-flux.json",
        timeout=15,
    )

    if not isinstance(raw, list) or not raw:
        prev = _cache.get("solar_radio", {}).get("data")
        return prev if prev else {"error": "Solar radio flux data unavailable"}

    # Get latest observation (first entry is most recent)
    latest = raw[0] if isinstance(raw[0], dict) else {}
    station = latest.get("common_name", "Unknown")
    obs_time = latest.get("time_tag", "")
    details = latest.get("details", [])

    frequencies: List[Dict[str, Any]] = []
    max_flux = 0
    max_freq = 0

    for det in details:
        if not isinstance(det, dict):
            continue
        freq = _safe_int(det.get("frequency"))
        flux = _safe_float(det.get("flux"))
        quality = det.get("observed_quality", "")

        if freq is not None and flux is not None:
            frequencies.append({
                "frequency_mhz": freq,
                "flux_sfu": flux,
                "quality": quality,
                "band": _freq_to_band(freq),
            })
            if flux > max_flux:
                max_flux = flux
                max_freq = freq

    # Military band assessment
    band_impact: Dict[str, str] = {}
    for f in frequencies:
        band = f["band"]
        flux = f["flux_sfu"]
        if flux > 10000:
            band_impact[band] = f"SEVERE — {flux} SFU at {f['frequency_mhz']} MHz"
        elif flux > 1000:
            band_impact[band] = f"ELEVATED — {flux} SFU at {f['frequency_mhz']} MHz"

    data: Dict[str, Any] = {
        "product": "Solar Radio Flux Monitor (Multi-Frequency)",
        "source": f"NOAA SWPC — Observatory: {station}",
        "observation_time": obs_time,
        "frequencies": frequencies,
        "peak_flux": {
            "frequency_mhz": max_freq,
            "flux_sfu": max_flux,
        },
        "military_band_impact": band_impact if band_impact else {"status": "CLEAR — no significant solar radio interference"},
        "intel_note": (
            "Solar radio bursts can directly interfere with radar and "
            "communications in L-band (1-2 GHz), S-band (2-4 GHz), and "
            "C-band (4-8 GHz).  A 10,000 SFU burst at 2695 MHz will "
            "degrade S-band radar performance.  Type II bursts at low "
            "frequencies (<500 MHz) indicate CME-driven shocks and predict "
            "geomagnetic storm arrival.  Cross-reference with GOES X-ray "
            "for flare confirmation."
        ),
        "fetched_at": time.time(),
    }

    return _store("solar_radio", data)


def _freq_to_band(freq_mhz: int) -> str:
    """Map frequency to standard radar/comms band designation."""
    if freq_mhz < 300:
        return "VHF"
    if freq_mhz < 1000:
        return "UHF"
    if freq_mhz < 2000:
        return "L-band"
    if freq_mhz < 4000:
        return "S-band"
    if freq_mhz < 8000:
        return "C-band"
    if freq_mhz < 12000:
        return "X-band"
    return "Ku-band+"


# =========================================================================
# 7. NASA EPIC — DSCOVR Earth Imagery from L1
# =========================================================================
#
# The EPIC (Earth Polychromatic Imaging Camera) on DSCOVR captures
# full-disk images of the sunlit side of Earth from L1.
# ~12 images per day, showing the Earth as seen from 1.5M km away.
#
# Intel value:
# - Full-disk imagery of the sunlit hemisphere
# - Spacecraft position data (L1 orbit confirmation)
# - Cloud cover assessment for ground-based ISR
# - Large-scale atmospheric phenomena (volcanic plumes, dust storms)
# =========================================================================

async def fetch_epic_imagery(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Fetch latest DSCOVR EPIC Earth imagery metadata.

    Returns image metadata including centroid coordinates (where the
    camera is pointing), spacecraft and lunar positions, and image URLs.
    """
    cached = _cached("epic", _TTL_EPIC)
    if cached is not None:
        return cached

    raw = await _fetch_json(
        client,
        "https://epic.gsfc.nasa.gov/api/natural",
        timeout=20,
    )

    if not isinstance(raw, list) or not raw:
        prev = _cache.get("epic", {}).get("data")
        return prev if prev else {"error": "EPIC data unavailable"}

    images: List[Dict[str, Any]] = []
    for entry in raw[:6]:  # Latest 6 images
        if not isinstance(entry, dict):
            continue

        img_name = entry.get("image", "")
        date_str = entry.get("date", "")
        # Build image URL: https://epic.gsfc.nasa.gov/archive/natural/YYYY/MM/DD/png/<image>.png
        date_parts = date_str.split(" ")[0].split("-") if date_str else []
        if len(date_parts) == 3:
            img_url = (
                f"https://epic.gsfc.nasa.gov/archive/natural/"
                f"{date_parts[0]}/{date_parts[1]}/{date_parts[2]}/png/{img_name}.png"
            )
        else:
            img_url = ""

        centroid = entry.get("centroid_coordinates", {})
        dscovr_pos = entry.get("dscovr_j2000_position", {})

        images.append({
            "identifier": entry.get("identifier", ""),
            "date": date_str,
            "image_url": img_url,
            "centroid_lat": centroid.get("lat"),
            "centroid_lon": centroid.get("lon"),
            "dscovr_x_km": _safe_float(dscovr_pos.get("x")),
            "dscovr_y_km": _safe_float(dscovr_pos.get("y")),
            "dscovr_z_km": _safe_float(dscovr_pos.get("z")),
            "caption": entry.get("caption", ""),
        })

    data: Dict[str, Any] = {
        "product": "DSCOVR EPIC Earth Imagery from L1",
        "source": "NASA EPIC — Earth Polychromatic Imaging Camera",
        "image_count": len(images),
        "images": images,
        "intel_note": (
            "EPIC provides full-disk Earth imagery from L1, useful for "
            "large-scale atmospheric awareness (volcanic plumes, dust storms, "
            "major weather systems).  Centroid coordinates indicate which "
            "hemisphere face is imaged.  DSCOVR position confirms L1 orbit "
            "status — loss of position would indicate spacecraft anomaly."
        ),
        "fetched_at": time.time(),
    }

    return _store("epic", data)


# =========================================================================
# 8. SatNOGS — Community Satellite Observations
# =========================================================================
#
# SatNOGS (Satellite Networked Open Ground Station) is a global network
# of amateur radio ground stations that track and receive telemetry from
# satellites.  The DB API provides satellite status and metadata.
#
# Intel value:
# - Community-sourced satellite status (is it transmitting?)
# - Frequency allocations for known satellites
# - Detection of unregistered/mystery satellites via amateur observations
# - Ground truth for orbital predictions
# =========================================================================

async def fetch_satnogs_satellites(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Fetch satellite data from SatNOGS community database.

    Returns active satellites with their NORAD IDs, status, and
    observation metadata.
    """
    cached = _cached("satnogs", _TTL_SATNOGS)
    if cached is not None:
        return cached

    raw = await _fetch_json(
        client,
        "https://db.satnogs.org/api/satellites/?format=json&status=alive",
        timeout=30,
    )

    if not isinstance(raw, list):
        prev = _cache.get("satnogs", {}).get("data")
        return prev if prev else {"error": "SatNOGS data unavailable"}

    # Count by country
    by_country: Dict[str, int] = {}
    satellites: List[Dict[str, Any]] = []

    for sat in raw:
        if not isinstance(sat, dict):
            continue
        countries = sat.get("countries", "")
        for c in countries.split(","):
            c = c.strip()
            if c:
                by_country[c] = by_country.get(c, 0) + 1

    total = len(raw)

    # Return summary (full list is too large)
    # Sort countries by count
    top_countries = sorted(by_country.items(), key=lambda x: x[1], reverse=True)[:20]

    data: Dict[str, Any] = {
        "product": "SatNOGS Community Satellite Database",
        "source": "https://db.satnogs.org — Libre Space Foundation",
        "total_active_satellites": total,
        "top_countries": dict(top_countries),
        "note": (
            "SatNOGS tracks amateur and professional satellites via a global "
            "network of volunteer ground stations.  Useful for cross-referencing "
            "satellite activity status and detecting anomalies in satellite "
            "transmissions that may indicate interference or malfunction."
        ),
        "api_endpoints": {
            "satellites": "https://db.satnogs.org/api/satellites/?format=json",
            "transmitters": "https://db.satnogs.org/api/transmitters/?format=json",
            "telemetry": "https://db.satnogs.org/api/telemetry/?format=json",
        },
        "fetched_at": time.time(),
    }

    return _store("satnogs", data)


# =========================================================================
# 9. COMPOSITE — All Global Feeds in One Call
# =========================================================================

async def fetch_global_composite(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Master composite of all global feed data in a single call.

    Fetches ionosphere, DSCOVR, EONET, radiation belt, earthquakes,
    solar radio, and EPIC in parallel.
    """
    cached = _cached("global_all", _TTL_COMPOSITE)
    if cached is not None:
        return cached

    (
        ionosphere,
        dscovr,
        earth_events,
        radiation,
        earthquakes,
        solar_radio,
        epic,
    ) = await asyncio.gather(
        fetch_ionosphere_data(client),
        fetch_dscovr_data(client),
        fetch_earth_events(client),
        fetch_radiation_belts(client),
        fetch_earthquakes(client),
        fetch_solar_radio(client),
        fetch_epic_imagery(client),
    )

    data: Dict[str, Any] = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "Global Space Environment Composite Intelligence Feed",
        "ionosphere": ionosphere,
        "dscovr_solar_wind": dscovr,
        "earth_events": earth_events,
        "radiation_belts": radiation,
        "seismic": earthquakes,
        "solar_radio": solar_radio,
        "epic_imagery": epic,
        "source_catalog": {
            "noaa_swpc_glotec": {
                "url": f"{_SWPC}/products/glotec/geojson_2d_urt.json",
                "data": "Ionospheric TEC map — GPS/comms impact",
                "auth": "None",
                "format": "GeoJSON",
            },
            "noaa_swpc_rtsw": {
                "urls": [
                    f"{_SWPC}/json/rtsw/rtsw_mag_1m.json",
                    f"{_SWPC}/json/rtsw/rtsw_wind_1m.json",
                    f"{_SWPC}/json/rtsw/rtsw_ephemerides_1h.json",
                ],
                "data": "Real-time solar wind at L1 (DSCOVR/ACE)",
                "auth": "None",
                "format": "JSON",
            },
            "nasa_eonet": {
                "url": "https://eonet.gsfc.nasa.gov/api/v3/events",
                "data": "Natural events (fires, storms, volcanoes)",
                "auth": "None",
                "format": "JSON",
            },
            "noaa_goes_particles": {
                "urls": [
                    f"{_SWPC}/json/goes/primary/integral-electrons-1-day.json",
                    f"{_SWPC}/json/goes/primary/differential-electrons-1-day.json",
                    f"{_SWPC}/json/goes/primary/differential-protons-1-day.json",
                    f"{_SWPC}/json/goes/primary/differential-alphas-1-day.json",
                ],
                "data": "Van Allen radiation belt particle environment",
                "auth": "None",
                "format": "JSON",
            },
            "kyoto_dst": {
                "url": f"{_SWPC}/products/kyoto-dst.json",
                "data": "Dst magnetosphere ring current index",
                "auth": "None",
                "format": "JSON",
            },
            "noaa_solar_radio": {
                "url": f"{_SWPC}/json/solar-radio-flux.json",
                "data": "Multi-frequency solar radio flux (245-15400 MHz)",
                "auth": "None",
                "format": "JSON",
            },
            "nasa_epic": {
                "url": "https://epic.gsfc.nasa.gov/api/natural",
                "data": "DSCOVR EPIC full-disk Earth imagery from L1",
                "auth": "None",
                "format": "JSON",
            },
            "usgs_earthquake": {
                "url": "https://earthquake.usgs.gov/fdsnws/event/1/query",
                "data": "Global seismic events M4+",
                "auth": "None",
                "format": "GeoJSON",
            },
            "satnogs": {
                "url": "https://db.satnogs.org/api/satellites/?format=json",
                "data": "Community satellite database and telemetry",
                "auth": "None",
                "format": "JSON",
            },
            "future_integration": [
                "ESA DISCOS (space objects DB — requires free account)",
                "JAXA Space Tracking and Communications Center (public data)",
                "ISRO MOSDAC (Meteorological/Oceanographic satellite data)",
                "ITU BRIFIC (satellite frequency filings)",
                "CTBTO virtual Data Exploitation Centre (seismic/infrasound/radionuclide)",
                "OpenAIP (airspace data for launch corridor correlation)",
                "AIS/MarineTraffic (Yuan Wang tracking ship monitoring)",
                "AMSAT satellite status page (amateur radio satellite health)",
                "NASA JPL Horizons (solar system body ephemerides)",
                "CERN NMDB (neutron monitor — cosmic ray intensity)",
            ],
        },
        "fetched_at": time.time(),
    }

    return _store("global_all", data)
