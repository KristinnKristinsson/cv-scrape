"""Logic: reduce a probe's per-request rate-limit signals into one summary. Pure
decision over values already in hand.
"""

from cv_scrape.logic.detect_rate_limit_signal import RateLimitSignal
from cv_scrape.state.rate_limit_findings import RateLimitFindings


def summarize_rate_limit_signals(signals: list[RateLimitSignal]) -> RateLimitFindings:
    hits = [signal for signal in signals if signal.hit]
    retry_after = next((signal.retry_after_seconds for signal in hits if signal.retry_after_seconds is not None), None)
    return RateLimitFindings(saw_rate_limit=bool(hits), retry_after_seconds=retry_after)
