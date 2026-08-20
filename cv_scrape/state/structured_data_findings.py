"""State: structured-data/API discovery findings read off a single response. Produced
by logic/discover_structured_data.py, folded into a SiteProfile.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StructuredDataFindings:
    has_json_ld: bool
    json_ld_types: tuple[str, ...] = ()
    feed_links: tuple[str, ...] = ()
    sitemap_hints: tuple[str, ...] = ()
    api_hints: tuple[str, ...] = ()
