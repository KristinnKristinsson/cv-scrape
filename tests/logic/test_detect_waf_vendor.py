from cv_scrape.logic.detect_waf_vendor import WafVendor, detect_waf_vendor
from cv_scrape.state.response_envelope import ResponseEnvelope


def test_cloudflare_ray_header_detected():
    envelope = ResponseEnvelope(url="https://example.com", status=200, headers={"CF-RAY": "abc123"}, body=b"")
    assert detect_waf_vendor(envelope) is WafVendor.CLOUDFLARE


def test_datadome_cookie_detected():
    envelope = ResponseEnvelope(
        url="https://example.com", status=200, headers={"Set-Cookie": "datadome=xyz; Path=/"}, body=b""
    )
    assert detect_waf_vendor(envelope) is WafVendor.DATADOME


def test_imperva_cookie_detected():
    envelope = ResponseEnvelope(
        url="https://example.com", status=200, headers={"Set-Cookie": "incap_ses_123=xyz; Path=/"}, body=b""
    )
    assert detect_waf_vendor(envelope) is WafVendor.IMPERVA


def test_no_signatures_and_ok_status_is_none():
    envelope = ResponseEnvelope(url="https://example.com", status=200, headers={}, body=b"<html></html>")
    assert detect_waf_vendor(envelope) is WafVendor.NONE


def test_suspicious_status_without_signature_is_unknown():
    envelope = ResponseEnvelope(url="https://example.com", status=503, headers={}, body=b"")
    assert detect_waf_vendor(envelope) is WafVendor.UNKNOWN
