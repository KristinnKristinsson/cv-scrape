"""State: a normalized fetch outcome. [WAF] extension point — see structure.md.

Produced by interaction/receive_fetch_response.py, consumed by logic/classify_response.py.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResponseEnvelope:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes
