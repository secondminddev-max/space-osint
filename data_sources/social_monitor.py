"""
Social Media Intelligence Monitor
Monitors open social media and public feeds for space-relevant intelligence.

Sources:
- Bluesky public search API (satellite, launch, ASAT, space warfare)
- Reddit space subreddits (r/space, r/spacex, r/spacepolicy, r/NonCredibleDefense)

Classification: UNCLASSIFIED // OSINT
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_cache: Dict[str, dict] = {}
_CACHE_TTL = 300  # 5 minutes


def _cached(key: str) -> Optional[list]:
    cached = _cache.get(key)
    if cached and (time.time() - cached["ts"]) < _CACHE_TTL:
        return cached["data"]
    return None


def _store(key: str, data: list) -> list:
    _cache[key] = {"data": data, "ts": time.time()}
    return data


# ---------------------------------------------------------------------------
# Relevance Scoring
# ---------------------------------------------------------------------------

_RELEVANCE_KEYWORDS = {
    # High relevance (3 points)
    "high": re.compile(
        r"anti.satellite|asat|counterspace|counter.space|space.warfare|"
        r"space.weapon|debris.cloud|collision.avoidance|"
        r"yaogan|shijian|cosmos.255|nudol|peresvet|"
        r"gps.jamming|gps.spoofing|satcom.jam|"
        r"space.force|ussf|space.command|spacecom|"
        r"tiangong|css\b|shenzhou",
        re.IGNORECASE,
    ),
    # Medium relevance (2 points)
    "medium": re.compile(
        r"satellite.launch|rocket.launch|spy.satellite|"
        r"reconnaissance.satellite|military.satellite|"
        r"space.debris|orbital.debris|conjunction|"
        r"starlink|falcon.9|electron|long.march|soyuz|"
        r"beidou|glonass|galileo|"
        r"space.policy|outer.space.treaty|artemis.accords|"
        r"solar.flare|geomagnetic|space.weather",
        re.IGNORECASE,
    ),
    # Low relevance (1 point)
    "low": re.compile(
        r"satellite|orbit|spacecraft|space.station|iss\b|"
        r"nasa\b|esa\b|jaxa|isro|cnsa|"
        r"rocket|launch.vehicle|payload|"
        r"missile|icbm|ballistic|hypersonic",
        re.IGNORECASE,
    ),
}

_REQUIRED_KEYWORDS = re.compile(
    r"satellite|space|launch|orbit|asat|missile|icbm|"
    r"rocket|spacecraft|starlink|spacex|nasa|esa|"
    r"debris|iss\b|tiangong|beidou|gps|"
    r"solar.flare|geomagnetic|counterspace|anti.satellite",
    re.IGNORECASE,
)


def _relevance_score(text: str) -> int:
    """Compute relevance score 0-10 based on keyword presence."""
    score = 0
    for kw_set in _RELEVANCE_KEYWORDS.get("high", []), :
        pass  # handled below

    if _RELEVANCE_KEYWORDS["high"].search(text):
        score += 3
    if _RELEVANCE_KEYWORDS["medium"].search(text):
        score += 2
    if _RELEVANCE_KEYWORDS["low"].search(text):
        score += 1

    # Cap at 10
    return min(score, 10)


def _is_relevant(text: str) -> bool:
    """Quick check if text contains any space-related keywords."""
    return bool(_REQUIRED_KEYWORDS.search(text))


# ---------------------------------------------------------------------------
# Bluesky Public Search API
# ---------------------------------------------------------------------------
_BSKY_URL = (
    "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    "?q=satellite+launch+OR+ASAT+OR+space+warfare&limit=20"
)


async def _fetch_bluesky(client: httpx.AsyncClient) -> List[dict]:
    """Search Bluesky public API for space-relevant posts."""
    cached = _cached("bluesky")
    if cached is not None:
        return cached

    try:
        r = await client.get(_BSKY_URL, timeout=15)
        r.raise_for_status()
        raw = r.json()
    except Exception:
        prev = _cache.get("bluesky")
        return prev["data"] if prev else []

    posts = []
    for post_data in raw.get("posts", []):
        record = post_data.get("record", {})
        text = record.get("text", "")

        if not _is_relevant(text):
            continue

        author = post_data.get("author", {})
        handle = author.get("handle", "unknown")
        display_name = author.get("displayName", handle)

        # Build Bluesky post URL
        uri = post_data.get("uri", "")
        # URI format: at://did:plc:xxx/app.bsky.feed.post/rkey
        post_url = ""
        if uri and handle:
            parts = uri.split("/")
            if len(parts) >= 5:
                rkey = parts[-1]
                post_url = f"https://bsky.app/profile/{handle}/post/{rkey}"

        created_at = record.get("createdAt", "")

        posts.append({
            "platform": "bluesky",
            "author": display_name,
            "handle": handle,
            "text": text[:500],
            "url": post_url,
            "timestamp": created_at,
            "relevance_score": _relevance_score(text),
        })

    posts.sort(key=lambda p: p["relevance_score"], reverse=True)
    return _store("bluesky", posts)


# ---------------------------------------------------------------------------
# Reddit JSON API
# ---------------------------------------------------------------------------
_REDDIT_URL = (
    "https://www.reddit.com/r/space+spacex+spacepolicy+NonCredibleDefense/.json"
    "?limit=20&sort=new"
)


async def _fetch_reddit(client: httpx.AsyncClient) -> List[dict]:
    """Fetch recent posts from space-related subreddits."""
    cached = _cached("reddit")
    if cached is not None:
        return cached

    headers = {
        "User-Agent": "SpaceOSINT/1.0 (research platform; contact: admin@example.com)",
    }
    try:
        r = await client.get(_REDDIT_URL, headers=headers, timeout=15)
        r.raise_for_status()
        raw = r.json()
    except Exception:
        prev = _cache.get("reddit")
        return prev["data"] if prev else []

    posts = []
    data = raw.get("data", {})
    children = data.get("children", [])

    for child in children:
        post = child.get("data", {})
        title = post.get("title", "")
        selftext = post.get("selftext", "")[:300]
        combined = f"{title} {selftext}"

        if not _is_relevant(combined):
            continue

        # Convert Unix timestamp
        created_utc = post.get("created_utc", 0)
        try:
            ts = datetime.fromtimestamp(created_utc, tz=timezone.utc).isoformat() if created_utc else ""
        except (ValueError, OSError):
            ts = ""

        permalink = post.get("permalink", "")
        url = f"https://www.reddit.com{permalink}" if permalink else ""

        posts.append({
            "platform": "reddit",
            "author": post.get("author", "unknown"),
            "text": combined[:500],
            "url": url,
            "timestamp": ts,
            "relevance_score": _relevance_score(combined),
            "subreddit": post.get("subreddit", ""),
            "score": post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
        })

    posts.sort(key=lambda p: p["relevance_score"], reverse=True)
    return _store("reddit", posts)


# ---------------------------------------------------------------------------
# Unified Social Intel Feed
# ---------------------------------------------------------------------------

async def fetch_social_intel(client: httpx.AsyncClient) -> List[dict]:
    """Unified social media feed relevant to space intelligence."""
    cached = _cached("social_feed")
    if cached is not None:
        return cached

    import asyncio
    bluesky, reddit = await asyncio.gather(
        _fetch_bluesky(client),
        _fetch_reddit(client),
        return_exceptions=True,
    )

    if isinstance(bluesky, Exception):
        bluesky = []
    if isinstance(reddit, Exception):
        reddit = []

    all_posts = list(bluesky) + list(reddit)

    # Sort by relevance score descending, then by timestamp
    all_posts.sort(
        key=lambda p: (p.get("relevance_score", 0), p.get("timestamp", "")),
        reverse=True,
    )

    return _store("social_feed", all_posts)
