"""Interaction: boundary for ledigajobb.se's listing-page HTML shape. Same split as
parse_job_listing_page.py (jobbsafari.se) and parse_academicwork_listing_page.py — finds
detail URLs to follow next, no per-field extraction, since the detail page carries a
complete, stable JobPosting JSON-LD block (parse_ledigajobb_job_posting_json_ld.py).

ledigajobb.se-specific, same reasoning as the other two sites' listing pieces: a second
static-HTML site gets its own piece rather than a shared one parameterized by a flag.
Reuses RejectedJobListingPage from parse_job_listing_page.py since "no recognizable
links found" is the same determination regardless of which site's markup produced it.

Per data/probes/ledigajobb.se/report.md, each card renders its title as an
`<a data-job-box-title href="https://ledigajobb.se/jobb/<id>/<slug>">` -- a reliable,
one-per-card marker confirmed live (50 cards, 50 unique data-job-box-title hrefs, no
duplicates), unlike the surrounding `job-link` class which is reused by extra
absolutely-positioned overlay anchors and duplicate desktop/mobile anchors pointing at
the same URL.

Pagination is real and server-rendered (confirmed live: `/sok?p=2&pcb=...` returns a
different, mostly-non-overlapping set of cards than page 1, and the last page's markup
has no "Nästa" control) -- unlike academicwork.se's client-side-only pagination. The
"Nästa" control's href is followed as next_url; its absence (last page) means next_url
is None.
"""

import re
from urllib.parse import urljoin

from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage
from cv_scrape.state.job_listing_page import JobListingPage
from cv_scrape.state.response_envelope import ResponseEnvelope

_DETAIL_HREF = re.compile(r'<a[^>]*href="([^"]+)"[^>]*data-job-box-title', re.IGNORECASE)
_NEXT_HREF = re.compile(r'<a[^>]*href="([^"]+)"[^>]*aria-label="Nästa"', re.IGNORECASE)


def parse_ledigajobb_listing_page(envelope: ResponseEnvelope) -> JobListingPage:
    body_text = envelope.body.decode("utf-8", errors="ignore")

    detail_urls = tuple(dict.fromkeys(urljoin(envelope.url, href) for href in _DETAIL_HREF.findall(body_text)))
    if not detail_urls:
        raise RejectedJobListingPage(f"{envelope.url}: no job-detail links found")

    next_match = _NEXT_HREF.search(body_text)
    next_url = urljoin(envelope.url, next_match.group(1)) if next_match else None

    return JobListingPage(detail_urls=detail_urls, next_url=next_url)
