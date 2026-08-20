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

CREATE TABLE IF NOT EXISTS cv (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    raw_text TEXT NOT NULL,
    skills TEXT NOT NULL,
    titles_held TEXT NOT NULL,
    years_experience REAL
);

CREATE TABLE IF NOT EXISTS match_score (
    job_url TEXT PRIMARY KEY REFERENCES job_posting(url),
    score REAL NOT NULL,
    reasons TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fetch_watermark (
    query_key TEXT PRIMARY KEY,
    last_run_at TEXT NOT NULL
);
"""

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
    return conn


def _add_missing_columns(conn: sqlite3.Connection) -> None:
    for table, column_defs in _COLUMN_ADDITIONS.items():
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        for column_def in column_defs:
            column_name = column_def.split()[0]
            if column_name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
