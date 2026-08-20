"""State: framework/CMS hints read off a single response. Produced by
logic/detect_framework_signals.py, folded into a SiteProfile.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FrameworkSignals:
    generator: str | None
    powered_by: str | None
    server: str | None
    matched_markers: tuple[str, ...] = ()
