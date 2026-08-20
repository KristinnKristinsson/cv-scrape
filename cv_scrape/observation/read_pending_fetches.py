"""Observation: [WAF] peek the retry queue, unchanged. See structure.md —
"Backoff / retry". Not implemented yet — this is the extension point.
"""

from cv_scrape.state.pending_fetch import PendingFetch


def read_pending_fetches() -> list[PendingFetch]:
    raise NotImplementedError
