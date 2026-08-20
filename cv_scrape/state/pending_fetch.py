"""State: [WAF] reified retry value. See structure.md — "Backoff / retry".

Not implemented yet — this is the extension point. A pending retry is a value first;
logic/decide_retry_action.py decides what it becomes, effect/enqueue_pending_fetch.py
and observation/read_pending_fetches.py move it, flow/retry_pending_fetches.py drains it.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PendingFetch:
    url: str
    attempt: int
    not_before: float
    reason: str
