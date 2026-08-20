"""Effect: convergent upsert — safe to repeat. Mirrors effect/save_job_posting.py's
shape for state/fetch_watermark.py.
"""

from cv_scrape.state.store import connect


def save_fetch_watermark(query_key: str, last_run_at: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO fetch_watermark (query_key, last_run_at)
            VALUES (?, ?)
            ON CONFLICT(query_key) DO UPDATE SET last_run_at=excluded.last_run_at
            """,
            (query_key, last_run_at),
        )
