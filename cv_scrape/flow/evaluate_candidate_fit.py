"""Flow: CLI-triggered. Sequences interaction -> observation -> logic -> effect over
the curated, deduped posting sample. No decision, no mutation of its own.

Scoped to role_family != "UNMATCHED" and deduplicated via
logic/deduplicate_job_postings.py — the same curated sample
Candidate Placement Findings.md's two hand/scratch-script passes evaluated, per
Objectives.md's own step 2 finding that UNMATCHED rows are "noise... not part of the
sample." This is also deduplicate_job_postings.py's first real flow caller —
Objectives.md flagged it as built but never wired in past a one-off scratch script.
"""

from cv_scrape.effect.save_candidate_fit_evaluation import save_candidate_fit_evaluation
from cv_scrape.interaction.parse_candidate_profile import RejectedCandidateProfile, parse_candidate_profile
from cv_scrape.logic.classify_candidate_seniority_fit import classify_candidate_seniority_fit
from cv_scrape.logic.deduplicate_job_postings import deduplicate_job_postings
from cv_scrape.logic.evaluate_candidate_against_job import evaluate_candidate_against_job
from cv_scrape.logic.summarize_capability_overlap import summarize_capability_overlap
from cv_scrape.observation.read_stored_job_signals import read_stored_job_signals
from cv_scrape.observation.read_stored_jobs import read_stored_jobs
from cv_scrape.state.candidate_fit_evaluation import CandidateFitEvaluation


def evaluate_candidate_fit() -> list[CandidateFitEvaluation]:
    try:
        profile = parse_candidate_profile()
    except RejectedCandidateProfile as exc:
        raise RuntimeError(f"No usable candidate profile: {exc}") from exc

    signals_by_url = {
        signals.job_url: signals for signals in read_stored_job_signals() if signals.role_family != "UNMATCHED"
    }
    curated_postings = [job for job in read_stored_jobs() if job.url in signals_by_url]
    deduped_postings = deduplicate_job_postings(curated_postings)

    evaluations = []
    for job in deduped_postings:
        signals = signals_by_url[job.url]
        overlap = summarize_capability_overlap(signals, profile)
        seniority_fit = classify_candidate_seniority_fit(job, signals.years_experience_required)
        evaluation = evaluate_candidate_against_job(signals, overlap, seniority_fit)
        save_candidate_fit_evaluation(evaluation)
        evaluations.append(evaluation)

    return evaluations
