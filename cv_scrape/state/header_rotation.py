"""State: [WAF] UA/header rotation pool. See structure.md — "UA/header rotation".

Not implemented yet — this is the extension point.
"""

from dataclasses import dataclass, field


@dataclass
class HeaderRotationState:
    pool: tuple[dict[str, str], ...] = field(default_factory=tuple)
    current_index: int = 0
