from cv_scrape.logic.discover_structured_data import discover_structured_data
from cv_scrape.state.response_envelope import ResponseEnvelope


def test_json_ld_job_posting_detected():
    body = b"""
    <html><head>
    <script type="application/ld+json">{"@type": "JobPosting", "title": "Engineer"}</script>
    </head></html>
    """
    envelope = ResponseEnvelope(url="https://example.com", status=200, headers={}, body=body)
    findings = discover_structured_data(envelope)
    assert findings.has_json_ld is True
    assert "JobPosting" in findings.json_ld_types


def test_rss_feed_link_detected():
    body = b'<link rel="alternate" type="application/rss+xml" href="/feed.xml">'
    envelope = ResponseEnvelope(url="https://example.com", status=200, headers={}, body=body)
    findings = discover_structured_data(envelope)
    assert "/feed.xml" in findings.feed_links


def test_no_structured_data_gives_empty_findings():
    envelope = ResponseEnvelope(url="https://example.com", status=200, headers={}, body=b"<html></html>")
    findings = discover_structured_data(envelope)
    assert findings.has_json_ld is False
    assert findings.json_ld_types == ()
    assert findings.feed_links == ()
    assert findings.api_hints == ()
