import pytest

from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage
from cv_scrape.interaction.parse_ledigajobb_listing_page import parse_ledigajobb_listing_page
from cv_scrape.state.response_envelope import ResponseEnvelope


def test_detail_links_are_collected_and_deduplicated():
    body = b"""
    <a class="job-link" href="https://ledigajobb.se/jobb/aaa111/first-job" style="position:absolute" tabindex="-1"></a>
    <a class="h6 job-link" href="https://ledigajobb.se/jobb/aaa111/first-job" data-job-box-title>First job</a>
    <a class="h6 job-link" href="https://ledigajobb.se/jobb/bbb222/second-job" data-job-box-title>Second job</a>
    """
    envelope = ResponseEnvelope(url="https://ledigajobb.se/sok?pcb=utvecklare-jobb", status=200, headers={}, body=body)
    listing = parse_ledigajobb_listing_page(envelope)
    assert listing.detail_urls == (
        "https://ledigajobb.se/jobb/aaa111/first-job",
        "https://ledigajobb.se/jobb/bbb222/second-job",
    )


def test_next_link_is_resolved_to_an_absolute_url():
    body = b"""
    <a href="https://ledigajobb.se/jobb/aaa111/first-job" data-job-box-title>First job</a>
    <a class="page-link" href="/sok?p=2&pcb=utvecklare-jobb" rel="nofollow" aria-label="N\xc3\xa4sta"></a>
    """
    envelope = ResponseEnvelope(url="https://ledigajobb.se/sok?pcb=utvecklare-jobb", status=200, headers={}, body=body)
    listing = parse_ledigajobb_listing_page(envelope)
    assert listing.next_url == "https://ledigajobb.se/sok?p=2&pcb=utvecklare-jobb"


def test_missing_next_link_gives_none():
    body = b'<a href="https://ledigajobb.se/jobb/aaa111/first-job" data-job-box-title>First job</a>'
    envelope = ResponseEnvelope(url="https://ledigajobb.se/sok?pcb=utvecklare-jobb", status=200, headers={}, body=body)
    listing = parse_ledigajobb_listing_page(envelope)
    assert listing.next_url is None


def test_no_detail_links_is_rejected():
    envelope = ResponseEnvelope(url="https://ledigajobb.se/sok?pcb=utvecklare-jobb", status=200, headers={}, body=b"<html></html>")
    with pytest.raises(RejectedJobListingPage):
        parse_ledigajobb_listing_page(envelope)
