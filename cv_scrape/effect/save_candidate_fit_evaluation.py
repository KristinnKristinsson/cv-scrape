"""Effect: convergent upsert — safe to repeat."""

import json

from cv_scrape.state.candidate_fit_evaluation import CandidateFitEvaluation
from cv_scrape.state.store import connect


def save_candidate_fit_evaluation(evaluation: CandidateFitEvaluation) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO candidate_fit_evaluation (
                job_url, role_family, recommendation, strong_matches, blockers, partial_matches, reasons
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_url) DO UPDATE SET
                role_family=excluded.role_family,
                recommendation=excluded.recommendation,
                strong_matches=excluded.strong_matches,
                blockers=excluded.blockers,
                partial_matches=excluded.partial_matches,
                reasons=excluded.reasons
            """,
            (
                evaluation.job_url,
                evaluation.role_family,
                evaluation.recommendation,
                json.dumps(evaluation.strong_matches),
                json.dumps(evaluation.blockers),
                json.dumps(evaluation.partial_matches),
                json.dumps(evaluation.reasons),
            ),
        )
