"""Logic: pull a rate-limit signal off one already-fetched raw result. Pure decision
over a status code and headers already in hand.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitSignal:
    hit: bool
    retry_after_seconds: float | None


def detect_rate_limit_signal(status: int, headers: dict[str, str]) -> RateLimitSignal:
    lowered = {k.lower(): v for k, v in headers.items()}
    retry_after = lowered.get("retry-after")

    retry_after_seconds = None
    if retry_after is not None:
        try:
            retry_after_seconds = float(retry_after)
        except ValueError:
            retry_after_seconds = None

    return RateLimitSignal(hit=status == 429 or retry_after is not None, retry_after_seconds=retry_after_seconds)
