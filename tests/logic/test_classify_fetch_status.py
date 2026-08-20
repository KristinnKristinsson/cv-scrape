from cv_scrape.logic.classify_fetch_status import FetchStatusOutcome, classify_fetch_status


def test_200_is_ok():
    assert classify_fetch_status(200) is FetchStatusOutcome.OK


def test_non_200_is_failed():
    assert classify_fetch_status(404) is FetchStatusOutcome.FAILED
    assert classify_fetch_status(500) is FetchStatusOutcome.FAILED
    assert classify_fetch_status(301) is FetchStatusOutcome.FAILED
