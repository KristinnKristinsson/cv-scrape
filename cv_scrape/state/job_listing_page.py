"""State: a listing page's already-parsed links — which detail pages to fetch next,
and which listing page (if any) comes after this one. Mirrors
state/job_search_api_page.py's shape (a page's contents plus what flow needs to keep
paginating), for the same reason: flow shouldn't re-read the raw body to find out.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class JobListingPage:
    detail_urls: tuple[str, ...]
    next_url: str | None
