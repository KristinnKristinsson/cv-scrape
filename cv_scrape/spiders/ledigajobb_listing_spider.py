"""Flow: ledigajobb.se spider. Two-stage per data/probes/ledigajobb.se/report.md's
recommendation: the listing page's cards carry title/company/meta text but no
description, so this stage only follows detail links
(interaction/parse_ledigajobb_listing_page.py) and lets
interaction/parse_ledigajobb_job_posting_json_ld.py extract the full JobPosting from
each detail page's JobPosting JSON-LD block (confirmed present live -- the probe report
didn't sample a detail page, so this is a fill-in-the-gap over the draft SitePolicy,
same situation academicwork.se's spider was built to handle, though here it resolved
in the easier direction: a stable JSON-LD block, not raw HTML selectors). Kept
flow-only, same as jobbsafari_listing_spider.py and example_listing_spider.py -- it
delegates and yields/routes, never picks fields out of the response itself, per
structure.md's Ambiguous Call #3.

Scoped to one start URL: `/pr/utvecklare-jobb/stockholm` -- the site's own "Utvecklare"
[Developer] profession-tag page, filtered by an appended location segment. Chosen over
the site's `/sok?pcb=utvecklare-jobb` search endpoint (this project's original choice)
because that endpoint is blocked outright: `robots.txt` disallows `/sok?*` wholesale, a
restriction the probe report's blanket "robots.txt: allowed" verdict missed since it
only checked the homepage path. `/pr/<tag>` is a different, unblocked route to the same
per-profession tag pages, and combining it with `/stockholm` genuinely narrows results
(confirmed live: three sampled `/pr/utvecklare-jobb/stockholm` postings' own JSON-LD all
had `addressLocality: Stockholm`; unlike the earlier `t=stockholm&t=utvecklare-jobb`
tag-search combo, which returned postings from Växjö and Borås alongside Stockholm and
was rejected for that reason). Same "topically relevant filter, not the whole firehose"
choice as jobbsafari's `data-och-it` and academicwork's category GUIDs, just reached via
a different URL shape on this site. `logic/classify_role_family.py` still does the real
role-family filtering downstream.

Pagination follows next_url from parse_ledigajobb_listing_page.py (confirmed live:
`/pr/utvecklare-jobb/stockholm` runs `/2` through `/7`, each a genuinely different page
-- consecutive pages shared only 1 of 50 cards -- until the site stops emitting a
"Nästa" control).

No SitePolicy/CSS-selector draft is used here -- the probe report's draft was explicitly
unverified (no detail page was sampled during probing) and inferred a
`div.job-card`/`a.job-link` shape that live-checking replaced with the more reliable
`data-job-box-title` marker; see parse_ledigajobb_listing_page.py's docstring.
classify_response.py gates both callbacks before trusting a body as real markup, same
defensive posture as the other two spiders -- ledigajobb.se sits behind Cloudflare
(CDN-only during probing, no active challenge seen, but a challenge/block response
should never be parsed as if it were real markup).
"""

import scrapy

from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage
from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.interaction.parse_ledigajobb_job_posting_json_ld import parse_ledigajobb_job_posting_json_ld
from cv_scrape.interaction.parse_ledigajobb_listing_page import parse_ledigajobb_listing_page
from cv_scrape.interaction.receive_fetch_response import RejectedResponse, receive_fetch_response
from cv_scrape.logic.classify_response import ResponseTag, classify_response
from cv_scrape.state.response_envelope import ResponseEnvelope


class LedigajobbListingSpider(scrapy.Spider):
    name = "ledigajobb_listing"
    start_urls = ["https://ledigajobb.se/pr/utvecklare-jobb/stockholm"]

    def parse(self, response):
        envelope = _accepted_envelope(response)
        if envelope is None:
            return

        try:
            listing = parse_ledigajobb_listing_page(envelope)
        except RejectedJobListingPage:
            return

        for detail_url in listing.detail_urls:
            yield response.follow(detail_url, callback=self.parse_detail)
        if listing.next_url:
            yield response.follow(listing.next_url, callback=self.parse)

    def parse_detail(self, response):
        envelope = _accepted_envelope(response)
        if envelope is None:
            return

        try:
            yield parse_ledigajobb_job_posting_json_ld(envelope)
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
