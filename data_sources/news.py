"""
Spaceflight News API v4
https://api.spaceflightnewsapi.net/v4/
"""
import time
import httpx
from config import CACHE_TTL_NEWS

_cache = {}
_URL = "https://api.spaceflightnewsapi.net/v4/articles/?limit=25&ordering=-published_at"


async def fetch_news(client: httpx.AsyncClient) -> list:
    now = time.time()
    cached = _cache.get("news")
    if cached and (now - cached["ts"]) < CACHE_TTL_NEWS:
        return cached["data"]

    try:
        r = await client.get(_URL, timeout=15)
        r.raise_for_status()
        raw = r.json()
    except Exception:
        return _cache.get("news", {}).get("data", [])

    articles = []
    for item in raw.get("results", []):
        articles.append({
            "title": item.get("title", ""),
            "summary": item.get("summary", "")[:300],
            "url": item.get("url", ""),
            "image_url": item.get("image_url", ""),
            "news_site": item.get("news_site", ""),
            "published_at": item.get("published_at", ""),
        })

    _cache["news"] = {"data": articles, "ts": now}
    return articles
