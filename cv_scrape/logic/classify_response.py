"""Logic: [WAF] classify an already-fetched envelope. See structure.md — "Challenge-page
detection". Not implemented yet — this is the extension point.

Pure decision over a ResponseEnvelope already in hand -> a tag the flow routes on.
"""

from enum import Enum, auto

from cv_scrape.state.response_envelope import ResponseEnvelope


class ResponseTag(Enum):
    OK = auto()
    CHALLENGE = auto()
    BLOCKED = auto()
    UNKNOWN = auto()


def classify_response(envelope: ResponseEnvelope) -> ResponseTag:
    raise NotImplementedError
