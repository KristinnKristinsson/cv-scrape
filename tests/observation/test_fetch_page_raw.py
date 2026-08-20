"""No real network calls — pytest-httpx intercepts httpx's transport."""

import httpx

from cv_scrape.observation.fetch_page_raw import RawFetchFailure, RawFetchResult, fetch_page_raw


def test_successful_fetch_returns_result(httpx_mock):
    httpx_mock.add_response(url="https://example.com/jobs", status_code=200, text="<html>jobs</html>")

    result = fetch_page_raw("https://example.com/jobs")

    assert isinstance(result, RawFetchResult)
    assert result.status == 200
    assert result.body == b"<html>jobs</html>"


def test_connection_error_returns_failure(httpx_mock):
    httpx_mock.add_exception(httpx.ConnectError("connection refused"))

    result = fetch_page_raw("https://example.com/jobs")

    assert isinstance(result, RawFetchFailure)
    assert "connection refused" in result.reason
