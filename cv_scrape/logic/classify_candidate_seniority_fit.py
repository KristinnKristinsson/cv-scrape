"""Logic: whether a posting's seniority bar is within the candidate's reach. A
different, coarser determination than classify_seniority.py's SeniorityTag, which
is tuned for market-wide tiering (fires at 3 years or any senior-ish word) — this
one exists specifically to tell apart an explicit Senior/Lead/Principal *title*
(candidate.yaml's job_evaluation_guidance treats that as a flat skip signal, no
hedging) from a stated *years* bar (candidate.yaml explicitly says not to
auto-reject on years alone: "evaluate the combination of required years,
responsibility level, central technology alignment and evidence strength").
SeniorityTag's single MID_OR_SENIOR bucket can't express that distinction without a
caller-selecting flag, so per the "same thing" test this is a separate piece, not a
reuse — same (JobPosting, years) input shape as classify_seniority deliberately, so
the pattern carries over even though the piece doesn't.
"""

from enum import Enum, auto

from cv_scrape.state.job_posting import JobPosting

_SENIOR_TITLE_MARKERS = ("senior", "lead", "principal", "erfaren", "expert", "head of")
_HIGH_YEARS_THRESHOLD = 5.0


class SeniorityFit(Enum):
    WITHIN_REACH = auto()
    SENIOR_TITLE = auto()
    HIGH_YEARS = auto()


def classify_candidate_seniority_fit(job: JobPosting, years_experience_required: float | None) -> SeniorityFit:
    title = job.title.lower()

    if any(marker in title for marker in _SENIOR_TITLE_MARKERS):
        return SeniorityFit.SENIOR_TITLE
    if years_experience_required is not None and years_experience_required >= _HIGH_YEARS_THRESHOLD:
        return SeniorityFit.HIGH_YEARS
    return SeniorityFit.WITHIN_REACH
