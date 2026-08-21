"""State: signals inferred from a job posting's text — the "how does this posting
actually read" companion to the read fields already on JobPosting (see
Objectives.md's read-fields-vs-inferred-fields split). Produced by the
logic/classify_*.py and logic/*_mentioned.py/*_required.py pieces, assembled by
flow/extract_job_signals.py, same shape as state/site_profile.py assembling probe
logic's outputs. Tag fields hold each producing Enum's `.name`, mirroring
SiteProfile's convention for logic-produced tags.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TechnologyRequirement:
    """One technology mentioned in a posting, paired with how strongly it's
    required — the pairing classify_technology_requirement_strength produces per
    already-matched technology name. A component of JobSignals, not a freestanding
    record, so it lives here rather than in its own file.
    """

    technology: str
    strength: str


@dataclass(frozen=True)
class JobSignals:
    job_url: str
    role_family: str
    seniority: str
    language_requirement: str
    education_requirement: str
    company_type: str
    technologies: tuple[TechnologyRequirement, ...] = ()
    cloud_platforms: tuple[str, ...] = ()
    years_experience_required: float | None = None
    salary_mentioned: str | None = None
