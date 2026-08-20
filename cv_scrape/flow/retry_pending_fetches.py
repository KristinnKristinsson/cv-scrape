"""Flow: [WAF] drains the pending-retry queue, routing on decide_retry_action's tag.
See structure.md — "Backoff / retry". Not implemented yet — this is the extension point.
"""


def retry_pending_fetches() -> None:
    raise NotImplementedError
