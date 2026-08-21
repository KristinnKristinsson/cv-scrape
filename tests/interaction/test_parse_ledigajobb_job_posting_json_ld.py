import json

import pytest

from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.interaction.parse_ledigajobb_job_posting_json_ld import parse_ledigajobb_job_posting_json_ld
from cv_scrape.state.response_envelope import ResponseEnvelope

_VALID_JOB_POSTING = {
    "@context": "https://schema.org",
    "@type": "JobPosting",
    "datePosted": "2026-08-12T12:20:59.336+01:00",
    "description": "<p>Mekaniker</p><p>Vi s&ouml;ker en mekaniker &amp; till v&aring;rt team.</p>",
    "title": "Mekaniker",
    "hiringOrganization": {"@type": "Organization", "name": "Malte Månson Verkstäder AB"},
    "jobLocation": {
        "@type": "Place",
        "address": {"@type": "PostalAddress", "addressCountry": "Sverige", "addressLocality": "Kalmar", "addressRegion": "Kalmar län"},
    },
}


def _envelope_with(job_posting: dict) -> ResponseEnvelope:
    body = f'<html><head><script type="application/ld+json">{json.dumps(job_posting)}</script></head></html>'.encode()
    return ResponseEnvelope(url="https://ledigajobb.se/jobb/cb9cca/mekaniker", status=200, headers={}, body=body)


def test_valid_job_posting_json_ld_is_parsed():
    posting = parse_ledigajobb_job_posting_json_ld(_envelope_with(_VALID_JOB_POSTING))
    assert posting.url == "https://ledigajobb.se/jobb/cb9cca/mekaniker"
    assert posting.source_domain == "ledigajobb.se"
    assert posting.title == "Mekaniker"
    assert posting.company == "Malte Månson Verkstäder AB"
    assert posting.location == "Kalmar"
    assert posting.posted_at == "2026-08-12T12:20:59.336+01:00"


def test_description_html_is_stripped_and_unescaped():
    posting = parse_ledigajobb_job_posting_json_ld(_envelope_with(_VALID_JOB_POSTING))
    assert posting.description == "Mekaniker Vi söker en mekaniker & till vårt team."


def test_missing_json_ld_block_is_rejected():
    envelope = ResponseEnvelope(url="https://ledigajobb.se/jobb/x", status=200, headers={}, body=b"<html></html>")
    with pytest.raises(RejectedJobPosting):
        parse_ledigajobb_job_posting_json_ld(envelope)


def test_non_job_posting_json_ld_is_rejected():
    other = {"@context": "https://schema.org", "@type": "WebSite", "name": "ledigajobb.se"}
    with pytest.raises(RejectedJobPosting):
        parse_ledigajobb_job_posting_json_ld(_envelope_with(other))


def test_job_posting_missing_required_field_is_rejected():
    incomplete = dict(_VALID_JOB_POSTING)
    del incomplete["title"]
    with pytest.raises(RejectedJobPosting):
        parse_ledigajobb_job_posting_json_ld(_envelope_with(incomplete))
