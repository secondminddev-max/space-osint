"""
Adversary & FVEY satellite catalog — CelesTrak GP filtering + classification
Filters the active satellite catalog by nation using NAME-BASED identification
(CelesTrak GP JSON does not include COUNTRY_CODE).
All classification based on open-source name-pattern analysis (NASIC, SWF reports).
"""
from __future__ import annotations

import time
import re
import math
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx

from data_sources.celestrak import propagate_satellite, fetch_catalog
from config import CACHE_TTL_TLE_CATALOG, CACHE_TTL_SATELLITES

# ---------------------------------------------------------------------------
# Name-based COUNTRY IDENTIFICATION
# Since CelesTrak GP JSON lacks COUNTRY_CODE, we identify by OBJECT_NAME
# ---------------------------------------------------------------------------

_PRC_NAMES = re.compile(
    r"YAOGAN|JILIN|GAOFEN|GF-\d|SHIYAN|SY-\d|CHUANGXIN|CX-\d|"
    r"HUANJING|HJ-\d|ZIYUAN|ZY-\d|SUPERVIEW|BEIJING-\d|LUOJIA|"
    r"TIANHUI|TH-\d|HEAD-?\d|CARBONSAT|PIESAT|"
    r"BEIDOU|BD-|BDS-|"
    r"ZHONGXING|ZX-\d|FENGHUO|SHENTONG|TIANTONG|APSTAR|CHINASAT|"
    r"SINOSAT|CENTISPACE|YINHE|HONGYUN|XINGYUN|"
    r"SHIJIAN|SJ-\d|BANXING|AOLONG|TJS-|"
    r"SHENZHOU|TIANHE|WENTIAN|MENGTIAN|TIANZHOU|TIANGONG|CSS\b|"
    r"CHANG.?E|TIANWEN|QUEQIAO|DAMPE|QUESS|MICIUS|WUKONG|"
    r"TAIJI|FENGYUN|FY-\d|HAIYANG|HY-\d|TANSAT|CFOSAT|CSES|"
    r"EINSTEIN PROBE|EP-WXT|TONGXIN JISHU|TJSW|"
    r"CZ-\d|LONG MARCH|KUAIZHOU|LIJIAN|CERES-|GEELY|GALAXY.SPACE|"
    r"LINGQUE|ZHUHAI|JIUTIAN|TIANMU|HEAD.AEROSPACE|"
    r"ZHONGKE|STECCO|RSW-|DSS-|NUSAT.*PRC|SPACETY",
    re.IGNORECASE,
)

_RUS_NAMES = re.compile(
    r"COSMOS|GLONASS|URAGAN|"
    r"BLAGOVEST|MERIDIAN|GONETS|RODNIK|LUCH|YAMAL|EXPRESS|"
    r"GAZPROM|SERAFIM|SKIF|MARATHON|SFERA|"
    r"KONDOR|LIANA|LOTOS|PION|RESURS|KANOPUS|EMKA|NEITRON|RAZDAN|"
    r"TUNDRA|EKS|KUPOL|"
    r"SOYUZ|PROGRESS|NAUKA|PRICHAL|ZARYA|ZVEZDA|POISK|"
    r"SPEKTR|RADIOASTRON|METEOR|ELEKTRO|ARKTIKA|"
    r"NIVELIR|BUREVESTNIK|PERESVET|"
    r"FREGAT|BREEZE|BRIZ|ROKOT|ANGARA|PROTON|VOLGA|"
    r"GONETS-M|STRELA|MOLNIYA|GARPUN|REPEI",
    re.IGNORECASE,
)

_DPRK_NAMES = re.compile(r"KWANGMYONGSONG|KMS-|MALLIGYONG", re.IGNORECASE)

_IRAN_NAMES = re.compile(
    r"NOOR|KHAYYAM|NAHID|ZAFAR|PARS|KOWSAR|MESBAH|SINA-|RASAD|FAJR|NAVID",
    re.IGNORECASE,
)

# FVEY name patterns
_US_NAMES = re.compile(
    r"GPS|NAVSTAR|SBIRS|STSS|DSP|WGS|AEHF|MUOS|MILSTAR|GSSAP|"
    r"USA[ -]\d|NROL|MENTOR|ORION|TRUMPET|ONYX|LACROSSE|"
    r"WORLDVIEW|GEOEYE|PLEIADES|SKYSAT|"
    r"STARLINK|ONEWEB|KUIPER|IRIDIUM|GLOBALSTAR|ORBCOMM|"
    r"NOAA[ -]\d|GOES[ -]\d|JPSS|LANDSAT|TERRA\b|AQUA\b|AURA\b|"
    r"SUOMI|CALIPSO|CLOUDSAT|HUBBLE|JWST|CHANDRA|SWIFT|FERMI|"
    r"TDRS|FALCON|DRAGON|CYGNUS|STARLINER|"
    r"SES[ -]\d|INTELSAT|TELESAT|VIASAT|ECHOSTAR|"
    r"SPACEX|BOEING|NORTHROP|LOCKHEED|BALL.AERO|"
    r"RADARSAT|NILESAT",
    re.IGNORECASE,
)

_UK_NAMES = re.compile(r"SKYNET|CARBONITE|SSTL|SURREY|ONESAT.*UK|INMARSAT", re.IGNORECASE)
_AU_NAMES = re.compile(r"OPTUS|NBNCO|M2[ABC]|BIARRI", re.IGNORECASE)
_CA_NAMES = re.compile(r"RADARSAT|SAPPHIRE|TELESAT|CASSIOPE|SCISAT|NEOSSAT", re.IGNORECASE)
_NZ_NAMES = re.compile(r"ELECTRON.*NZ|ROCKETLAB", re.IGNORECASE)


def identify_country(name: str) -> Optional[str]:
    """Identify the operating country of a satellite from its name."""
    if _PRC_NAMES.search(name):
        return "PRC"
    if _RUS_NAMES.search(name):
        return "CIS"
    if _DPRK_NAMES.search(name):
        return "NKOR"
    if _IRAN_NAMES.search(name):
        return "IRAN"
    return None


def identify_fvey_country(name: str) -> Optional[str]:
    """Identify FVEY nation from satellite name."""
    if _UK_NAMES.search(name):
        return "UK"
    if _CA_NAMES.search(name):
        return "CA"
    if _AU_NAMES.search(name):
        return "AU"
    if _NZ_NAMES.search(name):
        return "NZ"
    if _US_NAMES.search(name):
        return "US"
    return None


# ---------------------------------------------------------------------------
# Mission classification (same as before — uses country + name patterns)
# ---------------------------------------------------------------------------

_PRC_ISR = re.compile(
    r"YAOGAN|JILIN|GAOFEN|GF-|SHIYAN|SY-|CHUANGXIN|CX-|"
    r"HUANJING|HJ-|ZIYUAN|ZY-|SUPERVIEW|BEIJING-|"
    r"LUOJIA|TIANHUI|TH-|HEAD|CARBONSAT|PIESAT|"
    r"LINGQUE|ZHUHAI|JIUTIAN|TIANMU",
    re.IGNORECASE,
)
_PRC_NAV = re.compile(r"BEIDOU|BD-|BDS-", re.IGNORECASE)
_PRC_COMMS = re.compile(
    r"ZHONGXING|ZX-|FENGHUO|SHENTONG|TIANTONG|APSTAR|CHINASAT|"
    r"SINOSAT|CENTISPACE|YINHE|HONGYUN|XINGYUN",
    re.IGNORECASE,
)
_PRC_EW = re.compile(r"TONGXIN JISHU|TJSW", re.IGNORECASE)
_PRC_SDA = re.compile(r"SHIJIAN|SJ-|BANXING|AOLONG|TJS-", re.IGNORECASE)
_PRC_HUMAN = re.compile(r"SHENZHOU|TIANHE|WENTIAN|MENGTIAN|TIANZHOU|TIANGONG|CSS\b", re.IGNORECASE)
_PRC_SCI = re.compile(
    r"CHANG.?E|TIANWEN|QUEQIAO|DAMPE|QUESS|MICIUS|WUKONG|"
    r"TAIJI|FENGYUN|FY-|HAIYANG|HY-|TANSAT|CFOSAT|CSES|EINSTEIN",
    re.IGNORECASE,
)

_RUS_ISR = re.compile(r"KONDOR|LIANA|LOTOS|PION|RESURS|KANOPUS|EMKA|NEITRON|RAZDAN|BARS|PERSONA", re.IGNORECASE)
_RUS_NAV = re.compile(r"GLONASS|URAGAN", re.IGNORECASE)
_RUS_COMMS = re.compile(r"BLAGOVEST|MERIDIAN|GONETS|RODNIK|LUCH|YAMAL|EXPRESS|GAZPROM|SERAFIM|MOLNIYA|GARPUN", re.IGNORECASE)
_RUS_EW = re.compile(r"TUNDRA|EKS|KUPOL", re.IGNORECASE)
_RUS_SDA = re.compile(r"NIVELIR|BUREVESTNIK|COSMOS.*254[0-3]|COSMOS.*2558|COSMOS.*2519", re.IGNORECASE)
_RUS_HUMAN = re.compile(r"SOYUZ|PROGRESS|NAUKA|PRICHAL|ZARYA|ZVEZDA|POISK", re.IGNORECASE)
_RUS_SCI = re.compile(r"SPEKTR|RADIOASTRON|METEOR|ELEKTRO|ARKTIKA", re.IGNORECASE)


def classify_satellite(name: str, country: str) -> str:
    """Classify satellite mission category."""
    n = name.upper()
    if country == "PRC":
        if _PRC_HUMAN.search(n): return "human_spaceflight"
        if _PRC_ISR.search(n): return "military_isr"
        if _PRC_NAV.search(n): return "navigation"
        if _PRC_EW.search(n): return "early_warning"
        if _PRC_SDA.search(n): return "sda_asat"
        if _PRC_COMMS.search(n): return "comms"
        if _PRC_SCI.search(n): return "civil_scientific"
        return "unknown"
    if country == "CIS":
        if _RUS_HUMAN.search(n): return "human_spaceflight"
        if _RUS_ISR.search(n): return "military_isr"
        if _RUS_NAV.search(n): return "navigation"
        if _RUS_EW.search(n): return "early_warning"
        if _RUS_SDA.search(n): return "sda_asat"
        if _RUS_COMMS.search(n): return "comms"
        if _RUS_SCI.search(n): return "civil_scientific"
        if "COSMOS" in n: return "military_isr"
        return "unknown"
    if country in ("NKOR", "PRK"):
        return "military_isr"
    if country in ("IRAN", "IR"):
        if "NOOR" in n: return "military_isr"
        return "civil_scientific"
    return "unknown"


def classify_fvey_satellite(name: str) -> str:
    """Classify FVEY satellite mission."""
    n = name.upper()
    if any(p in n for p in ("GPS", "NAVSTAR")): return "navigation"
    if any(p in n for p in ("SBIRS", "STSS", "DSP")): return "early_warning"
    if any(p in n for p in ("WGS", "AEHF", "MUOS", "MILSTAR", "SKYNET", "INMARSAT")): return "comms"
    if any(p in n for p in ("NROL", "USA ", "MENTOR", "ORION", "TRUMPET", "WORLDVIEW", "GEOEYE")): return "military_isr"
    if any(p in n for p in ("GSSAP", "ORS", "SAPPHIRE", "SBSS", "NEOSSAT")): return "sda_asat"
    if any(p in n for p in ("STARLINK", "ONEWEB", "KUIPER", "IRIDIUM", "GLOBALSTAR", "SES", "INTELSAT", "TELESAT")): return "comms"
    if any(p in n for p in ("NOAA", "GOES", "JPSS", "LANDSAT", "TERRA", "AQUA", "HUBBLE", "JWST")): return "civil_scientific"
    return "unknown"


# ---------------------------------------------------------------------------
# Orbital regime
# ---------------------------------------------------------------------------

def _orbital_regime(period_min: float, alt_km: float) -> str:
    if alt_km < 0: return "unknown"
    if alt_km < 2000: return "LEO"
    if alt_km < 35000: return "MEO"
    if alt_km < 36500: return "GEO"
    return "HEO"


def _alt_from_period(period_min: float) -> float:
    """Estimate altitude from orbital period."""
    if period_min <= 0:
        return 0
    mu = 398600.4418
    T_sec = period_min * 60.0
    a = (mu * (T_sec / (2 * math.pi)) ** 2) ** (1.0 / 3.0)
    return a - 6371.0


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

_cache: Dict[str, dict] = {}

# Longer cache for adversary sats since it involves propagating 500+ objects
_ADV_CACHE_TTL = 120  # 2 minutes


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def _enrich(gp: dict, country: str, is_fvey: bool = False) -> Optional[dict]:
    """Propagate and classify a single satellite."""
    pos = propagate_satellite(gp)
    name = gp.get("OBJECT_NAME", "UNKNOWN")
    category = classify_fvey_satellite(name) if is_fvey else classify_satellite(name, country)

    period = pos["period_min"] if pos else 0
    alt = pos["alt_km"] if pos else _alt_from_period(1440.0 / float(gp.get("MEAN_MOTION", 1)))

    return {
        "norad_id": int(gp.get("NORAD_CAT_ID", 0)),
        "name": name,
        "country": country,
        "category": category,
        "lat": pos["lat"] if pos else 0,
        "lng": pos["lng"] if pos else 0,
        "alt_km": round(alt, 1),
        "inclination": round(float(gp.get("INCLINATION", 0)), 2),
        "period_min": round(period, 1),
        "regime": _orbital_regime(period, alt),
        "epoch": gp.get("EPOCH", ""),
    }


async def get_adversary_satellites(client: httpx.AsyncClient, country: str) -> List[dict]:
    """Get all satellites for a given adversary nation (PRC, CIS, NKOR, IRAN)."""
    cache_key = f"adv_{country}"
    now = time.time()
    cached = _cache.get(cache_key)
    if cached and (now - cached["ts"]) < _ADV_CACHE_TTL:
        return cached["data"]

    catalog = await fetch_catalog(client, "active")
    results = []

    # Map country arg to what identify_country returns
    target = country.upper()
    # Handle aliases
    alias_map = {"RUSSIA": "CIS", "DPRK": "NKOR", "NORTHKOREA": "NKOR"}
    target = alias_map.get(target, target)

    for gp in catalog:
        name = gp.get("OBJECT_NAME", "")
        detected = identify_country(name)
        if detected == target:
            enriched = _enrich(gp, target)
            if enriched:
                results.append(enriched)

    results.sort(key=lambda s: (s["category"], s["name"]))
    _cache[cache_key] = {"data": results, "ts": now}
    return results


async def get_fvey_satellites(client: httpx.AsyncClient, country: str = "US") -> List[dict]:
    """Get satellites for a FVEY nation."""
    cache_key = f"fvey_{country}"
    now = time.time()
    cached = _cache.get(cache_key)
    if cached and (now - cached["ts"]) < _ADV_CACHE_TTL:
        return cached["data"]

    catalog = await fetch_catalog(client, "active")
    results = []
    target = country.upper()

    for gp in catalog:
        name = gp.get("OBJECT_NAME", "")
        detected = identify_fvey_country(name)
        if detected == target:
            enriched = _enrich(gp, target, is_fvey=True)
            if enriched:
                results.append(enriched)

    results.sort(key=lambda s: (s["category"], s["name"]))
    _cache[cache_key] = {"data": results, "ts": now}
    return results


async def get_adversary_stats(client: httpx.AsyncClient) -> dict:
    """Aggregate statistics across all adversary + FVEY."""
    cache_key = "adv_stats_all"
    now = time.time()
    cached = _cache.get(cache_key)
    if cached and (now - cached["ts"]) < _ADV_CACHE_TTL:
        return cached["data"]

    catalog = await fetch_catalog(client, "active")

    adv_stats = {}
    for country_key in ["PRC", "CIS", "NKOR", "IRAN"]:
        adv_stats[country_key] = {"total": 0, "by_category": {}, "by_regime": {}}

    fvey_total = 0

    for gp in catalog:
        name = gp.get("OBJECT_NAME", "")
        country = identify_country(name)

        if country and country in adv_stats:
            cat = classify_satellite(name, country)
            mm = float(gp.get("MEAN_MOTION", 0))
            period = (1440.0 / mm) if mm > 0 else 0
            alt = _alt_from_period(period)
            regime = _orbital_regime(period, alt)

            adv_stats[country]["total"] += 1
            adv_stats[country]["by_category"][cat] = adv_stats[country]["by_category"].get(cat, 0) + 1
            adv_stats[country]["by_regime"][regime] = adv_stats[country]["by_regime"].get(regime, 0) + 1
        elif identify_fvey_country(name):
            fvey_total += 1

    # Add convenient top-level counts
    for k, v in adv_stats.items():
        v["military_isr"] = v["by_category"].get("military_isr", 0)
        v["navigation"] = v["by_category"].get("navigation", 0)

    data = {
        **adv_stats,
        "fvey_total": fvey_total,
        "catalog_size": len(catalog),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }

    _cache[cache_key] = {"data": data, "ts": now}
    return data
