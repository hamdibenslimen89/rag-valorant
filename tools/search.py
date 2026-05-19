"""
tools/search.py
Minimal web-search helper (DuckDuckGo HTML scrape, no API key needed).
Returns a list of {"title": str, "url": str, "snippet": str} dicts.
"""
from __future__ import annotations

import urllib.parse
import urllib.request
import re

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; valorant-agent/1.0)"
    )
}


def ddg_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Scrape DuckDuckGo HTML results for *query*.
    Returns up to *max_results* result dicts.
    """
    encoded = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"

    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        print(f"[search] Request failed: {exc}")
        return []

    results = []
    for m in re.finditer(
        r'class="result__title".*?href="([^"]+)"[^>]*>(.*?)</a>.*?'
        r'class="result__snippet"[^>]*>(.*?)</span>',
        html,
        re.DOTALL,
    ):
        url_raw, title_raw, snippet_raw = m.groups()
        results.append(
            {
                "title": re.sub(r"<[^>]+>", "", title_raw).strip(),
                "url": url_raw,
                "snippet": re.sub(r"<[^>]+>", "", snippet_raw).strip(),
            }
        )
        if len(results) >= max_results:
            break

    return results
