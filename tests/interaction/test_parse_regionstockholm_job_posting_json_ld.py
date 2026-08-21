import json

import pytest

from cv_scrape.interaction.parse_job_posting_html import RejectedJobPosting
from cv_scrape.interaction.parse_regionstockholm_job_posting_json_ld import parse_regionstockholm_job_posting_json_ld
from cv_scrape.state.response_envelope import ResponseEnvelope

_DETAIL_URL = "https://www.regionstockholm.se/jobb/lediga-jobb/trafikforvaltningen/projektledare-till-tunnelbanan/"

# The site's own JSON-LD bug: `title` is always the listing category label, never the
# real job title (confirmed live on five detail pages across three organizations) --
# the real title only lives in the page's <h1>.
_VALID_JOB_POSTING = {
    "@context": "https://schema.org",
    "@type": "JobPosting",
    "datePosted": "2026-08-16T22:00:00Z",
    "description": "<p>Vill du <strong>utveckla</strong> kollektivtrafiken &amp; mer?</p>",
    "title": "Administration, HR, ekonomi, juridik, IT",
    "hiringOrganization": {"@type": "Organization", "name": "Trafikförvaltningen"},
    "jobLocation": "Stockholm",
}

_H1 = "<h1>Projektledare till tunnelbanan</h1>"


def _envelope_with(job_posting: dict, h1: str = _H1) -> ResponseEnvelope:
    body = (
        f'<html><head><script type="application/ld+json">{json.dumps(job_posting)}</script></head>'
        f"<body>{h1}</body></html>"
    ).encode()
    return ResponseEnvelope(url=_DETAIL_URL, status=200, headers={}, body=body)


def test_valid_job_posting_is_parsed_with_title_from_h1_not_json_ld():
    posting = parse_regionstockholm_job_posting_json_ld(_envelope_with(_VALID_JOB_POSTING))
    assert posting.url == _DETAIL_URL
    assert posting.source_domain == "www.regionstockholm.se"
    assert posting.title == "Projektledare till tunnelbanan"
    assert posting.company == "Trafikförvaltningen"
    assert posting.location == "Stockholm"
    assert posting.posted_at == "2026-08-16T22:00:00Z"


def test_description_html_is_stripped_and_unescaped():
    posting = parse_regionstockholm_job_posting_json_ld(_envelope_with(_VALID_JOB_POSTING))
    assert posting.description == "Vill du utveckla kollektivtrafiken & mer?"


def test_missing_json_ld_block_is_rejected():
    envelope = ResponseEnvelope(url=_DETAIL_URL, status=200, headers={}, body=f"<html><body>{_H1}</body></html>".encode())
    with pytest.raises(RejectedJobPosting):
        parse_regionstockholm_job_posting_json_ld(envelope)


def test_missing_h1_is_rejected():
    body = f'<html><head><script type="application/ld+json">{json.dumps(_VALID_JOB_POSTING)}</script></head><body></body></html>'.encode()
    envelope = ResponseEnvelope(url=_DETAIL_URL, status=200, headers={}, body=body)
    with pytest.raises(RejectedJobPosting):
        parse_regionstockholm_job_posting_json_ld(envelope)


def test_non_job_posting_json_ld_is_rejected():
    other = {"@context": "https://schema.org", "@type": "WebSite", "name": "regionstockholm.se"}
    with pytest.raises(RejectedJobPosting):
        parse_regionstockholm_job_posting_json_ld(_envelope_with(other))


def test_missing_company_is_rejected():
    incomplete = dict(_VALID_JOB_POSTING)
    del incomplete["hiringOrganization"]
    with pytest.raises(RejectedJobPosting):
        parse_regionstockholm_job_posting_json_ld(_envelope_with(incomplete))
