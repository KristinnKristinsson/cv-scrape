"""Observation: fetch a URL over plain HTTP, changing nothing. Per structure.md's
Ambiguous Call #1, downloading a page is observation, not effect — our fetches are
idempotent GETs. Reused for the listing page, robots.txt, and any discovered
same-domain links; there is no separate "fetch robots.txt" piece.
"""

from dataclasses import dataclass

import httpx

PROBE_USER_AGENT = "cv-scrape-probe/0.1 (+personal job-search tool; contact via repo owner)"


@dataclass(frozen=True)
class RawFetchResult:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes
    elapsed_ms: float


@dataclass(frozen=True)
class RawFetchFailure:
    url: str
    reason: str


def fetch_page_raw(url: str, timeout: float = 15.0) -> RawFetchResult | RawFetchFailure:
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True, headers={"User-Agent": PROBE_USER_AGENT})
    except httpx.HTTPError as exc:
        return RawFetchFailure(url=url, reason=str(exc))

    return RawFetchResult(
        url=str(response.url),
        status=response.status_code,
        headers=dict(response.headers),
        body=response.content,
        elapsed_ms=response.elapsed.total_seconds() * 1000,
    )
