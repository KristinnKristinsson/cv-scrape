"""Interaction: boundary for jobbsafari.se's listing-page HTML shape. Site layout
drift is still uncontrolled even after bytes decode cleanly (interaction, not logic —
same reasoning as parse_job_posting_html.py's split from receive_fetch_response.py).

This piece only finds URLs to follow next, not per-field data: per
data/probes/jobbsafari.se/report.md, the listing card's MUI/emotion markup carries no
description and churns its class names across deploys, while the detail page carries a
complete, stable JobPosting JSON-LD block. So per-field extraction happens once,
downstream, in parse_job_posting_json_ld.py — not duplicated here.

jobbsafari.se-specific (the `/jobb/` detail-link prefix and `rel="next"` pagination
link are this site's own shape), same as parse_job_search_api_response.py hardcodes
Arbetsformedlingen's response shape rather than taking a generic pattern — a second
static-HTML site would get its own piece, not a shared one parameterized by a flag.
"""

import re
from urllib.parse import urljoin

from cv_scrape.state.job_listing_page import JobListingPage
from cv_scrape.state.response_envelope import ResponseEnvelope

_DETAIL_HREF = re.compile(r'href=["\'](/jobb/[^"\'#]+)["\']', re.IGNORECASE)
_NEXT_LINK = re.compile(r'<link[^>]+rel=["\']next["\'][^>]+href=["\']([^"\']+)["\']', re.IGNORECASE)


class RejectedJobListingPage(Exception):
    """Raised when a listing page's response contains no recognizable job-detail links."""


def parse_job_listing_page(envelope: ResponseEnvelope) -> JobListingPage:
    body_text = envelope.body.decode("utf-8", errors="ignore")

    detail_urls = tuple(dict.fromkeys(urljoin(envelope.url, href) for href in _DETAIL_HREF.findall(body_text)))
    if not detail_urls:
        raise RejectedJobListingPage(f"{envelope.url}: no job-detail links found")

    next_match = _NEXT_LINK.search(body_text)
    next_url = urljoin(envelope.url, next_match.group(1)) if next_match else None

    return JobListingPage(detail_urls=detail_urls, next_url=next_url)
