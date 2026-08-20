"""Interaction: [WAF] boundary for raw bytes from an external site. See structure.md.

Not implemented yet — this is the extension point. Guards against malformed/undecodable
responses generically — the same piece serves challenge pages and real pages (one piece
per the "same thing" rule); classify_response.py decides which is which afterward.
"""

from cv_scrape.state.response_envelope import ResponseEnvelope


class RejectedResponse(Exception):
    """Raised when raw response bytes cannot be normalized into a trustworthy envelope."""


def receive_fetch_response(url: str, status: int, headers: dict[str, str], body: bytes) -> ResponseEnvelope:
    raise NotImplementedError
