"""Observation: read-only query against the persisted store."""

import json

from cv_scrape.state.candidate_fit_evaluation import CandidateFitEvaluation
from cv_scrape.state.store import connect


def read_stored_candidate_fit_evaluations() -> list[CandidateFitEvaluation]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT job_url, role_family, recommendation, strong_matches, blockers, partial_matches, reasons
            FROM candidate_fit_evaluation
            """
        ).fetchall()
    return [
        CandidateFitEvaluation(
            job_url=row[0],
            role_family=row[1],
            recommendation=row[2],
            strong_matches=tuple(json.loads(row[3])),
            blockers=tuple(json.loads(row[4])),
            partial_matches=tuple(json.loads(row[5])),
            reasons=tuple(json.loads(row[6])),
        )
        for row in rows
    ]
