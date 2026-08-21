"""Interaction: boundary for www.regionstockholm.se's listing-page HTML shape. Same
split as parse_job_listing_page.py (jobbsafari.se) and the other sites' listing
pieces -- finds detail URLs to follow next, no per-field extraction, since the detail
page carries a JobPosting JSON-LD block (parse_regionstockholm_job_posting_json_ld.py).

regionstockholm.se-specific, same reasoning as the other sites' listing pieces: a
second static-HTML site gets its own piece rather than a shared one parameterized by
a flag. Reuses RejectedJobListingPage from parse_job_listing_page.py since "no
recognizable links found" is the same determination regardless of which site's markup
produced it.

Per data/probes/www.regionstockholm.se/report.md, each card renders its title inside
an `<h2><a href="https://www.regionstockholm.se/jobb/lediga-jobb/<org>/<slug>/">` --
confirmed live (20 cards, 20 matches, no duplicates).

Unlike the other three sites, this listing page has no next-page link to follow at
all (no `rel="next"`, no visible "next page" href in server-rendered markup --
pagination here is a "load more" control the page's own JS drives). But it's still
crawlable via a plain GET: `skip`/`take` query params on the request URL are honored
server-side (confirmed live: skip=20 returns a wholly different set of cards than
skip=0, and the site prints its own result total in a stable
`data-cy="search-result-message"` span -- "Din sökning gav 61 lediga jobb" when
filtered, "Visar 432 lediga jobb" unfiltered, same marker either way). So next_url is
synthesized here: bump the current request's own `skip` by its own `take` and keep
every other query param (the category/org/etc. filters) unchanged, stopping once
that would run past the printed total.
"""

import re
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit

from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage
from cv_scrape.state.job_listing_page import JobListingPage
from cv_scrape.state.response_envelope import ResponseEnvelope

_DETAIL_HREF = re.compile(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"', re.IGNORECASE)
_RESULT_TOTAL = re.compile(r'data-cy="search-result-message"[^>]*>[^<]*?(\d+)[^<]*<', re.IGNORECASE)


def parse_regionstockholm_listing_page(envelope: ResponseEnvelope) -> JobListingPage:
    body_text = envelope.body.decode("utf-8", errors="ignore")

    detail_urls = tuple(dict.fromkeys(urljoin(envelope.url, href) for href in _DETAIL_HREF.findall(body_text)))
    if not detail_urls:
        raise RejectedJobListingPage(f"{envelope.url}: no job-detail links found")

    return JobListingPage(detail_urls=detail_urls, next_url=_next_page_url(envelope.url, body_text))


def _next_page_url(url: str, body_text: str) -> str | None:
    total_match = _RESULT_TOTAL.search(body_text)
    if not total_match:
        return None

    split_url = urlsplit(url)
    params = parse_qs(split_url.query, keep_blank_values=True)
    skip = int((params.get("skip") or ["0"])[0])
    take = int((params.get("take") or ["0"])[0])
    if take <= 0 or skip + take >= int(total_match.group(1)):
        return None

    params["skip"] = [str(skip + take)]
    next_query = urlencode(params, doseq=True)
    return urlunsplit(split_url._replace(query=next_query))
