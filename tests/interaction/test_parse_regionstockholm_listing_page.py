import pytest

from cv_scrape.interaction.parse_job_listing_page import RejectedJobListingPage
from cv_scrape.interaction.parse_regionstockholm_listing_page import parse_regionstockholm_listing_page
from cv_scrape.state.response_envelope import ResponseEnvelope

_LISTING_URL = (
    "https://www.regionstockholm.se/jobb/lediga-jobb/"
    "?query=&orderBy=Published&skip=0&take=20&categories=Administration%2C+HR%2C+ekonomi%2C+juridik%2C+IT"
)


def _body_with(result_message: str, hrefs: list[str]) -> bytes:
    cards = "".join(f'<h2 class="mb-0 text-h4"><a href="{href}"><span>Title</span></a></h2>' for href in hrefs)
    return f'<html><body><span data-cy="search-result-message">{result_message}</span>{cards}</body></html>'.encode()


def test_detail_links_are_collected_and_deduplicated():
    body = _body_with(
        "Din sökning gav 61 lediga jobb",
        [
            "https://www.regionstockholm.se/jobb/lediga-jobb/org-a/first-job/",
            "https://www.regionstockholm.se/jobb/lediga-jobb/org-b/second-job/",
            "https://www.regionstockholm.se/jobb/lediga-jobb/org-a/first-job/",
        ],
    )
    envelope = ResponseEnvelope(url=_LISTING_URL, status=200, headers={}, body=body)
    listing = parse_regionstockholm_listing_page(envelope)
    assert listing.detail_urls == (
        "https://www.regionstockholm.se/jobb/lediga-jobb/org-a/first-job/",
        "https://www.regionstockholm.se/jobb/lediga-jobb/org-b/second-job/",
    )


def test_next_url_bumps_skip_by_take_and_preserves_other_params():
    body = _body_with("Din sökning gav 61 lediga jobb", ["https://www.regionstockholm.se/jobb/lediga-jobb/org-a/first-job/"])
    envelope = ResponseEnvelope(url=_LISTING_URL, status=200, headers={}, body=body)
    listing = parse_regionstockholm_listing_page(envelope)
    assert listing.next_url == (
        "https://www.regionstockholm.se/jobb/lediga-jobb/"
        "?query=&orderBy=Published&skip=20&take=20&categories=Administration%2C+HR%2C+ekonomi%2C+juridik%2C+IT"
    )


def test_next_url_is_none_once_skip_plus_take_reaches_the_total():
    body = _body_with("Din sökning gav 61 lediga jobb", ["https://www.regionstockholm.se/jobb/lediga-jobb/org-a/last-job/"])
    url = _LISTING_URL.replace("skip=0", "skip=60")
    envelope = ResponseEnvelope(url=url, status=200, headers={}, body=body)
    listing = parse_regionstockholm_listing_page(envelope)
    assert listing.next_url is None


def test_missing_result_total_gives_no_next_url():
    body = b'<html><body><h2><a href="https://www.regionstockholm.se/jobb/lediga-jobb/org-a/first-job/">x</a></h2></body></html>'
    envelope = ResponseEnvelope(url=_LISTING_URL, status=200, headers={}, body=body)
    listing = parse_regionstockholm_listing_page(envelope)
    assert listing.next_url is None


def test_no_detail_links_is_rejected():
    envelope = ResponseEnvelope(url=_LISTING_URL, status=200, headers={}, body=b"<html></html>")
    with pytest.raises(RejectedJobListingPage):
        parse_regionstockholm_listing_page(envelope)
