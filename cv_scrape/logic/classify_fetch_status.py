"""Logic: decide whether a fetched HTTP status code represents a usable response
body. Pure decision over a status code already in hand — no fetch happens here,
that's observation/fetch_page_raw.py.
"""

from enum import Enum, auto


class FetchStatusOutcome(Enum):
    OK = auto()
    FAILED = auto()


def classify_fetch_status(status: int) -> FetchStatusOutcome:
    return FetchStatusOutcome.OK if status == 200 else FetchStatusOutcome.FAILED
