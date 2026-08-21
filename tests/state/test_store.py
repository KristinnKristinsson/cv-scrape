"""State test: the store's schema round-trips a row, no mocks needed."""

import sqlite3

from cv_scrape.state.store import SCHEMA, _add_missing_columns, _drop_removed_tables


def test_schema_creates_expected_tables():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"job_posting", "fetch_watermark", "job_signals", "candidate_fit_evaluation"} <= tables


def test_drop_removed_tables_drops_a_pre_seeded_cv_table():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE cv (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE match_score (job_url TEXT PRIMARY KEY)")

    _drop_removed_tables(conn)

    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "cv" not in tables
    assert "match_score" not in tables


def test_drop_removed_tables_is_a_no_op_when_absent():
    conn = sqlite3.connect(":memory:")
    _drop_removed_tables(conn)  # must not raise


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
