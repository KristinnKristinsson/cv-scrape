"""Observation: read-only query against the persisted store."""

import json

from cv_scrape.state.cv import ParsedCv
from cv_scrape.state.store import connect


def read_stored_cv() -> ParsedCv | None:
    with connect() as conn:
        row = conn.execute("SELECT raw_text, skills, titles_held, years_experience FROM cv WHERE id = 1").fetchone()
    if row is None:
        return None
    raw_text, skills, titles_held, years_experience = row
    return ParsedCv(
        raw_text=raw_text,
        skills=tuple(json.loads(skills)),
        titles_held=tuple(json.loads(titles_held)),
        years_experience=years_experience,
    )
