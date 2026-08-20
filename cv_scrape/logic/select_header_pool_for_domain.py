"""Logic: [WAF] pick which header/UA pool applies to a domain. See structure.md —
"UA/header rotation". Not implemented yet — this is the extension point.

Picks a pool; does not advance the rotation index (that's effect/rotate_header_selection.py).
"""


def select_header_pool_for_domain(domain: str) -> tuple[dict[str, str], ...]:
    raise NotImplementedError
