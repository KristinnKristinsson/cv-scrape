"""Observation: read our own stored fetch-run watermark for a query, unchanged.
Mirrors observation/read_session_state.py's role for state/session.py.
"""

from cv_scrape.state.fetch_watermark import FetchWatermark
from cv_scrape.state.store import connect


def read_fetch_watermark(query_key: str) -> FetchWatermark | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT query_key, last_run_at FROM fetch_watermark WHERE query_key = ?", (query_key,)
        ).fetchone()

    if row is None:
        return None
    return FetchWatermark(query_key=row[0], last_run_at=row[1])
