from cv_scrape.logic.detect_rate_limit_signal import RateLimitSignal
from cv_scrape.logic.summarize_rate_limit_signals import summarize_rate_limit_signals


def test_no_signals_means_no_rate_limit_seen():
    result = summarize_rate_limit_signals([])
    assert result.saw_rate_limit is False
    assert result.retry_after_seconds is None


def test_any_hit_marks_rate_limit_seen():
    signals = [RateLimitSignal(hit=False, retry_after_seconds=None), RateLimitSignal(hit=True, retry_after_seconds=10.0)]
    result = summarize_rate_limit_signals(signals)
    assert result.saw_rate_limit is True
    assert result.retry_after_seconds == 10.0
