from cv_scrape.logic.classify_response import ResponseTag, classify_response
from cv_scrape.state.response_envelope import ResponseEnvelope


def test_ok_status_is_ok():
    envelope = ResponseEnvelope(url="https://example.com", status=200, headers={}, body=b"<html>hello</html>")
    assert classify_response(envelope) is ResponseTag.OK


def test_challenge_marker_in_body_is_challenge():
    envelope = ResponseEnvelope(
        url="https://example.com", status=200, headers={}, body=b"<html>Just a moment...</html>"
    )
    assert classify_response(envelope) is ResponseTag.CHALLENGE


def test_429_is_challenge():
    envelope = ResponseEnvelope(url="https://example.com", status=429, headers={}, body=b"")
    assert classify_response(envelope) is ResponseTag.CHALLENGE


def test_403_is_blocked():
    envelope = ResponseEnvelope(url="https://example.com", status=403, headers={}, body=b"")
    assert classify_response(envelope) is ResponseTag.BLOCKED


def test_500_is_unknown():
    envelope = ResponseEnvelope(url="https://example.com", status=500, headers={}, body=b"")
    assert classify_response(envelope) is ResponseTag.UNKNOWN
