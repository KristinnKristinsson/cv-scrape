"""Observation: [WAF] read our own stored cookies for a domain, unchanged. See
structure.md — "Cookie/session continuity". Not implemented yet — this is the
extension point. Ownership doesn't decide the category, only whether the call changes
anything — reading is observation, storing is effect/update_session_state.py.
"""

from cv_scrape.state.session import SessionState


def read_session_state(domain: str) -> SessionState | None:
    raise NotImplementedError
