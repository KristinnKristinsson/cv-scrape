from cv_scrape.logic.detect_rate_limit_signal import detect_rate_limit_signal


def test_429_status_is_a_hit():
    signal = detect_rate_limit_signal(429, {})
    assert signal.hit is True


def test_retry_after_header_is_a_hit_and_parsed():
    signal = detect_rate_limit_signal(200, {"Retry-After": "30"})
    assert signal.hit is True
    assert signal.retry_after_seconds == 30.0


def test_ok_status_with_no_header_is_not_a_hit():
    signal = detect_rate_limit_signal(200, {})
    assert signal.hit is False
    assert signal.retry_after_seconds is None


def test_non_numeric_retry_after_is_ignored_but_still_a_hit():
    signal = detect_rate_limit_signal(200, {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"})
    assert signal.hit is True
    assert signal.retry_after_seconds is None
