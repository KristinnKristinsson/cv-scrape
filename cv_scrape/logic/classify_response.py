"""Logic: classify an already-fetched envelope. See structure.md — "Challenge-page
detection".

Pure decision over a ResponseEnvelope already in hand -> a tag the flow routes on.
"""

from enum import Enum, auto

from cv_scrape.state.response_envelope import ResponseEnvelope


class ResponseTag(Enum):
    OK = auto()
    CHALLENGE = auto()
    BLOCKED = auto()
    UNKNOWN = auto()


_CHALLENGE_MARKERS = (
    "just a moment",
    "checking your browser",
    "verify you are a human",
    "verify you are human",
    "captcha",
    "please enable javascript and cookies",
    "ddos protection by",
    "cf-chl",
    "px-captcha",
    "attention required",
)

_BLOCK_MARKERS = (
    "access denied",
    "you have been blocked",
    "ip address has been blocked",
    "request blocked",
)


def classify_response(envelope: ResponseEnvelope) -> ResponseTag:
    body_text = envelope.body.decode("utf-8", errors="ignore").lower()

    if any(marker in body_text for marker in _CHALLENGE_MARKERS) or envelope.status == 429:
        return ResponseTag.CHALLENGE
    if envelope.status in (401, 403) or any(marker in body_text for marker in _BLOCK_MARKERS):
        return ResponseTag.BLOCKED
    if 200 <= envelope.status < 300:
        return ResponseTag.OK
    return ResponseTag.UNKNOWN
