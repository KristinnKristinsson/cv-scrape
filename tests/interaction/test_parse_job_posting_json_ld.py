import json

import pytest

from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.interaction.parse_job_posting_json_ld import parse_job_posting_json_ld
from cv_scrape.state.response_envelope import ResponseEnvelope

_VALID_JOB_POSTING = {
    "@context": "https://schema.org/",
    "@type": "JobPosting",
    "datePosted": "2026-08-12T22:00:01.000Z",
    "description": "<strong>About the role</strong><br />Do stuff &amp; things.",
    "title": "Business Controller Trading",
    "hiringOrganization": {"@type": "Organization", "name": "VAROPreem"},
    "jobLocation": {
        "@type": "Place",
        "address": {"@type": "PostalAddress", "addressLocality": "Stockholm", "addressRegion": "Stockholm"},
    },
}


def _envelope_with(job_posting: dict) -> ResponseEnvelope:
    body = f'<html><head><script type="application/ld+json">{json.dumps(job_posting)}</script></head></html>'.encode()
    return ResponseEnvelope(url="https://jobbsafari.se/jobb/business-controller-trading-spsre-20479645", status=200, headers={}, body=body)


def test_valid_job_posting_json_ld_is_parsed():
    posting = parse_job_posting_json_ld(_envelope_with(_VALID_JOB_POSTING))
    assert posting.url == "https://jobbsafari.se/jobb/business-controller-trading-spsre-20479645"
    assert posting.source_domain == "jobbsafari.se"
    assert posting.title == "Business Controller Trading"
    assert posting.company == "VAROPreem"
    assert posting.location == "Stockholm"
    assert posting.posted_at == "2026-08-12T22:00:01.000Z"


def test_description_html_is_stripped_and_unescaped():
    posting = parse_job_posting_json_ld(_envelope_with(_VALID_JOB_POSTING))
    assert posting.description == "About the role Do stuff & things."


def test_missing_json_ld_block_is_rejected():
    envelope = ResponseEnvelope(url="https://jobbsafari.se/jobb/x", status=200, headers={}, body=b"<html></html>")
    with pytest.raises(RejectedJobPosting):
        parse_job_posting_json_ld(envelope)


def test_non_job_posting_json_ld_is_rejected():
    other = {"@context": "https://schema.org/", "@type": "WebSite", "name": "jobbsafari.se"}
    with pytest.raises(RejectedJobPosting):
        parse_job_posting_json_ld(_envelope_with(other))


def test_job_posting_missing_required_field_is_rejected():
    incomplete = dict(_VALID_JOB_POSTING)
    del incomplete["title"]
    with pytest.raises(RejectedJobPosting):
        parse_job_posting_json_ld(_envelope_with(incomplete))
