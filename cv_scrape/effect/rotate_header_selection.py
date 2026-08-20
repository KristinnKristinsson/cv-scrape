"""Effect: [WAF] ATOMIC get-next-and-advance of our own rotation index. See structure.md
— "UA/header rotation" and Ambiguous call #4. Not implemented yet — this is the
extension point.
"""


def rotate_header_selection(domain: str) -> dict[str, str]:
    """Returns the next header set and advances our own rotation index."""
    raise NotImplementedError
