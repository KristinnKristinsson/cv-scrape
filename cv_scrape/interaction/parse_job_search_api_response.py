"""Interaction: boundary for Arbetsförmedlingen's JobSearch API response body. The
body still crosses receive_fetch_response first like every other fetched body in
this project (status-code and UTF-8 guard) — this piece adds the JSON-shape guard
on top and turns each hit into a JobPosting.

A different mechanism from parse_job_posting_html.py (JSON key access vs CSS/XPath
selectors against one HTML page), so a separate piece rather than a shared function
with a format flag — same split as fetch_page_raw/fetch_page_rendered. Reuses
RejectedJobPosting from parse_job_posting_html.py, though: "a candidate that doesn't
satisfy JobPosting's shape" is the same determination regardless of source format,
so flow can catch one exception type from either parser.

One malformed ad among many on a page is not grounds for discarding the rest of the
page, so per-ad failures are caught and skipped here rather than propagated —
unlike the top-level JSON-shape guard, which aborts the whole page.
"""

import json

from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.state.job_posting import JobPosting
from cv_scrape.state.job_search_api_page import JobSearchApiPage
from cv_scrape.state.response_envelope import ResponseEnvelope

SOURCE_DOMAIN = "arbetsformedlingen.se"


class RejectedJobSearchApiResponse(Exception):
    """Raised when the response body isn't decodable JSON in the API's documented shape."""


def parse_job_search_api_response(envelope: ResponseEnvelope) -> JobSearchApiPage:
    try:
        payload = json.loads(envelope.body)
    except json.JSONDecodeError as exc:
        raise RejectedJobSearchApiResponse(f"{envelope.url}: body is not valid JSON") from exc

    hits = payload.get("hits") if isinstance(payload, dict) else None
    total = payload.get("total", {}).get("value") if isinstance(payload, dict) else None
    if not isinstance(hits, list) or not isinstance(total, int):
        raise RejectedJobSearchApiResponse(f"{envelope.url}: response is missing 'hits' or 'total.value'")

    postings = []
    for ad in hits:
        try:
            postings.append(_parse_ad(ad))
        except RejectedJobPosting:
            continue

    return JobSearchApiPage(postings=tuple(postings), total=total)


def _parse_ad(ad: object) -> JobPosting:
    if not isinstance(ad, dict):
        raise RejectedJobPosting("ad is not a JSON object")

    url = ad.get("webpage_url")
    title = ad.get("headline")
    company = (ad.get("employer") or {}).get("name")
    description = (ad.get("description") or {}).get("text")
    if not (url and title and company and description):
        raise RejectedJobPosting(f"{url or ad.get('id') or '<unknown>'}: missing required field(s)")

    workplace_address = ad.get("workplace_address") or {}
    return JobPosting(
        url=url,
        source_domain=SOURCE_DOMAIN,
        title=title,
        company=company,
        description=description,
        location=workplace_address.get("municipality") or workplace_address.get("region"),
        posted_at=ad.get("publication_date"),
    )
