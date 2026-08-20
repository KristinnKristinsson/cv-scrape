"""Effect: convergent upsert — safe to repeat. Single CV row (id=1)."""

import json

from cv_scrape.state.cv import ParsedCv
from cv_scrape.state.store import connect


def save_cv(cv: ParsedCv) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO cv (id, raw_text, skills, titles_held, years_experience)
            VALUES (1, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                raw_text=excluded.raw_text,
                skills=excluded.skills,
                titles_held=excluded.titles_held,
                years_experience=excluded.years_experience
            """,
            (cv.raw_text, json.dumps(cv.skills), json.dumps(cv.titles_held), cv.years_experience),
        )
