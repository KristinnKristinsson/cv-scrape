"""Flow: jobbsafari.se spider. Two-stage per data/probes/jobbsafari.se/report.md: the
listing page's cards carry no description and sit behind churny MUI/emotion class
names, so this stage only follows links — job-detail pages
(interaction/parse_job_listing_page.py) — and lets
interaction/parse_job_posting_json_ld.py extract the full JobPosting from each detail
page's stable JobPosting JSON-LD block instead. Kept flow-only, same as
example_listing_spider.py — it delegates and yields/routes, never picks fields out of
the response itself, per structure.md's Ambiguous Call #3.

Scoped to two Stockholm listings, both walked independently (each paginating via the
page's own `rel="next"` link until the site stops emitting one, so neither runs past
its own inventory): `yrke/utvecklare` (the original scope) and `kategori/data-och-it`,
added per Objectives.md's jobbsafari-taxonomy-coverage check — the two overlap but
aren't the same set (confirmed: "Data Engineer till SPP," "Platform Engineer inom
Kubernetes," and a Sakerhetspolisen "DevOps Engineer" posting sit in `data-och-it`
but never appeared under `utvecklare`). `data-och-it` is jobbsafari's own broader
category, not a role-specific yrke tag, so like Platsbanken's `q` (Objectives.md's
step 2 finding) it's a recall tool, not a filter — real matches sit alongside
Servicetekniker/Saljare/etc. noise from the same category page. No new filtering
needed here: `logic/classify_role_family.py` already exists to sort exactly that
kind of loose result downstream, and `logic/deduplicate_job_postings.py` already
collapses the cross-listing overlap between the two start URLs by title+company.

No SitePolicy/CSS-selector draft is used here — see parse_job_listing_page.py's and
parse_job_posting_json_ld.py's docstrings for why this site's shape doesn't fit that
generic mechanism. classify_response.py gates both callbacks per structure.md's
documented job-posting-parsing chain: Cloudflare fronts this site (no active
challenge seen in probing, but a challenge/block response should never be parsed as if
it were real markup).
"""

import scrapy

from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage, parse_job_listing_page
from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.interaction.parse_job_posting_json_ld import parse_job_posting_json_ld
from cv_scrape.interaction.receive_fetch_response import RejectedResponse, receive_fetch_response
from cv_scrape.logic.classify_response import ResponseTag, classify_response
from cv_scrape.state.response_envelope import ResponseEnvelope


class JobbsafariListingSpider(scrapy.Spider):
    name = "jobbsafari_listing"
    start_urls = [
        "https://jobbsafari.se/lediga-jobb/ort/stockholm/yrke/utvecklare",
        "https://jobbsafari.se/lediga-jobb/ort/stockholm/kategori/data-och-it",
    ]

    def parse(self, response):
        envelope = _accepted_envelope(response)
        if envelope is None:
            return

        try:
            listing = parse_job_listing_page(envelope)
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
            yield parse_job_posting_json_ld(envelope)
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
