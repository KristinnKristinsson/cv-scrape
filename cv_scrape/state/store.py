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
    posted_at TEXT
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
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    return conn
