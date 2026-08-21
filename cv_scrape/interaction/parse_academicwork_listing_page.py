"""Interaction: boundary for www.academicwork.se's listing-page HTML shape. Same
split as parse_job_listing_page.py (jobbsafari.se) — finds detail URLs to follow
next, no per-field extraction, since that happens once downstream on the detail page
(parse_academicwork_job_posting.py).

academicwork.se-specific, same reasoning as jobbsafari's piece: a second static-HTML
site gets its own piece rather than a shared one parameterized by a flag. Reuses
RejectedJobListingPage from parse_job_listing_page.py since "no recognizable links
found" is the same determination regardless of which site's markup produced it.

No next_url is ever returned: per data/probes/www.academicwork.se/report.md's
Next.js/Payload listing page, the visible "page 2/3/..." control is a client-side
button (`setPage` React state, not an `<a href>`), and live-checking
`?page=2`/`?page=3` on `/lediga-jobb/stockholm` returned the exact same 10 links as
page 1 both times — the query string is ignored server-side. So a plain GET only ever
reaches the first `pageSize` (10) results for a given start URL; broader coverage
means scoping to more relevant start URLs (as this project already does for
jobbsafari.se's category pages), not paginating this one.
"""

import html
import re
from urllib.parse import urljoin

from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage
from cv_scrape.state.job_listing_page import JobListingPage
from cv_scrape.state.response_envelope import ResponseEnvelope

_DETAIL_HREF = re.compile(r'href=["\'](/lediga-jobb/j/[^"\'#]+)["\']', re.IGNORECASE)


def parse_academicwork_listing_page(envelope: ResponseEnvelope) -> JobListingPage:
    body_text = envelope.body.decode("utf-8", errors="ignore")

    detail_urls = tuple(
        dict.fromkeys(urljoin(envelope.url, html.unescape(href)) for href in _DETAIL_HREF.findall(body_text))
    )
    if not detail_urls:
        raise RejectedJobListingPage(f"{envelope.url}: no job-detail links found")

    return JobListingPage(detail_urls=detail_urls, next_url=None)
