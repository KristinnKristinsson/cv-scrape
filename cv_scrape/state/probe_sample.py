"""State: a reified single fetch-and-classify result gathered while probing a site.
Collected into a SiteProfile. Renderer is "raw" (plain HTTP) or "rendered" (headless
browser) — never a caller-selecting flag on a shared fetch function, two genuinely
different observations (see observation/fetch_page_raw.py, fetch_page_rendered.py).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProbeSample:
    url: str
    renderer: str
    fetched: bool
    status: int | None
    response_tag: str | None
    elapsed_ms: float | None
    error: str | None
