"""
Search module — DuckDuckGo (primary), Google (fallback).
Returns list of {"title": ..., "url": ..., "snippet": ...}
"""
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def search_duckduckgo(query: str, max_results: int = 8) -> list[dict]:
    try:
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=HEADERS,
            timeout=10
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        results = []
        for r in soup.select(".result__body"):
            title_tag = r.select_one(".result__title a")
            snippet_tag = r.select_one(".result__snippet")
            if not title_tag: continue
            url = title_tag.get("href", "")
            # DDG wraps URLs — unwrap
            if "uddg=" in url:
                from urllib.parse import unquote, urlparse, parse_qs
                url = unquote(parse_qs(urlparse(url).query).get("uddg", [""])[0])
            results.append({
                "title":   title_tag.get_text(strip=True),
                "url":     url,
                "snippet": snippet_tag.get_text(strip=True) if snippet_tag else ""
            })
            if len(results) >= max_results:
                break
        return results
    except Exception as e:
        return []

def search_google(query: str, max_results: int = 8) -> list[dict]:
    try:
        resp = requests.get(
            "https://www.google.com/search",
            params={"q": query, "num": max_results},
            headers=HEADERS,
            timeout=10
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        results = []
        for g in soup.select("div.tF2Cxc, div.g"):
            title_tag = g.select_one("h3")
            link_tag  = g.select_one("a")
            snip_tag  = g.select_one(".VwiC3b, .s3v9rd, span")
            if not title_tag or not link_tag: continue
            url = link_tag.get("href", "")
            if not url.startswith("http"): continue
            results.append({
                "title":   title_tag.get_text(strip=True),
                "url":     url,
                "snippet": snip_tag.get_text(strip=True) if snip_tag else ""
            })
            if len(results) >= max_results:
                break
        return results
    except Exception:
        return []

def search(query: str, max_results: int = 8) -> list[dict]:
    """Try DuckDuckGo first, fall back to Google."""
    results = search_duckduckgo(query, max_results)
    if not results:
        results = search_google(query, max_results)
    return results
