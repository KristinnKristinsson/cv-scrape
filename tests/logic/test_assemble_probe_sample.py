from cv_scrape.logic.assemble_probe_sample import assemble_probe_sample
from cv_scrape.observation.fetch_page_raw import RawFetchFailure, RawFetchResult
from cv_scrape.observation.fetch_page_rendered import RenderedFetchFailure, RenderedFetchResult
from cv_scrape.state.probe_sample import ProbeSample


def test_raw_success_carries_status_and_tag():
    result = RawFetchResult(url="https://example.com", status=200, headers={}, body=b"hi", elapsed_ms=12.5)

    sample = assemble_probe_sample("raw", result, "OK")

    assert sample == ProbeSample(
        url="https://example.com", renderer="raw", fetched=True, status=200, response_tag="OK", elapsed_ms=12.5, error=None
    )


def test_raw_failure_carries_reason_and_no_tag():
    result = RawFetchFailure(url="https://example.com", reason="connection reset")

    sample = assemble_probe_sample("raw", result, None)

    assert sample == ProbeSample(
        url="https://example.com",
        renderer="raw",
        fetched=False,
        status=None,
        response_tag=None,
        elapsed_ms=None,
        error="connection reset",
    )


def test_rendered_success_carries_status_and_tag():
    result = RenderedFetchResult(url="https://example.com", status=200, headers={}, body=b"hi", elapsed_ms=800.0)

    sample = assemble_probe_sample("rendered", result, "CHALLENGE")

    assert sample == ProbeSample(
        url="https://example.com",
        renderer="rendered",
        fetched=True,
        status=200,
        response_tag="CHALLENGE",
        elapsed_ms=800.0,
        error=None,
    )


def test_rendered_failure_carries_reason():
    result = RenderedFetchFailure(url="https://example.com", reason="navigation timeout")

    sample = assemble_probe_sample("rendered", result, None)

    assert sample == ProbeSample(
        url="https://example.com",
        renderer="rendered",
        fetched=False,
        status=None,
        response_tag=None,
        elapsed_ms=None,
        error="navigation timeout",
    )
