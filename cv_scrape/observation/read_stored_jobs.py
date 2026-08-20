"""Observation: read-only query against the persisted store."""

from cv_scrape.state.job_posting import JobPosting
from cv_scrape.state.store import connect


def read_stored_jobs() -> list[JobPosting]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT url, source_domain, title, company, description, location, posted_at FROM job_posting"
        ).fetchall()
    return [JobPosting(*row) for row in rows]
