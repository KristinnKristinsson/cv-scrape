"""Effect: [WAF] store newly-received cookies into our own jar. See structure.md —
"Cookie/session continuity". Not implemented yet — this is the extension point.
"""

from cv_scrape.state.session import SessionState


def update_session_state(domain: str, new_cookies: dict[str, str]) -> SessionState:
    raise NotImplementedError
