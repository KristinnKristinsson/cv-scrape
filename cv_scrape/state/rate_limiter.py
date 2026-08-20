"""State: [WAF] per-domain rate-limit token bucket. See structure.md — "Rate limiting".

Not implemented yet — this is the extension point.
"""

from dataclasses import dataclass


@dataclass
class RateLimiterState:
    domain: str
    tokens: float
    last_refill: float
