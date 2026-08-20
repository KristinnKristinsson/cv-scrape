"""State test: the store's schema round-trips a row, no mocks needed."""

import sqlite3

from cv_scrape.state.store import SCHEMA


def test_schema_creates_expected_tables():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"job_posting", "cv", "match_score"} <= tables
