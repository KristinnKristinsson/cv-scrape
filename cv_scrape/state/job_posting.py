"""State: a scraped job posting. Defined by what it is, not by who touches it."""

from dataclasses import dataclass


@dataclass(frozen=True)
class JobPosting:
    url: str
    source_domain: str
    title: str
    company: str
    description: str
    location: str | None = None
    posted_at: str | None = None
