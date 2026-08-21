"""State: the outcome of evaluating one job posting against the candidate's
capability profile — produced by logic/evaluate_candidate_against_job.py, assembled
from state/capability_overlap.py plus the seniority-fit determination. Tag field
holds the producing Enum's `.name`, mirroring JobSignals' convention.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateFitEvaluation:
    job_url: str
    role_family: str
    recommendation: str
    strong_matches: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    partial_matches: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
