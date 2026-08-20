"""Effect: [WAF] ATOMIC check-and-decrement of our own token bucket. See structure.md —
"Rate limiting" and Ambiguous call #4 (Atomicity: must not split into observation+effect,
that opens a stale-check race). Not implemented yet — this is the extension point.
"""


def consume_rate_limit_token(domain: str) -> bool:
    """Returns True if a token was available and consumed, False otherwise."""
    raise NotImplementedError
