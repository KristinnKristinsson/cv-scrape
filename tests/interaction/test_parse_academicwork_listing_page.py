import pytest

from cv_scrape.interaction.parse_academicwork_listing_page import parse_academicwork_listing_page
from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage
from cv_scrape.state.response_envelope import ResponseEnvelope


def test_detail_links_are_collected_and_deduplicated():
    body = b"""
    <a href="/lediga-jobb/j/first-job/AB12CD?l=whosonfirst%3Alocality%3A1"><img/>First</a>
    <a href="/lediga-jobb/j/second-job/EF34GH?l=whosonfirst%3Alocality%3A1">Second</a>
    <a href="/lediga-jobb/j/first-job/AB12CD?l=whosonfirst%3Alocality%3A1">duplicate title link</a>
    """
    envelope = ResponseEnvelope(url="https://www.academicwork.se/lediga-jobb/stockholm/it", status=200, headers={}, body=body)
    listing = parse_academicwork_listing_page(envelope)
    assert listing.detail_urls == (
        "https://www.academicwork.se/lediga-jobb/j/first-job/AB12CD?l=whosonfirst%3Alocality%3A1",
        "https://www.academicwork.se/lediga-jobb/j/second-job/EF34GH?l=whosonfirst%3Alocality%3A1",
    )


def test_next_url_is_always_none():
    body = b'<a href="/lediga-jobb/j/first-job/AB12CD">First</a>'
    envelope = ResponseEnvelope(url="https://www.academicwork.se/lediga-jobb/stockholm/it", status=200, headers={}, body=body)
    listing = parse_academicwork_listing_page(envelope)
    assert listing.next_url is None


def test_html_escaped_ampersands_in_query_strings_are_unescaped():
    body = b'<a href="/lediga-jobb/j/first-job/AB12CD?b=1&amp;c=2&amp;c=3">First</a>'
    envelope = ResponseEnvelope(url="https://www.academicwork.se/lediga-jobb/stockholm/it", status=200, headers={}, body=body)
    listing = parse_academicwork_listing_page(envelope)
    assert listing.detail_urls == ("https://www.academicwork.se/lediga-jobb/j/first-job/AB12CD?b=1&c=2&c=3",)


def test_no_detail_links_is_rejected():
    envelope = ResponseEnvelope(url="https://www.academicwork.se/lediga-jobb/stockholm/it", status=200, headers={}, body=b"<html></html>")
    with pytest.raises(RejectedJobListingPage):
        parse_academicwork_listing_page(envelope)
