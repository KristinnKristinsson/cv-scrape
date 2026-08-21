"""Flow: www.regionstockholm.se spider. Two-stage per
data/probes/www.regionstockholm.se/report.md: the listing page's cards carry title/
org/employment-type but no description, so this stage only follows detail links
(interaction/parse_regionstockholm_listing_page.py) and lets
interaction/parse_regionstockholm_job_posting_json_ld.py extract the full JobPosting
from each detail page's JobPosting JSON-LD block plus its `<h1>` (that site's JSON-LD
`title` field is bugged -- see that piece's docstring). Kept flow-only, same as
jobbsafari_listing_spider.py and example_listing_spider.py -- it delegates and
yields/routes, never picks fields out of the response itself, per structure.md's
Ambiguous Call #3.

Scoped to one start URL supplied directly by the user: the site's own "Administration,
HR, ekonomi, juridik, IT" category filter (61 postings as of probing) -- the closest of
this site's own categories to this project's target software/IT role families, same
"topically relevant filter, not the whole firehose" choice as jobbsafari's
`data-och-it`, academicwork's category GUIDs, and ledigajobb's `utvecklare-jobb` tag.
It's a broader net than those three (mixing in general admin/HR/legal/finance roles
alongside IT), same tradeoff jobbsafari's `data-och-it` already makes --
`logic/classify_role_family.py` does the real filtering downstream.

No location scoping beyond this: unlike jobbsafari/academicwork/ledigajobb, this site
has no separate location facet in its query params at all (only `categories`,
`organizations`, `departments`, `subDepartments`, `placements`, `employmentScopes`) --
but since Region Stockholm is inherently a Stockholm-region employer (confirmed: every
sampled posting's `jobLocation` was a Stockholm-area municipality -- Stockholm,
Danderyd, Norrtälje), no further scoping is needed here.

Pagination follows next_url from parse_regionstockholm_listing_page.py, which
synthesizes it from the request's own `skip`/`take` query params and the page's
printed result total (this site has no next-page link in its server-rendered markup
at all -- see that piece's docstring for why a plain GET still works).

No SitePolicy/CSS-selector draft is used here -- the probe report's draft targeted the
listing page's card markup only and never sampled a detail page; see
parse_regionstockholm_listing_page.py's and
parse_regionstockholm_job_posting_json_ld.py's docstrings for what live-checking found
instead. classify_response.py gates both callbacks before trusting a body as real
markup, same defensive posture as the other three spiders -- regionstockholm.se sits
behind Cloudflare (CDN-only during probing, no active challenge seen, but a
challenge/block response should never be parsed as if it were real markup).
"""

import scrapy

from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage
from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.interaction.parse_regionstockholm_job_posting_json_ld import parse_regionstockholm_job_posting_json_ld
from cv_scrape.interaction.parse_regionstockholm_listing_page import parse_regionstockholm_listing_page
from cv_scrape.interaction.receive_fetch_response import RejectedResponse, receive_fetch_response
from cv_scrape.logic.classify_response import ResponseTag, classify_response
from cv_scrape.state.response_envelope import ResponseEnvelope


class RegionstockholmListingSpider(scrapy.Spider):
    name = "regionstockholm_listing"
    start_urls = [
        "https://www.regionstockholm.se/jobb/lediga-jobb/"
        "?query=&orderBy=Published&skip=0&take=20"
        "&categories=Administration%2C+HR%2C+ekonomi%2C+juridik%2C+IT"
        "&organizations=&departments=&subDepartments=&placements=&employmentScopes="
    ]

    def parse(self, response):
        envelope = _accepted_envelope(response)
        if envelope is None:
            return

        try:
            listing = parse_regionstockholm_listing_page(envelope)
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
            yield parse_regionstockholm_job_posting_json_ld(envelope)
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
