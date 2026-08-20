"""Logic: [WAF] pick which rate-limit policy applies to a domain. See structure.md —
"Rate limiting". Not implemented yet — this is the extension point.

Picks a policy; does not advance any counter (that's effect/consume_rate_limit_token.py).
"""


def select_rate_limit_policy_for_domain(domain: str) -> tuple[float, float]:
    """Returns (tokens_per_second, bucket_capacity) for the domain."""
    raise NotImplementedError
