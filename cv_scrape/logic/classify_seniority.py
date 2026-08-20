"""Logic: whether a posting actually reads as junior-friendly, regardless of its
title — Objectives.md step 3's "whether the job actually looks junior despite its
title." Takes the JobPosting already in hand plus the years-of-experience figure
logic/extract_years_experience_required.py already computed, per Behavioral
Architecture.md's flow-routes-on-already-returned-determinations pattern rather
than re-deriving it here.
"""

from enum import Enum, auto

from cv_scrape.state.job_posting import JobPosting


class SeniorityTag(Enum):
    JUNIOR_FRIENDLY = auto()
    MID_OR_SENIOR = auto()
    UNCLEAR = auto()


_JUNIOR_MARKERS = ("junior", "entry level", "entry-level", "nyexaminerad", "trainee", "graduate")
_SENIOR_MARKERS = ("senior", "lead ", "principal", "erfaren", "expert")
_SIGNIFICANT_EXPERIENCE_YEARS = 3


def classify_seniority(job: JobPosting, years_experience_required: float | None) -> SeniorityTag:
    text = f"{job.title}\n{job.description}".lower()

    has_junior_marker = any(marker in text for marker in _JUNIOR_MARKERS)
    has_senior_marker = any(marker in text for marker in _SENIOR_MARKERS)
    requires_significant_experience = (
        years_experience_required is not None and years_experience_required >= _SIGNIFICANT_EXPERIENCE_YEARS
    )

    if has_senior_marker or requires_significant_experience:
        return SeniorityTag.MID_OR_SENIOR
    if has_junior_marker:
        return SeniorityTag.JUNIOR_FRIENDLY
    return SeniorityTag.UNCLEAR
