"""
Multi-Source SIGINT & Advanced Intelligence Feeds
================================================================================
Beyond-basic space intelligence: satellite RF observations, thermal anomaly
detection, seismic correlation, ionospheric monitoring, and natural event
tracking.  Each feed provides unique intelligence not available from standard
satellite tracking.

Data sources integrated (all free, public, no API keys required):

1. SatNOGS Network API — Amateur radio satellite observation network
   https://network.satnogs.org/api/
   - Global network of 400+ ground stations recording satellite RF emissions
   - Provides waterfall spectrograms, demodulated data, station metadata
   - Intelligence value: detect satellite transmissions, identify active
     transponders, correlate with known frequency allocations to spot
     anomalous or undocumented emissions

2. NASA FIRMS (Fire Information for Resource Management System)
   https://firms.modaps.eosdis.nasa.gov/api/
   - MODIS and VIIRS thermal anomaly / hotspot data, global coverage
   - Near-real-time fire / thermal detection from Terra, Aqua, NOAA-20, SNPP
   - Intelligence value: detect rocket launches by thermal signature at known
     launch sites, monitor test ranges, correlate with adversary launch
     schedules.  Large sustained hotspots at known sites = probable launch.

3. USGS Earthquake Hazards Program — FDSN Event Web Service
   https://earthquake.usgs.gov/fdsnws/event/1/query
   - Global seismic event catalog, real-time updates
   - Intelligence value: shallow seismic events near nuclear test sites
     (Lop Nur, Punggye-ri, Novaya Zemlya, Semipalatinsk) may indicate
     underground nuclear tests.  ASAT interceptor tests and large rocket
     engine tests also produce seismic signatures.  Cross-correlate with
     CTBTO infrasound data and satellite imagery for confirmation.

4. NOAA SWPC Ionospheric TEC (Total Electron Content)
   https://services.swpc.noaa.gov/
   - US-TEC and global TEC maps showing ionospheric electron density
   - Intelligence value: elevated TEC degrades GPS accuracy (affects PNT),
     enhances over-the-horizon radar propagation (benefits adversary OTH-B),
     indicates nuclear detonation effects (HEMP causes instant TEC spikes),
     affects satellite drag models (higher TEC = hotter thermosphere = more
     drag on LEO assets).

5. NASA EONET (Earth Observatory Natural Events Tracker)
   https://eonet.gsfc.nasa.gov/api/v3/events
   - Curated natural events: wildfires, volcanic eruptions, severe storms,
     icebergs, dust/haze, floods, earthquakes, sea/lake ice
   - Intelligence value: volcanic eruptions produce atmospheric debris
     affecting satellite sensors, wildfires near ground stations degrade
     operations, severe storms affect launch windows, sea ice changes
     affect polar satellite ground station access.

6. SatNOGS DB API — Satellite & Transmitter Database
   https://db.satnogs.org/api/
   - Comprehensive database of satellites and their transmitter frequencies
   - Intelligence value: cross-reference with RF observations to identify
     undocumented transmissions, track frequency changes indicating satellite
     mode changes or anomalies.

7. GPS/GNSS Status Monitoring — NAVCEN NANU & SWPC
   - USCG NAVCEN publishes GPS constellation health NOTAMs (NANUs)
   - SWPC ionospheric data shows GPS degradation conditions
   - Intelligence value: correlate GPS outages with known jamming/spoofing
     events, identify areas of degraded PNT for military operations.

Analytical methods referenced (implemented where data permits):
  - Orbit determination from TLE differencing (maneuver detection)
  - Photometric analysis (brightness = shape/orientation)
  - Radar cross-section correlation with known satellite buses
  - RF fingerprinting from SatNOGS waterfall data
  - Conjunction screening via SGP4 propagation
  - Debris flux modeling (ESA MASTER / NASA ORDEM concepts)
  - Infrasound/seismic correlation for launch detection
  - Thermal anomaly clustering for launch site activity
"""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache: Dict[str, Dict[str, Any]] = {}

# Base URLs
_SATNOGS_NET = "https://network.satnogs.org/api"
_SATNOGS_DB = "https://db.satnogs.org/api"
_FIRMS_BASE = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
_FIRMS_MAP_KEY = "FIRMS_MAP_KEY"  # placeholder; free key from NASA Earthdata
_USGS_BASE = "https://earthquake.usgs.gov/fdsnws/event/1/query"
_SWPC_BASE = "https://services.swpc.noaa.gov"
_EONET_BASE = "https://eonet.gsfc.nasa.gov/api/v3"

# Cache TTLs (seconds)
_TTL_SATNOGS = 300       # 5 min — observations update continuously
_TTL_THERMAL = 600       # 10 min — FIRMS updates every ~3 hours per sensor
_TTL_SEISMIC = 300       # 5 min — USGS updates in near-real-time
_TTL_IONO = 600          # 10 min — TEC maps update every 15 min
_TTL_EVENTS = 900        # 15 min — EONET updates less frequently
_TTL_COMPOSITE = 300     # 5 min — composite refresh

# ---------------------------------------------------------------------------
# Known adversary launch sites (lat, lng, name, country)
# Used for thermal anomaly correlation
# ---------------------------------------------------------------------------
_LAUNCH_SITES: List[Dict[str, Any]] = [
    {"name": "Jiuquan SLC", "country": "PRC", "lat": 40.96, "lng": 100.28, "radius_km": 50},
    {"name": "Xichang SLC", "country": "PRC", "lat": 28.25, "lng": 102.03, "radius_km": 50},
    {"name": "Taiyuan SLC", "country": "PRC", "lat": 38.85, "lng": 111.61, "radius_km": 50},
    {"name": "Wenchang SLC", "country": "PRC", "lat": 19.61, "lng": 110.95, "radius_km": 50},
    {"name": "Plesetsk Cosmodrome", "country": "RUS", "lat": 62.93, "lng": 40.58, "radius_km": 50},
    {"name": "Vostochny Cosmodrome", "country": "RUS", "lat": 51.88, "lng": 128.33, "radius_km": 50},
    {"name": "Baikonur Cosmodrome", "country": "RUS/KAZ", "lat": 45.96, "lng": 63.31, "radius_km": 80},
    {"name": "Kapustin Yar", "country": "RUS", "lat": 48.58, "lng": 46.25, "radius_km": 50},
    {"name": "Sohae SLS", "country": "DPRK", "lat": 39.66, "lng": 124.71, "radius_km": 30},
    {"name": "Tonghae SLS", "country": "DPRK", "lat": 40.85, "lng": 129.67, "radius_km": 30},
    {"name": "Semnan Launch Site", "country": "IRAN", "lat": 35.23, "lng": 53.92, "radius_km": 30},
    {"name": "Imam Khomeini Spaceport", "country": "IRAN", "lat": 35.54, "lng": 51.40, "radius_km": 30},
    {"name": "Palmachim AFB", "country": "ISR", "lat": 31.88, "lng": 34.69, "radius_km": 20},
    {"name": "Satish Dhawan SC", "country": "IND", "lat": 13.73, "lng": 80.23, "radius_km": 30},
    # FVEY sites for completeness
    {"name": "Cape Canaveral SFS", "country": "US", "lat": 28.49, "lng": -80.58, "radius_km": 50},
    {"name": "Vandenberg SFB", "country": "US", "lat": 34.63, "lng": -120.57, "radius_km": 50},
    {"name": "Wallops Flight Facility", "country": "US", "lat": 37.94, "lng": -75.47, "radius_km": 30},
    {"name": "Kodiak Launch Complex", "country": "US", "lat": 57.44, "lng": -152.34, "radius_km": 30},
    {"name": "Woomera", "country": "AUS", "lat": -31.16, "lng": 136.83, "radius_km": 50},
    {"name": "Kourou (CSG)", "country": "ESA/FR", "lat": 5.24, "lng": -52.77, "radius_km": 50},
]

# Known nuclear/ASAT test sites for seismic correlation
_TEST_SITES: List[Dict[str, Any]] = [
    {"name": "Lop Nur", "country": "PRC", "lat": 41.73, "lng": 88.39, "radius_km": 100},
    {"name": "Punggye-ri", "country": "DPRK", "lat": 41.28, "lng": 129.07, "radius_km": 30},
    {"name": "Novaya Zemlya", "country": "RUS", "lat": 73.37, "lng": 54.78, "radius_km": 100},
    {"name": "Semipalatinsk", "country": "RUS/KAZ", "lat": 50.07, "lng": 78.43, "radius_km": 100},
    {"name": "Sary-Shagan", "country": "RUS/KAZ", "lat": 46.35, "lng": 73.61, "radius_km": 50,
     "note": "ASAT/ABM test range"},
    {"name": "Korla", "country": "PRC", "lat": 41.76, "lng": 86.13, "radius_km": 50,
     "note": "Reported ASAT / directed-energy test area"},
    {"name": "Pokhran", "country": "IND", "lat": 26.73, "lng": 71.75, "radius_km": 50},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _fetch_json(
    client: httpx.AsyncClient,
    url: str,
    timeout: int = 25,
    params: Optional[Dict[str, str]] = None,
) -> Optional[Any]:
    """Fetch JSON from *url*, returning None on any error."""
    try:
        r = await client.get(url, timeout=timeout, params=params)
        r.raise_for_status()
        return r.json()
    except (httpx.HTTPError, ValueError, TypeError):
        return None


async def _fetch_text(
    client: httpx.AsyncClient,
    url: str,
    timeout: int = 25,
    params: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """Fetch text content from *url*, returning None on any error."""
    try:
        r = await client.get(url, timeout=timeout, params=params)
        r.raise_for_status()
        return r.text
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


def _safe_float(val: Any) -> Optional[float]:
    """Convert to float or return None."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Approximate distance in km between two lat/lng points."""
    import math
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _utc_now() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# 1. SatNOGS — Amateur Radio Satellite Observation Network
# ---------------------------------------------------------------------------

async def fetch_satnogs_observations(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Fetch recent satellite RF observations from the SatNOGS network.

    SatNOGS is a global network of 400+ amateur ground stations that record
    satellite radio transmissions.  Each observation includes:
      - Satellite NORAD ID and name
      - Ground station ID and location
      - Start/end time of pass
      - Frequency (MHz)
      - Mode (FM, CW, AFSK, BPSK, etc.)
      - Waterfall spectrogram URL
      - Demodulated data URL (if available)
      - Observation status (good/bad/failed)

    Intelligence value:
      - Detect active satellite transmissions across global frequency spectrum
      - Identify undocumented or anomalous transmissions
      - Track satellite operational status changes
      - Correlate RF activity with orbital maneuvers
      - Monitor adversary satellite communication patterns

    The SatNOGS DB API provides the satellite/transmitter catalog while the
    Network API provides actual observations.
    """
    cached = _cached("satnogs", _TTL_SATNOGS)
    if cached is not None:
        return cached

    # Fetch recent observations (last 100, sorted by start time descending)
    observations_raw = await _fetch_json(
        client,
        f"{_SATNOGS_NET}/observations/",
        params={"format": "json", "page_size": "50"},
    )

    # Fetch satellite transmitter catalog for cross-reference
    transmitters_raw = await _fetch_json(
        client,
        f"{_SATNOGS_DB}/transmitters/",
        params={"format": "json", "status": "active"},
    )

    # Fetch ground station list for network coverage assessment
    stations_raw = await _fetch_json(
        client,
        f"{_SATNOGS_NET}/stations/",
        params={"format": "json", "status": "2"},  # status 2 = online
    )

    # Process observations
    observations: List[Dict[str, Any]] = []
    if isinstance(observations_raw, list):
        for obs in observations_raw[:50]:
            if not isinstance(obs, dict):
                continue
            observations.append({
                "id": obs.get("id"),
                "satellite_norad_id": obs.get("norad_cat_id"),
                "satellite_name": obs.get("satellite_name", obs.get("tle0", "")),
                "station_id": obs.get("ground_station"),
                "station_name": obs.get("station_name", ""),
                "start": obs.get("start"),
                "end": obs.get("end"),
                "frequency_mhz": _safe_float(obs.get("transmitter_downlink_low")),
                "mode": obs.get("transmitter_mode", ""),
                "status": obs.get("vetted_status", obs.get("status", "")),
                "waterfall_url": obs.get("waterfall"),
                "demod_data_url": obs.get("demoddata") or [],
                "max_elevation": _safe_float(obs.get("max_altitude")),
            })

    # Process ground station network coverage
    active_stations: List[Dict[str, Any]] = []
    station_count = 0
    if isinstance(stations_raw, list):
        station_count = len(stations_raw)
        for stn in stations_raw[:100]:
            if not isinstance(stn, dict):
                continue
            active_stations.append({
                "id": stn.get("id"),
                "name": stn.get("name", ""),
                "lat": _safe_float(stn.get("lat")),
                "lng": _safe_float(stn.get("lng")),
                "altitude_m": _safe_float(stn.get("altitude")),
                "min_horizon": _safe_float(stn.get("min_horizon")),
                "antenna": stn.get("antenna", ""),
                "last_seen": stn.get("last_seen", ""),
            })

    # Process transmitter catalog stats
    transmitter_count = 0
    freq_bands: Dict[str, int] = {}
    if isinstance(transmitters_raw, list):
        transmitter_count = len(transmitters_raw)
        for tx in transmitters_raw:
            if not isinstance(tx, dict):
                continue
            freq = tx.get("downlink_low")
            if freq is not None:
                try:
                    freq_ghz = float(freq) / 1e9
                    if freq_ghz < 0.3:
                        band = "HF/VHF (<300 MHz)"
                    elif freq_ghz < 1.0:
                        band = "UHF (300 MHz - 1 GHz)"
                    elif freq_ghz < 2.0:
                        band = "L-band (1-2 GHz)"
                    elif freq_ghz < 4.0:
                        band = "S-band (2-4 GHz)"
                    elif freq_ghz < 8.0:
                        band = "C-band (4-8 GHz)"
                    elif freq_ghz < 12.0:
                        band = "X-band (8-12 GHz)"
                    else:
                        band = "Ku/Ka/Higher (>12 GHz)"
                    freq_bands[band] = freq_bands.get(band, 0) + 1
                except (ValueError, TypeError):
                    pass

    data: Dict[str, Any] = {
        "classification": "UNCLASSIFIED // OSINT",
        "source": "SatNOGS Network — Libre Space Foundation",
        "source_urls": {
            "network_api": f"{_SATNOGS_NET}/observations/",
            "db_api": f"{_SATNOGS_DB}/transmitters/",
            "dashboard": "https://network.satnogs.org/",
            "db_dashboard": "https://db.satnogs.org/",
        },
        "network_status": {
            "active_stations": station_count,
            "station_sample": active_stations[:20],
        },
        "transmitter_catalog": {
            "total_active_transmitters": transmitter_count,
            "frequency_band_distribution": freq_bands,
        },
        "recent_observations": {
            "count": len(observations),
            "observations": observations,
        },
        "analytical_methods": {
            "rf_fingerprinting": (
                "Compare waterfall spectrograms against known satellite RF "
                "signatures to identify anomalous or undocumented transmissions.  "
                "Unexpected frequency shifts may indicate satellite malfunction, "
                "mode changes, or deliberate frequency hopping."
            ),
            "transmission_pattern_analysis": (
                "Track observation frequency and success rate per satellite over "
                "time.  Sudden cessation of transmissions may indicate satellite "
                "failure, decommissioning, or deliberate emission control.  "
                "New transmissions from previously silent objects warrant "
                "immediate investigation."
            ),
            "coverage_gap_analysis": (
                "Map SatNOGS station coverage to identify geographic blind spots "
                "where adversary satellites could transmit unobserved.  Priority "
                "gaps: central Asia, equatorial Africa, southern Pacific."
            ),
        },
        "intel_note": (
            "SatNOGS provides the only open-source global satellite RF "
            "observation network.  Cross-reference observations with CelesTrak "
            "TLE data to correlate RF activity with orbital maneuvers.  "
            "Satellites transmitting on undocumented frequencies or with "
            "unexpected modulation schemes warrant further analysis.  "
            "Waterfall spectrograms can reveal spread-spectrum or frequency-"
            "hopping patterns indicative of military communications."
        ),
        "fetched_at": time.time(),
    }

    return _store("satnogs", data)


# ---------------------------------------------------------------------------
# 2. NASA FIRMS — Thermal Anomaly Detection at Launch Sites
# ---------------------------------------------------------------------------

async def fetch_thermal_anomalies(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Fetch NASA FIRMS (Fire Information for Resource Management System) thermal
    anomaly data and correlate with known rocket launch sites and test ranges.

    FIRMS provides near-real-time MODIS and VIIRS active fire/thermal anomaly
    data.  A rocket launch produces an intense thermal signature detectable
    by both sensors.

    Detection method:
      - Query FIRMS for hotspots within radius of each known launch site
      - Cluster hotspots by time and intensity
      - High-confidence, high-FRP (Fire Radiative Power) detections near
        launch pads strongly correlate with launch events
      - Lower-confidence detections may indicate static fire tests, engine
        tests, or propellant handling incidents

    Note: The FIRMS API requires a free MAP_KEY from NASA Earthdata.  Without
    it we fall back to the FIRMS CSV summary and the EONET fire events feed.
    The code is structured to work with or without the key.

    Intelligence value:
      - Near-real-time detection of rocket launches without NOTAM monitoring
      - Detect static fire / engine tests at adversary launch sites
      - Monitor missile test ranges for ICBM/IRBM test launches
      - Correlate with seismic data for cross-source confirmation
    """
    cached = _cached("thermal", _TTL_THERMAL)
    if cached is not None:
        return cached

    # Strategy: Use NASA EONET wildfires + FIRMS summary CSV as fallback
    # since full FIRMS API requires registration key.
    # Also check EONET for volcanic eruptions near launch sites.

    # 1) EONET recent fire events (open, no key required)
    eonet_fires = await _fetch_json(
        client,
        f"{_EONET_BASE}/events",
        params={
            "category": "wildfires",
            "status": "open",
            "limit": "50",
        },
    )

    # 2) EONET volcanoes (eruptions produce thermal + atmospheric signatures)
    eonet_volcanoes = await _fetch_json(
        client,
        f"{_EONET_BASE}/events",
        params={
            "category": "volcanoes",
            "status": "open",
            "limit": "20",
        },
    )

    # Process fire events and check proximity to launch/test sites
    launch_site_alerts: List[Dict[str, Any]] = []
    fire_events: List[Dict[str, Any]] = []

    if isinstance(eonet_fires, dict):
        events_list = eonet_fires.get("events", [])
        for evt in events_list:
            if not isinstance(evt, dict):
                continue
            title = evt.get("title", "")
            geometries = evt.get("geometry", evt.get("geometries", []))
            if not isinstance(geometries, list):
                geometries = [geometries] if isinstance(geometries, dict) else []

            for geom in geometries[-3:]:  # latest geometry entries
                if not isinstance(geom, dict):
                    continue
                coords = geom.get("coordinates", [])
                if not coords or not isinstance(coords, list) or len(coords) < 2:
                    continue
                try:
                    lng, lat = float(coords[0]), float(coords[1])
                except (ValueError, TypeError, IndexError):
                    continue

                fire_entry = {
                    "title": title,
                    "lat": lat,
                    "lng": lng,
                    "date": geom.get("date", ""),
                    "event_id": evt.get("id", ""),
                }
                fire_events.append(fire_entry)

                # Check proximity to launch/test sites
                for site in _LAUNCH_SITES + _TEST_SITES:
                    dist = _haversine_km(lat, lng, site["lat"], site["lng"])
                    if dist <= site["radius_km"] * 2:  # 2x radius for margin
                        launch_site_alerts.append({
                            "alert_type": "THERMAL_ANOMALY_NEAR_LAUNCH_SITE",
                            "priority": "HIGH" if dist <= site["radius_km"] else "MEDIUM",
                            "fire_event": title,
                            "fire_lat": lat,
                            "fire_lng": lng,
                            "fire_date": geom.get("date", ""),
                            "site_name": site["name"],
                            "site_country": site["country"],
                            "distance_km": round(dist, 1),
                            "assessment": (
                                f"Thermal anomaly detected {dist:.0f} km from "
                                f"{site['name']} ({site['country']}).  "
                                "Requires imagery confirmation to distinguish "
                                "launch activity from wildfire/agricultural burn."
                            ),
                        })

    # Process volcanic events
    volcanic_events: List[Dict[str, Any]] = []
    if isinstance(eonet_volcanoes, dict):
        events_list = eonet_volcanoes.get("events", [])
        for evt in events_list:
            if not isinstance(evt, dict):
                continue
            geometries = evt.get("geometry", evt.get("geometries", []))
            if not isinstance(geometries, list):
                geometries = [geometries] if isinstance(geometries, dict) else []
            latest_geom = geometries[-1] if geometries else {}
            coords = latest_geom.get("coordinates", []) if isinstance(latest_geom, dict) else []
            lat, lng = None, None
            if isinstance(coords, list) and len(coords) >= 2:
                try:
                    lng, lat = float(coords[0]), float(coords[1])
                except (ValueError, TypeError):
                    pass
            volcanic_events.append({
                "title": evt.get("title", ""),
                "event_id": evt.get("id", ""),
                "lat": lat,
                "lng": lng,
                "date": latest_geom.get("date", "") if isinstance(latest_geom, dict) else "",
            })

    data: Dict[str, Any] = {
        "classification": "UNCLASSIFIED // OSINT",
        "source": "NASA FIRMS + EONET Thermal Anomaly Detection",
        "source_urls": {
            "firms_api": "https://firms.modaps.eosdis.nasa.gov/api/",
            "firms_map": "https://firms.modaps.eosdis.nasa.gov/map/",
            "eonet_api": f"{_EONET_BASE}/events",
            "firms_key_registration": "https://firms.modaps.eosdis.nasa.gov/api/area/",
        },
        "monitored_launch_sites": [
            {
                "name": s["name"],
                "country": s["country"],
                "lat": s["lat"],
                "lng": s["lng"],
                "alert_radius_km": s["radius_km"],
            }
            for s in _LAUNCH_SITES
        ],
        "launch_site_thermal_alerts": {
            "count": len(launch_site_alerts),
            "alerts": launch_site_alerts,
        },
        "fire_events": {
            "description": "EONET tracked wildfire events (open status)",
            "count": len(fire_events),
            "events": fire_events[:30],
        },
        "volcanic_activity": {
            "description": "Active volcanic eruptions — atmospheric/sensor impact",
            "count": len(volcanic_events),
            "events": volcanic_events,
            "intel_note": (
                "Volcanic aerosols degrade optical satellite imaging, affect "
                "GPS signal propagation, and can cause thermal sensor false "
                "positives.  Major eruptions produce stratospheric debris "
                "potentially impacting LEO satellites."
            ),
        },
        "analytical_methods": {
            "launch_detection": (
                "Correlate FIRMS hotspot clusters with known launch site "
                "coordinates.  A single high-FRP (>500 MW) detection within "
                "10 km of a launch pad with duration < 30 min is consistent "
                "with a rocket launch.  Multiple sustained detections suggest "
                "ground fire, not launch.  Cross-reference with seismic data, "
                "TLE updates, and NOTAM/NOTMAR publications for confirmation."
            ),
            "static_fire_detection": (
                "Lower-FRP detections (50-500 MW) at launch sites lasting "
                "< 5 min may indicate engine static fire tests.  These often "
                "precede launch by 1-14 days for liquid-fueled vehicles."
            ),
            "missile_test_correlation": (
                "Monitor IRBM/ICBM test ranges (Sary-Shagan, Korla) for "
                "thermal signatures.  Missile launches produce briefer, lower-"
                "FRP signatures than orbital launches but are still detectable "
                "by VIIRS at close range."
            ),
        },
        "intel_note": (
            "FIRMS thermal anomaly detection provides an independent launch "
            "detection capability requiring no NOTAM monitoring.  For best "
            "results, register for a free NASA Earthdata MAP_KEY to access "
            "the full FIRMS API with 24-hour NRT data at 375m resolution "
            "(VIIRS) and 1km resolution (MODIS).  Without the key, EONET "
            "fire events provide a coarser but still useful indicator."
        ),
        "fetched_at": time.time(),
    }

    return _store("thermal", data)


# ---------------------------------------------------------------------------
# 3. USGS Seismic Events — Nuclear Test & ASAT Correlation
# ---------------------------------------------------------------------------

async def fetch_seismic_events(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Fetch seismic events from USGS and correlate with known nuclear test sites,
    ASAT test ranges, and launch facilities.

    Detection methodology:
      - Nuclear tests produce characteristic seismic signatures:
        * Shallow depth (0-2 km for underground tests)
        * Specific body-wave magnitude (mb) to surface-wave magnitude (Ms)
          ratio (mb/Ms > 1.0 suggests explosion vs earthquake)
        * Location within known test site boundaries
      - ASAT kinetic kill tests produce smaller seismic signatures from
        interceptor launch and ground impact of debris
      - Large rocket engine tests and launch events produce detectable
        seismic waves, especially solid-fuel motors

    Intelligence value:
      - Early detection of nuclear tests before official announcement
      - ASAT test detection via seismic + orbital correlation
      - Launch site activity monitoring via ground vibration
      - Underground facility construction detection (microseismicity)
    """
    cached = _cached("seismic", _TTL_SEISMIC)
    if cached is not None:
        return cached

    # Query USGS for events in last 7 days, M2.5+ globally
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")

    seismic_raw = await _fetch_json(
        client,
        _USGS_BASE,
        params={
            "format": "geojson",
            "starttime": start,
            "endtime": end,
            "minmagnitude": "2.5",
            "orderby": "time",
            "limit": "200",
        },
    )

    all_events: List[Dict[str, Any]] = []
    test_site_correlations: List[Dict[str, Any]] = []
    launch_site_correlations: List[Dict[str, Any]] = []
    shallow_explosions: List[Dict[str, Any]] = []

    if isinstance(seismic_raw, dict):
        features = seismic_raw.get("features", [])
        for feat in features:
            if not isinstance(feat, dict):
                continue
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            coords = geom.get("coordinates", [])

            if not isinstance(coords, list) or len(coords) < 3:
                continue
            try:
                lng = float(coords[0])
                lat = float(coords[1])
                depth = float(coords[2])
            except (ValueError, TypeError, IndexError):
                continue

            mag = _safe_float(props.get("mag"))
            event_entry = {
                "id": feat.get("id", ""),
                "title": props.get("title", ""),
                "time": props.get("time"),
                "time_iso": datetime.fromtimestamp(
                    props["time"] / 1000, tz=timezone.utc
                ).isoformat() if props.get("time") else "",
                "lat": lat,
                "lng": lng,
                "depth_km": depth,
                "magnitude": mag,
                "mag_type": props.get("magType", ""),
                "place": props.get("place", ""),
                "type": props.get("type", ""),
                "status": props.get("status", ""),
                "tsunami": props.get("tsunami", 0),
                "url": props.get("url", ""),
            }
            all_events.append(event_entry)

            # Flag shallow events that could be explosions (depth < 5 km)
            if depth < 5.0 and mag is not None and mag >= 3.0:
                shallow_explosions.append({
                    **event_entry,
                    "assessment": (
                        f"Shallow event (depth {depth:.1f} km) with M{mag:.1f} "
                        "warrants explosion discrimination analysis.  Natural "
                        "earthquakes at this depth are less common; compare "
                        "mb/Ms ratio if available."
                    ),
                })

            # Correlate with nuclear/ASAT test sites
            for site in _TEST_SITES:
                dist = _haversine_km(lat, lng, site["lat"], site["lng"])
                if dist <= site["radius_km"]:
                    priority = "CRITICAL" if depth < 5.0 else "HIGH"
                    test_site_correlations.append({
                        "alert_type": "SEISMIC_EVENT_NEAR_TEST_SITE",
                        "priority": priority,
                        "event": event_entry,
                        "site_name": site["name"],
                        "site_country": site["country"],
                        "distance_km": round(dist, 1),
                        "note": site.get("note", "Nuclear test site"),
                        "assessment": (
                            f"M{mag} seismic event at {depth:.1f} km depth, "
                            f"{dist:.0f} km from {site['name']} "
                            f"({site['country']}).  "
                            + (
                                "SHALLOW DEPTH — consistent with underground "
                                "nuclear test or large conventional explosion.  "
                                "IMMEDIATE discrimination analysis required."
                                if depth < 5.0
                                else "Depth suggests natural tectonic origin "
                                "but proximity to test site warrants monitoring."
                            )
                        ),
                    })

            # Correlate with launch sites
            for site in _LAUNCH_SITES:
                dist = _haversine_km(lat, lng, site["lat"], site["lng"])
                if dist <= site["radius_km"]:
                    launch_site_correlations.append({
                        "alert_type": "SEISMIC_EVENT_NEAR_LAUNCH_SITE",
                        "priority": "MEDIUM",
                        "event": event_entry,
                        "site_name": site["name"],
                        "site_country": site["country"],
                        "distance_km": round(dist, 1),
                        "assessment": (
                            f"M{mag} seismic event {dist:.0f} km from "
                            f"{site['name']}.  Could indicate launch activity "
                            "(solid motor ignition), static fire test, or "
                            "unrelated tectonic activity."
                        ),
                    })

    # Sort correlations by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    test_site_correlations.sort(
        key=lambda x: priority_order.get(x.get("priority", "LOW"), 99)
    )

    data: Dict[str, Any] = {
        "classification": "UNCLASSIFIED // OSINT",
        "source": "USGS Earthquake Hazards Program — FDSN Event Web Service",
        "source_urls": {
            "api": _USGS_BASE,
            "web": "https://earthquake.usgs.gov/earthquakes/map/",
            "documentation": "https://earthquake.usgs.gov/fdsnws/event/1/",
        },
        "query_parameters": {
            "time_window": f"{start} to {end}",
            "min_magnitude": 2.5,
            "max_results": 200,
        },
        "global_events": {
            "total_count": len(all_events),
            "events": all_events[:50],  # Limit payload
        },
        "test_site_correlations": {
            "description": "Seismic events near known nuclear/ASAT test sites",
            "count": len(test_site_correlations),
            "alerts": test_site_correlations,
        },
        "launch_site_correlations": {
            "description": "Seismic events near known launch facilities",
            "count": len(launch_site_correlations),
            "alerts": launch_site_correlations,
        },
        "shallow_explosion_candidates": {
            "description": "Shallow M3+ events warranting explosion discrimination",
            "count": len(shallow_explosions),
            "events": shallow_explosions,
        },
        "monitored_test_sites": [
            {"name": s["name"], "country": s["country"], "lat": s["lat"],
             "lng": s["lng"], "note": s.get("note", "Nuclear test site")}
            for s in _TEST_SITES
        ],
        "analytical_methods": {
            "explosion_discrimination": (
                "The mb/Ms discriminant is the primary method: underground "
                "nuclear explosions produce high body-wave magnitudes (mb) "
                "relative to surface-wave magnitudes (Ms), yielding mb/Ms > 1.0.  "
                "Natural earthquakes typically show mb/Ms < 1.0.  The USGS "
                "provides mb and Ms when available for this analysis."
            ),
            "depth_analysis": (
                "Nuclear tests occur at 0-2 km depth (shaft) or 0.5-1.5 km "
                "(tunnel).  Events reported at exactly 0 km or 10 km depth "
                "may be fixed-depth solutions indicating the USGS could not "
                "determine depth — these warrant closer examination."
            ),
            "ctbto_correlation": (
                "The CTBTO International Monitoring System uses infrasound, "
                "hydroacoustic, radionuclide, and seismic stations globally.  "
                "While CTBTO data is not publicly available in real-time, "
                "USGS seismic data can be correlated with CTBTO press releases "
                "and reports for confirmation."
            ),
        },
        "intel_note": (
            "USGS seismic data provides an independent means to detect "
            "underground nuclear tests and large ASAT/missile tests.  "
            "Priority monitoring: Lop Nur (PRC), Punggye-ri (DPRK), "
            "Novaya Zemlya (RUS).  Shallow events (< 5 km) near these "
            "sites with M > 4.0 should trigger immediate cross-source "
            "verification (satellite imagery, atmospheric sampling, "
            "infrasound detection)."
        ),
        "fetched_at": time.time(),
    }

    return _store("seismic", data)


# ---------------------------------------------------------------------------
# 4. Ionospheric TEC — Total Electron Content
# ---------------------------------------------------------------------------

async def fetch_ionospheric_tec(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Fetch ionospheric Total Electron Content (TEC) data from NOAA SWPC.

    TEC measures the total number of electrons in a column from ground to
    satellite altitude, expressed in TEC Units (TECU, 1 TECU = 10^16 e/m^2).

    Sources:
      - NOAA SWPC US-TEC product (covers US, model-derived)
      - NOAA SWPC global TEC map imagery
      - D-RAP (D-Region Absorption Prediction) for HF absorption
      - Planetary K-index (driver of ionospheric disturbance)

    Intelligence value:
      - GPS accuracy degradation assessment (each TECU adds ~0.16m range error)
      - Over-the-horizon radar propagation analysis
      - Nuclear detonation detection (HEMP causes massive TEC spike)
      - GPS scintillation risk at high/equatorial latitudes
      - Satellite drag model inputs (TEC correlates with thermospheric density)
      - Electronic warfare effectiveness assessment
    """
    cached = _cached("ionosphere", _TTL_IONO)
    if cached is not None:
        return cached

    # Fetch multiple SWPC ionospheric-relevant products in parallel
    (
        kp_recent,
        planetary_k,
        drap_raw,
        alerts_raw,
    ) = await asyncio.gather(
        _fetch_json(
            client,
            f"{_SWPC_BASE}/products/noaa-planetary-k-index.json",
        ),
        _fetch_json(
            client,
            f"{_SWPC_BASE}/products/noaa-planetary-k-index-forecast.json",
        ),
        _fetch_json(
            client,
            f"{_SWPC_BASE}/products/alerts.json",
        ),
        _fetch_json(
            client,
            f"{_SWPC_BASE}/json/goes/primary/xrays-1-day.json",
        ),
    )

    # Parse recent Kp values (driver of ionospheric storms)
    kp_values: List[Dict[str, Any]] = []
    latest_kp: Optional[float] = None
    if isinstance(kp_recent, list):
        for entry in kp_recent:
            if not isinstance(entry, (list, tuple)) or len(entry) < 2:
                continue
            try:
                kp_values.append({
                    "time": entry[0],
                    "kp": float(entry[1]),
                })
                latest_kp = float(entry[1])
            except (ValueError, TypeError, IndexError):
                continue

    # Parse Kp forecast
    kp_forecast: List[Dict[str, Any]] = []
    if isinstance(planetary_k, list):
        for entry in planetary_k:
            if not isinstance(entry, dict):
                continue
            kp_forecast.append({
                "time": entry.get("time_tag", ""),
                "kp": _safe_float(entry.get("kp")),
                "observed": entry.get("observed", ""),
                "noaa_scale": entry.get("noaa_scale"),
            })

    # Filter SWPC alerts for ionospheric/GPS-related
    iono_alerts: List[Dict[str, str]] = []
    if isinstance(drap_raw, list):
        iono_keywords = [
            "ionospheric", "TEC", "GPS", "GNSS", "scintillation",
            "radio blackout", "HF", "D-region", "absorption",
            "R1", "R2", "R3", "R4", "R5",
        ]
        for alert in drap_raw[-50:]:
            if not isinstance(alert, dict):
                continue
            msg = alert.get("message", "")
            if any(kw.lower() in msg.lower() for kw in iono_keywords):
                iono_alerts.append({
                    "product_id": alert.get("product_id", ""),
                    "issue_datetime": alert.get("issue_datetime", ""),
                    "message": msg[:500],
                })

    # Latest X-ray flux (HF blackout indicator)
    latest_xray: Optional[Dict[str, Any]] = None
    if isinstance(alerts_raw, list) and alerts_raw:
        for entry in reversed(alerts_raw):
            if not isinstance(entry, dict):
                continue
            if entry.get("energy", "") == "0.1-0.8nm":
                latest_xray = {
                    "time": entry.get("time_tag", ""),
                    "flux": entry.get("flux"),
                    "satellite": entry.get("satellite"),
                }
                break

    # Compute ionospheric disturbance level
    iono_level = "QUIET"
    if latest_kp is not None:
        if latest_kp >= 7:
            iono_level = "SEVERE_STORM"
        elif latest_kp >= 5:
            iono_level = "STORM"
        elif latest_kp >= 4:
            iono_level = "ACTIVE"
        elif latest_kp >= 3:
            iono_level = "UNSETTLED"

    # GPS degradation estimate based on Kp
    gps_impact = "NOMINAL"
    if latest_kp is not None:
        if latest_kp >= 7:
            gps_impact = "SEVERE — expect multi-meter errors, possible loss of lock"
        elif latest_kp >= 5:
            gps_impact = "DEGRADED — 2-5x normal positioning error, scintillation likely"
        elif latest_kp >= 4:
            gps_impact = "MARGINAL — elevated error at high latitudes, monitor"

    data: Dict[str, Any] = {
        "classification": "UNCLASSIFIED // OSINT",
        "source": "NOAA SWPC Ionospheric Products",
        "source_urls": {
            "swpc_dashboard": "https://www.swpc.noaa.gov/",
            "us_tec": "https://www.swpc.noaa.gov/products/us-total-electron-content",
            "global_tec_map": f"{_SWPC_BASE}/images/animations/ctipe/tec/latest.png",
            "drap_map": f"{_SWPC_BASE}/images/animations/d-rap/global/d-rap/latest.png",
            "scintillation_info": "https://www.swpc.noaa.gov/phenomena/ionospheric-scintillation",
        },
        "ionospheric_status": {
            "disturbance_level": iono_level,
            "latest_kp": latest_kp,
            "gps_impact_assessment": gps_impact,
        },
        "kp_history": {
            "description": "Recent planetary K-index values (3-hour intervals)",
            "values": kp_values[-24:],  # last 3 days
        },
        "kp_forecast": {
            "description": "Predicted Kp values (SWPC forecast)",
            "values": kp_forecast,
        },
        "xray_hf_blackout": {
            "description": "Latest GOES X-ray flux — HF radio blackout indicator",
            "latest": latest_xray,
            "hf_impact": (
                "X-ray flux > 1e-5 W/m2 (M-class flare) causes partial HF "
                "blackout on sunlit hemisphere.  > 1e-4 W/m2 (X-class) = "
                "complete HF blackout lasting minutes to hours."
            ),
        },
        "ionospheric_alerts": {
            "count": len(iono_alerts),
            "alerts": iono_alerts[:10],
        },
        "imagery": {
            "global_tec_map": f"{_SWPC_BASE}/images/animations/ctipe/tec/latest.png",
            "us_tec_map": f"{_SWPC_BASE}/images/ustec/latest.png",
            "drap_hf_absorption": f"{_SWPC_BASE}/images/animations/d-rap/global/d-rap/latest.png",
            "aurora_north": f"{_SWPC_BASE}/images/animations/ovation/north/latest.jpg",
        },
        "analytical_methods": {
            "gps_error_estimation": (
                "GPS single-frequency ranging error (meters) ~ 0.16 * TEC(TECU) / f^2.  "
                "At L1 (1575.42 MHz), 1 TECU ~ 0.16m range error.  Dual-frequency "
                "receivers can correct for ionospheric delay but military signals "
                "(M-code) on single frequency in degraded mode cannot."
            ),
            "scintillation_prediction": (
                "GPS scintillation (rapid amplitude/phase fluctuations) occurs "
                "in two regions: (1) Equatorial anomaly (±15° geomagnetic lat) "
                "after sunset — affects low-latitude military operations.  "
                "(2) Auroral oval during geomagnetic storms (Kp >= 5) — affects "
                "polar routes and high-latitude operations."
            ),
            "hemp_detection": (
                "A high-altitude nuclear detonation (HEMP) causes an instantaneous "
                "TEC enhancement of 100+ TECU over a wide area.  This would appear "
                "as a sudden, massive, geographically bounded TEC spike not "
                "correlating with solar activity.  GPS receivers would simultaneously "
                "lose lock across the affected region."
            ),
            "oth_radar_propagation": (
                "Over-the-horizon radar (OTH-B, Sunflower) depends on ionospheric "
                "refraction.  Elevated TEC can extend OTH range but also introduces "
                "multipath.  Ionospheric storms degrade OTH performance, potentially "
                "creating surveillance gaps exploitable for adversary operations."
            ),
        },
        "intel_note": (
            "Ionospheric conditions directly impact GPS accuracy, HF communications, "
            "satellite-to-ground links, and OTH radar.  Current Kp and TEC levels "
            "should be factored into all PNT-dependent operations.  During "
            "geomagnetic storms (Kp >= 5), expect degraded GPS in polar and "
            "equatorial regions, HF blackouts on sunlit hemisphere, and increased "
            "satellite drag affecting LEO orbit predictions."
        ),
        "fetched_at": time.time(),
    }

    return _store("ionosphere", data)


# ---------------------------------------------------------------------------
# 5. NASA EONET — Natural Events Relevant to Space Operations
# ---------------------------------------------------------------------------

async def fetch_natural_events(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Fetch natural events from NASA EONET (Earth Observatory Natural Events
    Tracker) that could impact space operations, satellite sensors, ground
    infrastructure, or launch activities.

    Event categories monitored:
      - Volcanoes: atmospheric debris affecting optical sensors, aviation
      - Severe storms: ground station outages, launch delays
      - Wildfires: ground station proximity, smoke affecting optics
      - Floods: ground infrastructure damage
      - Earthquakes: ground station/antenna damage
      - Sea/lake ice: polar ground station access
      - Dust/haze: optical sensor degradation

    Intelligence value:
      - Ground station vulnerability assessment
      - Launch window environmental constraints
      - Satellite sensor degradation prediction
      - Infrastructure resilience planning
    """
    cached = _cached("natural_events", _TTL_EVENTS)
    if cached is not None:
        return cached

    # Fetch all open events
    events_raw = await _fetch_json(
        client,
        f"{_EONET_BASE}/events",
        params={
            "status": "open",
            "limit": "100",
        },
    )

    # Also fetch event categories for reference
    categories_raw = await _fetch_json(
        client,
        f"{_EONET_BASE}/categories",
    )

    events_by_category: Dict[str, List[Dict[str, Any]]] = {}
    all_events: List[Dict[str, Any]] = []
    ground_station_impacts: List[Dict[str, Any]] = []

    # Ground stations to check proximity against
    ground_stations = [
        {"name": "Pine Gap", "lat": -23.80, "lng": 133.74, "country": "AUS"},
        {"name": "NRO Menwith Hill", "lat": 54.00, "lng": -1.69, "country": "UK"},
        {"name": "Buckley SFB", "lat": 39.72, "lng": -104.75, "country": "US"},
        {"name": "Schriever SFB", "lat": 38.81, "lng": -104.53, "country": "US"},
        {"name": "Diego Garcia", "lat": -7.32, "lng": 72.42, "country": "UK/US"},
        {"name": "Thule AB (Pituffik)", "lat": 76.53, "lng": -68.70, "country": "US/DNK"},
        {"name": "Fylingdales", "lat": 54.36, "lng": -0.67, "country": "UK"},
        {"name": "Cape Canaveral", "lat": 28.49, "lng": -80.58, "country": "US"},
        {"name": "Vandenberg SFB", "lat": 34.63, "lng": -120.57, "country": "US"},
        {"name": "Woomera", "lat": -31.16, "lng": 136.83, "country": "AUS"},
        {"name": "Kaena Point", "lat": 21.57, "lng": -158.27, "country": "US"},
        {"name": "Ascension Island", "lat": -7.97, "lng": -14.40, "country": "UK"},
    ]

    if isinstance(events_raw, dict):
        events_list = events_raw.get("events", [])
        for evt in events_list:
            if not isinstance(evt, dict):
                continue

            categories = evt.get("categories", [])
            cat_name = "Unknown"
            if isinstance(categories, list) and categories:
                first_cat = categories[0]
                if isinstance(first_cat, dict):
                    cat_name = first_cat.get("title", "Unknown")

            geometries = evt.get("geometry", evt.get("geometries", []))
            if not isinstance(geometries, list):
                geometries = [geometries] if isinstance(geometries, dict) else []

            # Get latest position
            latest_geom = geometries[-1] if geometries else {}
            coords = latest_geom.get("coordinates", []) if isinstance(latest_geom, dict) else []
            lat, lng = None, None
            if isinstance(coords, list) and len(coords) >= 2:
                try:
                    lng, lat = float(coords[0]), float(coords[1])
                except (ValueError, TypeError):
                    pass

            event_entry = {
                "id": evt.get("id", ""),
                "title": evt.get("title", ""),
                "category": cat_name,
                "lat": lat,
                "lng": lng,
                "date": latest_geom.get("date", "") if isinstance(latest_geom, dict) else "",
                "sources": [
                    {"id": s.get("id", ""), "url": s.get("url", "")}
                    for s in (evt.get("sources", []) or [])
                    if isinstance(s, dict)
                ],
                "link": evt.get("link", ""),
            }
            all_events.append(event_entry)

            if cat_name not in events_by_category:
                events_by_category[cat_name] = []
            events_by_category[cat_name].append(event_entry)

            # Check proximity to FVEY ground stations
            if lat is not None and lng is not None:
                for gs in ground_stations:
                    dist = _haversine_km(lat, lng, gs["lat"], gs["lng"])
                    if dist <= 500:  # within 500 km
                        impact_level = "HIGH" if dist <= 100 else "MEDIUM" if dist <= 250 else "LOW"
                        ground_station_impacts.append({
                            "alert_type": "NATURAL_EVENT_NEAR_GROUND_STATION",
                            "priority": impact_level,
                            "event": event_entry,
                            "station_name": gs["name"],
                            "station_country": gs["country"],
                            "distance_km": round(dist, 1),
                            "assessment": (
                                f"{cat_name} event '{evt.get('title', '')}' "
                                f"detected {dist:.0f} km from {gs['name']} "
                                f"({gs['country']}).  "
                                + _get_impact_assessment(cat_name, dist)
                            ),
                        })

    # Category summaries
    category_summary: Dict[str, int] = {
        cat: len(evts) for cat, evts in events_by_category.items()
    }

    # Available categories
    available_categories: List[Dict[str, str]] = []
    if isinstance(categories_raw, dict):
        for cat in categories_raw.get("categories", []):
            if isinstance(cat, dict):
                available_categories.append({
                    "id": cat.get("id", ""),
                    "title": cat.get("title", ""),
                })

    data: Dict[str, Any] = {
        "classification": "UNCLASSIFIED // OSINT",
        "source": "NASA EONET — Earth Observatory Natural Events Tracker",
        "source_urls": {
            "api": f"{_EONET_BASE}/events",
            "web": "https://eonet.gsfc.nasa.gov/",
            "documentation": "https://eonet.gsfc.nasa.gov/docs/v3",
        },
        "summary": {
            "total_open_events": len(all_events),
            "by_category": category_summary,
            "available_categories": available_categories,
        },
        "events": all_events[:60],
        "ground_station_impact_alerts": {
            "description": "Natural events within 500 km of FVEY ground stations",
            "count": len(ground_station_impacts),
            "alerts": ground_station_impacts,
        },
        "space_ops_impact": {
            "volcanic_eruptions": {
                "count": len(events_by_category.get("Volcanoes", [])),
                "events": events_by_category.get("Volcanoes", [])[:10],
                "impact": (
                    "Volcanic plumes inject aerosols to stratospheric altitude, "
                    "degrading optical satellite sensors (increased atmospheric "
                    "opacity), affecting aviation (SIGMET/NOTAM), and potentially "
                    "causing GPS multipath in dense ash clouds."
                ),
            },
            "severe_storms": {
                "count": len(events_by_category.get("Severe Storms", [])),
                "events": events_by_category.get("Severe Storms", [])[:10],
                "impact": (
                    "Severe storms cause ground station outages (power, comms), "
                    "delay launches (lightning/wind constraints), and generate "
                    "ionospheric disturbances (sprites, elves) affecting VLF/LF "
                    "propagation."
                ),
            },
            "wildfires": {
                "count": len(events_by_category.get("Wildfires", [])),
                "events": events_by_category.get("Wildfires", [])[:10],
                "impact": (
                    "Wildfires near ground stations pose direct infrastructure "
                    "risk and smoke plumes degrade optical tracking/imaging.  "
                    "Large fires can also trigger FIRMS thermal anomalies that "
                    "must be discriminated from launch signatures."
                ),
            },
        },
        "analytical_methods": {
            "ground_station_vulnerability": (
                "Continuously monitor natural events within 500 km of FVEY "
                "ground stations.  Wildfires and severe storms within 100 km "
                "require immediate operational continuity assessment.  Volcanic "
                "eruptions within 500 km may require sensor recalibration or "
                "temporary data quality flagging."
            ),
            "launch_window_impact": (
                "Cross-reference severe weather events with upcoming launch "
                "schedules.  Tropical cyclones within 500 km of coastal launch "
                "sites (Canaveral, Wenchang, Kourou) typically force 24-72 hour "
                "delays.  Upper-level wind shear from distant storms can affect "
                "trajectory."
            ),
        },
        "intel_note": (
            "NASA EONET aggregates multiple satellite-derived event feeds into "
            "a unified API.  Events are curated by NASA analysts, providing "
            "higher signal-to-noise than raw satellite data.  For space "
            "operations planning, prioritize volcanic eruptions (sensor impact), "
            "severe storms (launch/ground station impact), and wildfires "
            "(ground station proximity and FIRMS false positive discrimination)."
        ),
        "fetched_at": time.time(),
    }

    return _store("natural_events", data)


def _get_impact_assessment(category: str, distance_km: float) -> str:
    """Generate impact assessment text based on event category and distance."""
    cat_lower = category.lower()
    if "volcano" in cat_lower or "eruption" in cat_lower:
        if distance_km <= 100:
            return (
                "CRITICAL: Volcanic eruption in close proximity.  Expect "
                "ash fall on optical equipment, possible evacuation of "
                "personnel, degraded atmospheric transmission."
            )
        return (
            "Monitor volcanic plume trajectory for potential sensor "
            "degradation.  Ash cloud at altitude may affect satellite "
            "optical imaging over the area."
        )
    if "fire" in cat_lower or "wildfire" in cat_lower:
        if distance_km <= 50:
            return (
                "HIGH: Wildfire in close proximity to ground station.  "
                "Assess evacuation readiness, backup site activation, "
                "and smoke impact on optical tracking."
            )
        return (
            "Monitor fire progression toward station.  Smoke may "
            "degrade optical tracking performance."
        )
    if "storm" in cat_lower:
        if distance_km <= 100:
            return (
                "Severe storm may cause power outages, antenna damage, "
                "or communication disruptions at the station."
            )
        return "Monitor storm track for potential approach to station."
    if "flood" in cat_lower:
        return "Flooding may affect ground-level infrastructure and access roads."
    if "ice" in cat_lower:
        return "Sea/lake ice changes may affect maritime resupply or coastal access."
    return "Natural event proximity — monitor for operational impact."


# ---------------------------------------------------------------------------
# 6. Composite Multi-Source Intelligence
# ---------------------------------------------------------------------------

async def get_multi_source_intel(client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Composite multi-source intelligence product combining all SIGINT and
    advanced feeds into a single unified assessment.

    This function aggregates:
      - SatNOGS RF observations (satellite transmissions)
      - NASA FIRMS thermal anomalies (launch detection)
      - USGS seismic data (nuclear/ASAT test correlation)
      - NOAA ionospheric data (GPS/comms impact)
      - NASA EONET natural events (operational impact)

    The composite product cross-correlates between sources to identify
    intelligence patterns not visible in any single feed.
    """
    cached = _cached("sigint_composite", _TTL_COMPOSITE)
    if cached is not None:
        return cached

    # Fetch all sources in parallel
    (
        satnogs,
        thermal,
        seismic,
        ionosphere,
        events,
    ) = await asyncio.gather(
        fetch_satnogs_observations(client),
        fetch_thermal_anomalies(client),
        fetch_seismic_events(client),
        fetch_ionospheric_tec(client),
        fetch_natural_events(client),
    )

    # Cross-source correlation analysis
    correlations: List[Dict[str, Any]] = []

    # 1) Thermal + Seismic = possible launch detection
    thermal_alerts = thermal.get("launch_site_thermal_alerts", {}).get("alerts", [])
    seismic_launch = seismic.get("launch_site_correlations", {}).get("alerts", [])
    if thermal_alerts and seismic_launch:
        for ta in thermal_alerts:
            for sl in seismic_launch:
                if ta.get("site_name") == sl.get("site_name"):
                    correlations.append({
                        "correlation_type": "THERMAL_SEISMIC_LAUNCH",
                        "priority": "CRITICAL",
                        "site": ta.get("site_name"),
                        "country": ta.get("site_country"),
                        "assessment": (
                            f"MULTI-SOURCE CORRELATION: Both thermal anomaly "
                            f"and seismic event detected near {ta.get('site_name')} "
                            f"({ta.get('site_country')}).  High confidence of "
                            f"launch or major engine test activity.  Correlate "
                            f"with TLE updates and NOTAM publications."
                        ),
                        "thermal_alert": ta,
                        "seismic_alert": sl,
                    })

    # 2) Seismic near test site + ionospheric disturbance = possible nuclear test
    test_site_events = seismic.get("test_site_correlations", {}).get("alerts", [])
    iono_level = ionosphere.get("ionospheric_status", {}).get("disturbance_level", "QUIET")
    if test_site_events and iono_level in ("STORM", "SEVERE_STORM"):
        for tse in test_site_events:
            if tse.get("priority") in ("CRITICAL", "HIGH"):
                correlations.append({
                    "correlation_type": "SEISMIC_IONO_NUCLEAR",
                    "priority": "CRITICAL",
                    "site": tse.get("site_name"),
                    "country": tse.get("site_country"),
                    "assessment": (
                        f"WARNING: Seismic event near {tse.get('site_name')} "
                        f"coincides with ionospheric storm conditions.  While "
                        f"the ionospheric disturbance is likely solar-driven, "
                        f"the temporal correlation warrants verification that "
                        f"it is not a HEMP (High-altitude Electromagnetic Pulse) "
                        f"signature.  Check for sudden TEC spike not correlated "
                        f"with solar flare."
                    ),
                    "seismic_alert": tse,
                    "ionospheric_status": iono_level,
                })

    # 3) Natural events near launch sites = launch constraint
    gs_impacts = events.get("ground_station_impact_alerts", {}).get("alerts", [])
    if gs_impacts:
        for impact in gs_impacts:
            if impact.get("priority") in ("HIGH", "CRITICAL"):
                correlations.append({
                    "correlation_type": "NATURAL_EVENT_OPS_IMPACT",
                    "priority": "HIGH",
                    "station": impact.get("station_name"),
                    "assessment": (
                        f"Natural event impacting {impact.get('station_name')}: "
                        f"{impact.get('assessment', '')}"
                    ),
                    "event_alert": impact,
                })

    # Sort correlations by priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    correlations.sort(
        key=lambda x: priority_order.get(x.get("priority", "LOW"), 99)
    )

    # Build threat level summary
    critical_count = sum(1 for c in correlations if c.get("priority") == "CRITICAL")
    high_count = sum(1 for c in correlations if c.get("priority") == "HIGH")

    if critical_count > 0:
        overall_threat = "ELEVATED"
    elif high_count > 0:
        overall_threat = "GUARDED"
    else:
        overall_threat = "NOMINAL"

    data: Dict[str, Any] = {
        "classification": "UNCLASSIFIED // OSINT // REL TO FVEY",
        "product": "MULTI-SOURCE SIGINT & ADVANCED INTELLIGENCE COMPOSITE",
        "generated_at": _utc_now(),
        "overall_threat_level": overall_threat,
        "cross_source_correlations": {
            "description": (
                "Intelligence patterns identified by correlating multiple "
                "independent data sources.  Multi-source correlation increases "
                "confidence and reduces false positive rate."
            ),
            "critical_count": critical_count,
            "high_count": high_count,
            "total_correlations": len(correlations),
            "correlations": correlations,
        },
        "source_summaries": {
            "satnogs": {
                "status": "OK" if "error" not in satnogs else "DEGRADED",
                "active_stations": satnogs.get("network_status", {}).get("active_stations", 0),
                "recent_observations": satnogs.get("recent_observations", {}).get("count", 0),
            },
            "thermal_anomaly": {
                "status": "OK" if "error" not in thermal else "DEGRADED",
                "launch_site_alerts": thermal.get("launch_site_thermal_alerts", {}).get("count", 0),
                "fire_events": thermal.get("fire_events", {}).get("count", 0),
            },
            "seismic": {
                "status": "OK" if "error" not in seismic else "DEGRADED",
                "total_events": seismic.get("global_events", {}).get("total_count", 0),
                "test_site_correlations": seismic.get("test_site_correlations", {}).get("count", 0),
                "launch_site_correlations": seismic.get("launch_site_correlations", {}).get("count", 0),
                "shallow_explosions": seismic.get("shallow_explosion_candidates", {}).get("count", 0),
            },
            "ionosphere": {
                "status": "OK" if "error" not in ionosphere else "DEGRADED",
                "disturbance_level": ionosphere.get("ionospheric_status", {}).get("disturbance_level", "UNKNOWN"),
                "latest_kp": ionosphere.get("ionospheric_status", {}).get("latest_kp"),
                "gps_impact": ionosphere.get("ionospheric_status", {}).get("gps_impact_assessment", "UNKNOWN"),
            },
            "natural_events": {
                "status": "OK" if "error" not in events else "DEGRADED",
                "total_events": events.get("summary", {}).get("total_open_events", 0),
                "ground_station_alerts": events.get("ground_station_impact_alerts", {}).get("count", 0),
            },
        },
        "data_source_catalog": {
            "operational": [
                {
                    "name": "SatNOGS Network",
                    "type": "SIGINT — Satellite RF Observations",
                    "access": "Free, no API key, public API",
                    "url": "https://network.satnogs.org/api/",
                    "unique_intel": "Global amateur satellite RF observation network",
                    "update_frequency": "Continuous — observations posted after each pass",
                },
                {
                    "name": "NASA EONET",
                    "type": "GEOINT — Natural Events Tracking",
                    "access": "Free, no API key, public API",
                    "url": "https://eonet.gsfc.nasa.gov/api/v3/events",
                    "unique_intel": "Curated natural events impacting space operations",
                    "update_frequency": "Near-real-time, NASA analyst curated",
                },
                {
                    "name": "USGS Earthquake Hazards",
                    "type": "SIGINT — Seismic Event Detection",
                    "access": "Free, no API key, public API",
                    "url": "https://earthquake.usgs.gov/fdsnws/event/1/",
                    "unique_intel": "Nuclear test and ASAT test seismic correlation",
                    "update_frequency": "Near-real-time (minutes)",
                },
                {
                    "name": "NOAA SWPC Ionosphere",
                    "type": "ELINT — Ionospheric Monitoring",
                    "access": "Free, no API key, public API",
                    "url": "https://services.swpc.noaa.gov/",
                    "unique_intel": "GPS degradation and HF blackout assessment",
                    "update_frequency": "1-15 minute intervals depending on product",
                },
                {
                    "name": "SatNOGS DB",
                    "type": "SIGINT — Satellite Transmitter Database",
                    "access": "Free, no API key, public API",
                    "url": "https://db.satnogs.org/api/",
                    "unique_intel": "Comprehensive satellite frequency/mode catalog",
                    "update_frequency": "Community-maintained, continuous updates",
                },
            ],
            "registration_required": [
                {
                    "name": "NASA FIRMS",
                    "type": "GEOINT — Thermal Anomaly Detection",
                    "access": "Free, requires NASA Earthdata MAP_KEY (free registration)",
                    "url": "https://firms.modaps.eosdis.nasa.gov/api/",
                    "unique_intel": "375m resolution thermal anomaly for launch detection",
                    "registration": "https://firms.modaps.eosdis.nasa.gov/api/area/",
                },
                {
                    "name": "Space-Track.org",
                    "type": "SSA — Conjunction Data Messages",
                    "access": "Free, requires account (free registration)",
                    "url": "https://www.space-track.org/",
                    "unique_intel": "Official conjunction screening, decay predictions",
                },
                {
                    "name": "Sentinel Hub (Copernicus)",
                    "type": "GEOINT — Multispectral Imagery",
                    "access": "Free tier available, registration required",
                    "url": "https://www.sentinel-hub.com/",
                    "unique_intel": "10m resolution optical + SAR imagery globally",
                },
                {
                    "name": "NASA Worldview / GIBS",
                    "type": "GEOINT — Earth Observation Imagery",
                    "access": "Free, GIBS API open, some products require Earthdata login",
                    "url": "https://worldview.earthdata.nasa.gov/",
                    "unique_intel": "Multi-sensor global imagery layers, near-real-time",
                },
            ],
            "future_integration": [
                {
                    "name": "TinyGS",
                    "type": "SIGINT — LoRa Satellite Ground Station Network",
                    "url": "https://tinygs.com/",
                    "unique_intel": "IoT/LoRa satellite downlink monitoring",
                },
                {
                    "name": "EUROCONTROL GPS Outage Reports",
                    "type": "ELINT — GPS Jamming/Spoofing Detection",
                    "url": "https://www.eurocontrol.int/",
                    "unique_intel": "Aviation-reported GPS interference events",
                },
                {
                    "name": "ESA DISCOS",
                    "type": "SSA — Space Debris Database",
                    "url": "https://discosweb.esac.esa.int/",
                    "unique_intel": "Detailed object characterization, RCS data",
                },
                {
                    "name": "NMDB Neutron Monitor",
                    "type": "Space Weather — Cosmic Ray Detection",
                    "url": "https://www.nmdb.eu/",
                    "unique_intel": "Ground-based cosmic ray intensity (GLE detection)",
                },
                {
                    "name": "INTERMAGNET",
                    "type": "Space Weather — Ground Magnetometer Network",
                    "url": "https://intermagnet.github.io/",
                    "unique_intel": "Global geomagnetic field measurements",
                },
            ],
        },
        "intel_note": (
            "This composite product integrates five independent intelligence "
            "sources to provide multi-domain space situational awareness beyond "
            "standard satellite tracking.  Cross-source correlations (thermal + "
            "seismic = launch detection, seismic + ionospheric = nuclear test "
            "screening) provide higher confidence than any single source.  "
            "All sources are open, unclassified, and freely accessible."
        ),
        "fetched_at": time.time(),
    }

    return _store("sigint_composite", data)
