"""State: the outcome of scoring a job posting against the CV."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchScore:
    job_url: str
    score: float
    reasons: tuple[str, ...] = ()
