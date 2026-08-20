"""State: [WAF] per-domain cookie/session continuity. See structure.md — "Cookie/session continuity".

Not implemented yet — this is the extension point.
"""

from dataclasses import dataclass, field


@dataclass
class SessionState:
    domain: str
    cookies: dict[str, str] = field(default_factory=dict)
    last_used_headers: dict[str, str] = field(default_factory=dict)
