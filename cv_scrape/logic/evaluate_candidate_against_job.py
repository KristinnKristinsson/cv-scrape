"""Logic: the final placement decision — formalizes the mechanical rule
candidate.yaml's own job_evaluation_guidance section already describes in prose,
and which two prior hand/scratch-script passes (Candidate Placement Findings.md)
independently reimplemented and validated against the curated posting sample. Pure
decision over already-derived values: a CapabilityOverlap
(summarize_capability_overlap.py) and a SeniorityFit
(classify_candidate_seniority_fit.py), same "value already in hand" shape as the
rest of this project's logic pieces.

The base table fills two gaps both prior passes' prose rule left undefined (strong
count of 0, and strong>=2 with blockers>=3) rather than leaving them as fallthrough
accidents of code order.

SeniorityFit then adjusts the base result, deliberately asymmetrically per
candidate.yaml's own text: SENIOR_TITLE is a flat, unconditional skip signal there
("Senior/Lead/Principal ownership"), so it overrides the base result outright.
HIGH_YEARS is explicitly *not* meant to auto-reject on its own ("do not
automatically reject a vacancy because stated years exceed the candidate's
chronological experience... evaluate the combination") — both prior scratch passes
got this wrong with a hard years>=5 cutoff, so here it only demotes the base result
by one tier instead of overriding it.
"""

from enum import Enum, auto

from cv_scrape.logic.classify_candidate_seniority_fit import SeniorityFit
from cv_scrape.state.candidate_fit_evaluation import CandidateFitEvaluation
from cv_scrape.state.capability_overlap import CapabilityOverlap
from cv_scrape.state.job_signals import JobSignals


class Recommendation(Enum):
    APPLY = auto()
    APPLY_STRETCH = auto()
    LOW_PRIORITY = auto()
    SKIP = auto()


_DEMOTE = {
    Recommendation.APPLY: Recommendation.APPLY_STRETCH,
    Recommendation.APPLY_STRETCH: Recommendation.LOW_PRIORITY,
    Recommendation.LOW_PRIORITY: Recommendation.SKIP,
    Recommendation.SKIP: Recommendation.SKIP,
}


def _base_recommendation(strong: int, blockers: int) -> Recommendation:
    if strong == 0:
        return Recommendation.SKIP
    if strong == 1:
        return Recommendation.SKIP if blockers >= 3 else Recommendation.LOW_PRIORITY
    if blockers == 0:
        return Recommendation.APPLY
    if blockers <= 2:
        return Recommendation.APPLY_STRETCH
    return Recommendation.LOW_PRIORITY


def evaluate_candidate_against_job(
    job_signals: JobSignals, overlap: CapabilityOverlap, seniority_fit: SeniorityFit
) -> CandidateFitEvaluation:
    recommendation = _base_recommendation(len(overlap.strong_matches), len(overlap.blockers))

    reasons = []
    if overlap.strong_matches:
        reasons.append(f"Strong-evidence overlap: {', '.join(overlap.strong_matches)}")
    if overlap.blockers:
        reasons.append(f"Zero-evidence blockers (required/preferred): {', '.join(overlap.blockers)}")
    if overlap.partial_matches:
        reasons.append(f"Partial-evidence overlap: {', '.join(overlap.partial_matches)}")

    if seniority_fit is SeniorityFit.SENIOR_TITLE:
        recommendation = Recommendation.SKIP
        reasons.append("Title reads as Senior/Lead/Principal")
    elif seniority_fit is SeniorityFit.HIGH_YEARS:
        demoted = _DEMOTE[recommendation]
        if demoted is not recommendation:
            reasons.append(f"Demoted from {recommendation.name} — years requirement is high, evaluated in combination")
        recommendation = demoted

    return CandidateFitEvaluation(
        job_url=job_signals.job_url,
        role_family=job_signals.role_family,
        recommendation=recommendation.name,
        strong_matches=overlap.strong_matches,
        blockers=overlap.blockers,
        partial_matches=overlap.partial_matches,
        reasons=tuple(reasons),
    )
