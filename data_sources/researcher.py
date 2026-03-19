"""
Active Intelligence Research Agent
Aggregates space intelligence from multiple open sources:
- Spaceflight News API v4 (articles, blogs, reports)
- ArXiv academic papers (space security, warfare, counterspace)
- NOAA SWPC alerts (deep parsing)
- US Federal Register space policy documents

Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

import time
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache: Dict[str, dict] = {}
_CACHE_TTL = 600  # 10 minutes


def _cached(key: str) -> Optional[list]:
    cached = _cache.get(key)
    if cached and (time.time() - cached["ts"]) < _CACHE_TTL:
        return cached["data"]
    return None


def _store(key: str, data: list) -> list:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# ---------------------------------------------------------------------------
# Relevance tagging
# ---------------------------------------------------------------------------

_TAG_PATTERNS: List[tuple] = [
    ("ADVERSARY_ACTIVITY", re.compile(
        r"china|chinese|prc|russia|russian|iran|dprk|north.korea|"
        r"yaogan|beidou|glonass|cosmos|shijian|jilin|gaofen",
        re.IGNORECASE,
    )),
    ("THREAT", re.compile(
        r"asat|anti.satellite|counterspace|counter.space|weapon|"
        r"debris|collision|threat|attack|jamming|spoofing|cyber|"
        r"missile|intercept|kill.vehicle",
        re.IGNORECASE,
    )),
    ("SPACE_WEATHER", re.compile(
        r"solar.flare|cme|coronal|geomagnetic|kp.index|radiation.storm|"
        r"aurora|magnetosphere|space.weather|swpc|proton.event",
        re.IGNORECASE,
    )),
    ("POLICY", re.compile(
        r"policy|regulation|treaty|executive.order|directive|legislation|"
        r"norms|governance|artemis.accords|outer.space.treaty|"
        r"congress|senate|dod|pentagon|ussf|space.force|space.command",
        re.IGNORECASE,
    )),
    ("TECHNOLOGY", re.compile(
        r"propulsion|sensor|radar|laser|optical|satellite.bus|"
        r"encryption|quantum|ai|autonomy|on.orbit.servicing|"
        r"refuel|deorbit|rendezvous|proximity",
        re.IGNORECASE,
    )),
    ("LAUNCH", re.compile(
        r"launch|rocket|falcon|starship|atlas|vulcan|soyuz|long.march|"
        r"electron|ariane|kuaizhou|vega|new.glenn|neutron",
        re.IGNORECASE,
    )),
    ("RESEARCH", re.compile(
        r"study|research|paper|analysis|simulation|model|experiment|"
        r"arxiv|journal|university|institute",
        re.IGNORECASE,
    )),
]


def _assign_tag(text: str) -> str:
    """Assign a relevance tag based on keyword matching against combined text."""
    for tag, pattern in _TAG_PATTERNS:
        if pattern.search(text):
            return tag
    return "RESEARCH"


# ---------------------------------------------------------------------------
# Spaceflight News API v4
# ---------------------------------------------------------------------------
_SFNEWS_BASE = "https://api.spaceflightnewsapi.net/v4"


async def _fetch_sfnews(client: httpx.AsyncClient, endpoint: str, limit: int = 15) -> List[dict]:
    """Fetch from a Spaceflight News API v4 endpoint."""
    url = f"{_SFNEWS_BASE}/{endpoint}/?limit={limit}&ordering=-published_at"
    try:
        r = await client.get(url, timeout=15)
        r.raise_for_status()
        raw = r.json()
    except Exception:
        return []

    items = []
    for item in raw.get("results", []):
        title = item.get("title", "")
        summary = item.get("summary", "")[:400]
        combined = f"{title} {summary}"
        items.append({
            "title": title,
            "source": f"SFNEWS/{endpoint}",
            "url": item.get("url", ""),
            "published_at": item.get("published_at", ""),
            "summary": summary,
            "relevance_tag": _assign_tag(combined),
            "news_site": item.get("news_site", ""),
            "image_url": item.get("image_url", ""),
        })
    return items


# ---------------------------------------------------------------------------
# ArXiv API — space security / warfare papers
# ---------------------------------------------------------------------------
_ARXIV_URL = (
    "http://export.arxiv.org/api/query?"
    "search_query=cat:astro-ph+AND+(space+warfare+OR+space+security+OR+anti-satellite+OR+counterspace)"
    "&sortBy=submittedDate&sortOrder=descending&max_results=10"
)

# ArXiv Atom namespace
_ATOM = "{http://www.w3.org/2005/Atom}"


async def fetch_arxiv_papers(client: httpx.AsyncClient) -> List[dict]:
    """Fetch recent space security academic papers from ArXiv."""
    cached = _cached("arxiv")
    if cached is not None:
        return cached

    try:
        r = await client.get(_ARXIV_URL, timeout=20)
        r.raise_for_status()
        root = ET.fromstring(r.text)
    except Exception:
        prev = _cache.get("arxiv")
        return prev["data"] if prev else []

    papers = []
    for entry in root.findall(f"{_ATOM}entry"):
        title_el = entry.find(f"{_ATOM}title")
        summary_el = entry.find(f"{_ATOM}summary")
        published_el = entry.find(f"{_ATOM}published")
        link_el = entry.find(f"{_ATOM}id")

        title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else ""
        summary = summary_el.text.strip().replace("\n", " ")[:400] if summary_el is not None and summary_el.text else ""
        published = published_el.text.strip() if published_el is not None and published_el.text else ""
        url = link_el.text.strip() if link_el is not None and link_el.text else ""

        # Extract authors
        authors = []
        for author_el in entry.findall(f"{_ATOM}author"):
            name_el = author_el.find(f"{_ATOM}name")
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        combined = f"{title} {summary}"
        papers.append({
            "title": title,
            "source": "ArXiv",
            "url": url,
            "published_at": published,
            "summary": summary,
            "relevance_tag": _assign_tag(combined),
            "authors": authors[:5],  # Cap at 5 authors
        })

    return _store("arxiv", papers)


# ---------------------------------------------------------------------------
# US Federal Register — space policy documents
# ---------------------------------------------------------------------------
_FED_REG_URL = (
    "https://www.federalregister.gov/api/v1/documents.json?"
    "conditions%5Bterm%5D=space+security&per_page=5&order=newest"
)


async def fetch_policy_updates(client: httpx.AsyncClient) -> List[dict]:
    """Fetch recent US Federal Register space security policy documents."""
    cached = _cached("policy")
    if cached is not None:
        return cached

    try:
        r = await client.get(_FED_REG_URL, timeout=15)
        r.raise_for_status()
        raw = r.json()
    except Exception:
        prev = _cache.get("policy")
        return prev["data"] if prev else []

    docs = []
    for item in raw.get("results", []):
        title = item.get("title", "")
        abstract = item.get("abstract") or ""
        excerpt = item.get("excerpts") or ""
        summary = (abstract or excerpt)[:400]
        combined = f"{title} {summary}"

        docs.append({
            "title": title,
            "source": "Federal Register",
            "url": item.get("html_url", ""),
            "published_at": item.get("publication_date", ""),
            "summary": summary,
            "relevance_tag": _assign_tag(combined) if _assign_tag(combined) != "RESEARCH" else "POLICY",
            "document_type": item.get("type", ""),
            "agencies": [a.get("name", "") for a in item.get("agencies", []) if isinstance(a, dict)],
        })

    return _store("policy", docs)


# ---------------------------------------------------------------------------
# NOAA SWPC Alerts — deep parsing
# ---------------------------------------------------------------------------
_SWPC_ALERTS_URL = "https://services.swpc.noaa.gov/products/alerts.json"


async def _fetch_swpc_alerts(client: httpx.AsyncClient) -> List[dict]:
    """Fetch and deeply parse NOAA SWPC space weather alerts."""
    cached = _cached("swpc_alerts")
    if cached is not None:
        return cached

    try:
        r = await client.get(_SWPC_ALERTS_URL, timeout=15)
        r.raise_for_status()
        raw = r.json()
    except Exception:
        prev = _cache.get("swpc_alerts")
        return prev["data"] if prev else []

    alerts = []
    if isinstance(raw, list):
        for alert in raw[-30:]:  # last 30 alerts
            if not isinstance(alert, dict):
                continue

            product_id = alert.get("product_id", "")
            message = alert.get("message", "")
            issue_dt = alert.get("issue_datetime", "")

            # Determine severity from product_id / message content
            severity = "INFO"
            if "WARNING" in product_id.upper() or "WARNING" in message[:200].upper():
                severity = "WARNING"
            elif "WATCH" in product_id.upper() or "WATCH" in message[:200].upper():
                severity = "WATCH"
            elif "ALERT" in product_id.upper() or "ALERT" in message[:200].upper():
                severity = "ALERT"

            # Extract summary from first meaningful line
            lines = [ln.strip() for ln in message.split("\n") if ln.strip()]
            summary_text = " ".join(lines[:3])[:400] if lines else ""

            alerts.append({
                "title": f"SWPC {severity}: {product_id}",
                "source": "NOAA/SWPC",
                "url": "https://www.swpc.noaa.gov/products/alerts-watches-and-warnings",
                "published_at": issue_dt,
                "summary": summary_text,
                "relevance_tag": "SPACE_WEATHER",
                "severity": severity,
                "product_id": product_id,
            })

    return _store("swpc_alerts", alerts)


# ---------------------------------------------------------------------------
# Unified Research Feed
# ---------------------------------------------------------------------------

async def fetch_research_feed(client: httpx.AsyncClient) -> List[dict]:
    """Aggregate all research sources into a unified intelligence feed sorted by time."""
    cached = _cached("research_feed")
    if cached is not None:
        return cached

    import asyncio
    articles, blogs, reports, arxiv, policy, swpc = await asyncio.gather(
        _fetch_sfnews(client, "articles", 15),
        _fetch_sfnews(client, "blogs", 10),
        _fetch_sfnews(client, "reports", 10),
        fetch_arxiv_papers(client),
        fetch_policy_updates(client),
        _fetch_swpc_alerts(client),
    )

    all_items = articles + blogs + reports + arxiv + policy + swpc

    # Sort by published_at descending (most recent first)
    def _sort_key(item: dict) -> str:
        dt = item.get("published_at", "")
        if not dt:
            return "0000-00-00"
        return dt

    all_items.sort(key=_sort_key, reverse=True)

    return _store("research_feed", all_items)
