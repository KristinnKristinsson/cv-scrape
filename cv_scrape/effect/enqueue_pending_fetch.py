"""Effect: [WAF] push a PendingFetch onto our retry queue. See structure.md —
"Backoff / retry". Not implemented yet — this is the extension point.
"""

from cv_scrape.state.pending_fetch import PendingFetch


def enqueue_pending_fetch(pending: PendingFetch) -> None:
    raise NotImplementedError
