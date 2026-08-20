"""State: rate-limit signals observed across a probe's sample of requests."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitFindings:
    saw_rate_limit: bool
    retry_after_seconds: float | None
