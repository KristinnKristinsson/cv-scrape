from cv_scrape.logic.detect_framework_signals import detect_framework_signals
from cv_scrape.state.response_envelope import ResponseEnvelope


def test_generator_meta_tag_extracted():
    body = b'<html><head><meta name="generator" content="WordPress 6.4"></head></html>'
    envelope = ResponseEnvelope(url="https://example.com", status=200, headers={}, body=body)
    signals = detect_framework_signals(envelope)
    assert signals.generator == "WordPress 6.4"


def test_wordpress_markers_matched():
    body = b'<html><script src="/wp-content/theme.js"></script></html>'
    envelope = ResponseEnvelope(url="https://example.com", status=200, headers={}, body=body)
    signals = detect_framework_signals(envelope)
    assert "wordpress" in signals.matched_markers


def test_powered_by_and_server_headers_captured():
    envelope = ResponseEnvelope(
        url="https://example.com",
        status=200,
        headers={"X-Powered-By": "Express", "Server": "nginx"},
        body=b"<html></html>",
    )
    signals = detect_framework_signals(envelope)
    assert signals.powered_by == "Express"
    assert signals.server == "nginx"
    assert signals.generator is None
    assert signals.matched_markers == ()
