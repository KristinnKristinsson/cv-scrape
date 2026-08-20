"""State: what a robots.txt evaluation determined for one target path. Produced by
logic/evaluate_robots_txt.py, folded into a SiteProfile.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RobotsEvaluation:
    fetched: bool
    allowed: bool
    crawl_delay: float | None
