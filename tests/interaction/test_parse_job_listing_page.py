import pytest

from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage, parse_job_listing_page
from cv_scrape.state.response_envelope import ResponseEnvelope


def test_detail_links_are_collected_and_deduplicated():
    body = b"""
    <div id="jobentry-1"><a href="/jobb/first-job-1">First</a></div>
    <div id="jobentry-2"><a href="/jobb/second-job-2">Second</a></div>
    <a href="/jobb/first-job-1">duplicate mobile link</a>
    """
    envelope = ResponseEnvelope(url="https://jobbsafari.se/lediga-jobb/ort/stockholm", status=200, headers={}, body=body)
    listing = parse_job_listing_page(envelope)
    assert listing.detail_urls == (
        "https://jobbsafari.se/jobb/first-job-1",
        "https://jobbsafari.se/jobb/second-job-2",
    )


def test_next_link_is_resolved_to_an_absolute_url():
    body = b"""
    <link rel="next" href="/lediga-jobb/ort/stockholm?page=2">
    <a href="/jobb/first-job-1">First</a>
    """
    envelope = ResponseEnvelope(url="https://jobbsafari.se/lediga-jobb/ort/stockholm", status=200, headers={}, body=body)
    listing = parse_job_listing_page(envelope)
    assert listing.next_url == "https://jobbsafari.se/lediga-jobb/ort/stockholm?page=2"


def test_missing_next_link_gives_none():
    body = b'<a href="/jobb/first-job-1">First</a>'
    envelope = ResponseEnvelope(url="https://jobbsafari.se/lediga-jobb/ort/stockholm", status=200, headers={}, body=body)
    listing = parse_job_listing_page(envelope)
    assert listing.next_url is None


def test_no_detail_links_is_rejected():
    envelope = ResponseEnvelope(url="https://jobbsafari.se/lediga-jobb/ort/stockholm", status=200, headers={}, body=b"<html></html>")
    with pytest.raises(RejectedJobListingPage):
        parse_job_listing_page(envelope)
