"""Flow: www.academicwork.se spider. Two-stage per
data/probes/www.academicwork.se/report.md: the listing page's cards carry title/
company/meta text but no description, so this stage only follows detail links
(interaction/parse_academicwork_listing_page.py) and lets
interaction/parse_academicwork_job_posting.py extract the full posting from each
detail page's visible markup — unlike jobbsafari.se, academicwork.se's detail pages
carry no JobPosting JSON-LD, so that piece parses Tailwind HTML directly instead of a
structured-data block. Kept flow-only, same as jobbsafari_listing_spider.py and
example_listing_spider.py — it delegates and yields/routes, never picks fields out of
the response itself, per structure.md's Ambiguous Call #3.

Scoped to one start URL: academicwork.se's own advanced-search filter combining three
category GUIDs (opaque IDs the site assigns its filter checkboxes — no human-readable
label is exposed anywhere in the response, but the resulting postings are consistently
data/software-engineering roles: Data Engineer, Database Developer, .NET/Software
Engineer, Data Analyst) with `w=fullTime` and Stockholm's `l=whosonfirst:locality:...`
code. Chosen over the broader `/lediga-jobb/stockholm/it` category (receptionists,
accountants, generic IT support) as a closer match to this project's target role
families — same "topically relevant filter, not the whole firehose" choice as
jobbsafari's `data-och-it`. `logic/classify_role_family.py` still does the real
filtering downstream.

No pagination: parse_academicwork_listing_page.py's `next_url` is always None (see
its docstring — page 2+ is client-side only, unreachable via plain GET; re-confirmed
against this exact start URL, where `&page=2`/`&page=3` returned the identical 10
links as page 1). So each run is capped at this query's first `pageSize` results (10
of 17 total as of probing). Broader recall means adding more relevant start URLs
later, not paginating this one.

No SitePolicy/CSS-selector draft is used here — see parse_academicwork_listing_page.py's
and parse_academicwork_job_posting.py's docstrings for why this site's shape doesn't
fit that generic mechanism. classify_response.py gates both callbacks before trusting
a body as real markup, same defensive posture as jobbsafari_listing_spider.py, even
though academicwork.se showed no WAF during probing.
"""

import scrapy

from cv_scrape.interaction.parse_academicwork_job_posting import parse_academicwork_job_posting
from cv_scrape.interaction.parse_academicwork_listing_page import parse_academicwork_listing_page
from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage
from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.interaction.receive_fetch_response import RejectedResponse, receive_fetch_response
from cv_scrape.logic.classify_response import ResponseTag, classify_response
from cv_scrape.state.response_envelope import ResponseEnvelope


class AcademicworkListingSpider(scrapy.Spider):
    name = "academicwork_listing"
    start_urls = [
        "https://www.academicwork.se/lediga-jobb"
        "?c=407ea39c-03f4-4bb2-bc15-c6062acb997c"
        "&c=ea5a5587-c51f-43b6-9546-9d7e6f48f98c"
        "&c=2084a48c-dcf4-4d8d-86ad-40be7cab5983"
        "&w=fullTime"
        "&l=whosonfirst%3Alocality%3A101752307"
    ]

    def parse(self, response):
        envelope = _accepted_envelope(response)
        if envelope is None:
            return

        try:
            listing = parse_academicwork_listing_page(envelope)
        except RejectedJobListingPage:
            return

        for detail_url in listing.detail_urls:
            yield response.follow(detail_url, callback=self.parse_detail)

    def parse_detail(self, response):
        envelope = _accepted_envelope(response)
        if envelope is None:
            return

        try:
            yield parse_academicwork_job_posting(envelope)
        except RejectedJobPosting:
            return


def _accepted_envelope(response) -> ResponseEnvelope | None:
    try:
        envelope = receive_fetch_response(
            url=response.url,
            status=response.status,
            headers={k.decode(): v[0].decode() for k, v in response.headers.items()},
            body=response.body,
        )
    except RejectedResponse:
        return None

    return envelope if classify_response(envelope) is ResponseTag.OK else None
