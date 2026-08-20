import pytest

from cv_scrape.interaction.receive_fetch_response import RejectedResponse, receive_fetch_response


def test_valid_response_becomes_envelope():
    envelope = receive_fetch_response("https://example.com", 200, {"Content-Type": "text/html"}, b"<html></html>")
    assert envelope.url == "https://example.com"
    assert envelope.status == 200
    assert envelope.body == b"<html></html>"


def test_invalid_status_code_is_rejected():
    with pytest.raises(RejectedResponse):
        receive_fetch_response("https://example.com", 999, {}, b"")


def test_undecodable_body_is_rejected():
    with pytest.raises(RejectedResponse):
        receive_fetch_response("https://example.com", 200, {}, b"\xff\xfe\x00\x01")
