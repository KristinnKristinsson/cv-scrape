"""State: the persisted store's shape. Not a decision/fetch/mutation itself — see
structure.md's "Ambiguous placement calls" #5. Imported by effect (writes) and
observation (reads).
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "cv_scrape.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS job_posting (
    url TEXT PRIMARY KEY,
    source_domain TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    description TEXT NOT NULL,
    location TEXT,
    posted_at TEXT,
    last_fetched_at TEXT
);

CREATE TABLE IF NOT EXISTS fetch_watermark (
    query_key TEXT PRIMARY KEY,
    last_run_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS job_signals (
    job_url TEXT PRIMARY KEY REFERENCES job_posting(url),
    role_family TEXT NOT NULL,
    seniority TEXT NOT NULL,
    language_requirement TEXT NOT NULL,
    education_requirement TEXT NOT NULL,
    company_type TEXT NOT NULL,
    technologies TEXT NOT NULL,
    cloud_platforms TEXT NOT NULL,
    years_experience_required REAL,
    salary_mentioned TEXT
);

CREATE TABLE IF NOT EXISTS candidate_fit_evaluation (
    job_url TEXT PRIMARY KEY REFERENCES job_posting(url),
    role_family TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    strong_matches TEXT NOT NULL,
    blockers TEXT NOT NULL,
    partial_matches TEXT NOT NULL,
    reasons TEXT NOT NULL
);
"""

# Tables from a superseded generic CV-matching vertical, replaced by candidate.yaml +
# evaluate_candidate_against_job.py — dropped here (not just removed from SCHEMA
# above) so the live local DB actually loses them, not just the code that wrote them.
# Both were confirmed empty (never wired to a working flow) before removal.
_TABLES_TO_DROP = ("cv", "match_score")

# CREATE TABLE IF NOT EXISTS only covers tables missing outright — a table that
# already existed before a column was added to SCHEMA needs that column added
# explicitly. Same declarative-shape-enforcement role as SCHEMA itself (Ambiguous
# Call #5), just the ALTER-path version of it.
_COLUMN_ADDITIONS = {
    "job_posting": ["last_fetched_at TEXT"],
}


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    _add_missing_columns(conn)
    _drop_removed_tables(conn)
    return conn


def _add_missing_columns(conn: sqlite3.Connection) -> None:
    for table, column_defs in _COLUMN_ADDITIONS.items():
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        for column_def in column_defs:
            column_name = column_def.split()[0]
            if column_name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")


def _drop_removed_tables(conn: sqlite3.Connection) -> None:
    for table in _TABLES_TO_DROP:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
