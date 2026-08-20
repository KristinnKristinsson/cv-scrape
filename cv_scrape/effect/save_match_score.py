"""Effect: convergent upsert — safe to repeat."""

import json

from cv_scrape.state.match_score import MatchScore
from cv_scrape.state.store import connect


def save_match_score(match: MatchScore) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO match_score (job_url, score, reasons)
            VALUES (?, ?, ?)
            ON CONFLICT(job_url) DO UPDATE SET
                score=excluded.score,
                reasons=excluded.reasons
            """,
            (match.job_url, match.score, json.dumps(match.reasons)),
        )
