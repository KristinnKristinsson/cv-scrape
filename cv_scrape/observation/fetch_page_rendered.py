"""Observation: fetch a URL through a real headless browser, changing nothing.
Reveals content and challenge behavior that only appear after JS execution — a
different observation from fetch_page_raw.py's plain HTTP GET, not a caller-selecting
flag on one function, because a browser and a raw client are genuinely different
"other systems" to ask.
"""

import time
from dataclasses import dataclass

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from cv_scrape.observation.fetch_page_raw import PROBE_USER_AGENT


@dataclass(frozen=True)
class RenderedFetchResult:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes
    elapsed_ms: float


@dataclass(frozen=True)
class RenderedFetchFailure:
    url: str
    reason: str


def fetch_page_rendered(url: str, timeout: float = 20.0) -> RenderedFetchResult | RenderedFetchFailure:
    start = time.monotonic()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(user_agent=PROBE_USER_AGENT)
                response = page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
                if response is None:
                    return RenderedFetchFailure(url=url, reason="no response object from navigation")
                status = response.status
                headers = dict(response.headers)
                body = page.content().encode("utf-8")
            finally:
                browser.close()
    except (PlaywrightError, PlaywrightTimeoutError) as exc:
        return RenderedFetchFailure(url=url, reason=str(exc))

    elapsed_ms = (time.monotonic() - start) * 1000
    return RenderedFetchResult(url=url, status=status, headers=headers, body=body, elapsed_ms=elapsed_ms)
