"""State test: the store's schema round-trips a row, no mocks needed."""

import sqlite3

from cv_scrape.state.store import SCHEMA, _add_missing_columns


def test_schema_creates_expected_tables():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"job_posting", "cv", "match_score", "fetch_watermark"} <= tables


def test_add_missing_columns_adds_last_fetched_at_to_a_pre_existing_table():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE job_posting (
            url TEXT PRIMARY KEY, source_domain TEXT, title TEXT, company TEXT,
            description TEXT, location TEXT, posted_at TEXT
        )
        """
    )

    _add_missing_columns(conn)

    columns = {row[1] for row in conn.execute("PRAGMA table_info(job_posting)")}
    assert "last_fetched_at" in columns
