"""State: static per-domain configuration. Consumed by logic, never decided by it."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SitePolicy:
    domain: str
    listing_selector: str
    title_selector: str
    company_selector: str
    description_selector: str
