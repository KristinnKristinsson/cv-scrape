"""Interaction: boundary for raw bytes from an external site. See structure.md.

Guards against malformed/undecodable responses generically — the same piece serves
challenge pages and real pages (one piece per the "same thing" rule);
classify_response.py decides which is which afterward. First real caller is
flow/probe_site.py; the runtime WAF path (spiders/middlewares) gets this for free.
"""

from cv_scrape.state.response_envelope import ResponseEnvelope


class RejectedResponse(Exception):
    """Raised when raw response bytes cannot be normalized into a trustworthy envelope."""


def receive_fetch_response(url: str, status: int, headers: dict[str, str], body: bytes) -> ResponseEnvelope:
    if not (100 <= status <= 599):
        raise RejectedResponse(f"{url}: status {status} is not a valid HTTP status code")

    try:
        body.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise RejectedResponse(f"{url}: body is not valid UTF-8 text") from exc

    return ResponseEnvelope(url=url, status=status, headers=headers, body=body)
