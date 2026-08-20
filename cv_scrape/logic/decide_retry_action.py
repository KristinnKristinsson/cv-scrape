"""Logic: [WAF] decide what a pending retry becomes. See structure.md — "Backoff / retry".
Not implemented yet — this is the extension point.

Pure decision over a PendingFetch and the current time, both already in hand -> a tag
the flow routes on.
"""

from enum import Enum, auto

from cv_scrape.state.pending_fetch import PendingFetch


class RetryAction(Enum):
    RETRY_NOW = auto()
    WAIT = auto()
    ABANDON = auto()


def decide_retry_action(pending: PendingFetch, now: float) -> RetryAction:
    raise NotImplementedError
