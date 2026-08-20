"""Flow: placeholder spider demonstrating the pattern. Kept flow-only — it must never
pick fields out of the response itself (that's interaction/parse_job_posting_html.py)
or decide anything; it only delegates and yields/routes.

Lives under spiders/, not flow/, because Scrapy discovers spider classes by that
directory path — a framework requirement on file location, not a behavioral category.
The `except RejectedJobPosting` is routing on the tag the interaction boundary already
determined (rejected vs. accepted), not a decision made here.
"""

import scrapy

from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting, parse_job_posting_html
from cv_scrape.interaction.receive_fetch_response import receive_fetch_response
from cv_scrape.state.site_policy import SitePolicy

EXAMPLE_POLICY = SitePolicy(
    domain="example.com",
    listing_selector="",
    title_selector="",
    company_selector="",
    description_selector="",
)


class ExampleListingSpider(scrapy.Spider):
    name = "example_listing"
    start_urls = ["https://example.com/jobs"]

    def parse(self, response):
        envelope = receive_fetch_response(
            url=response.url,
            status=response.status,
            headers={k.decode(): v[0].decode() for k, v in response.headers.items()},
            body=response.body,
        )
        try:
            yield parse_job_posting_html(envelope, EXAMPLE_POLICY)
        except RejectedJobPosting:
            return
