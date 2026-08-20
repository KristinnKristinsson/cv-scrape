"""Effect: convergent upsert — safe to repeat.

fetched_at is when *we* retrieved this posting, not a property of the posting
itself (state/job_posting.py's JobPosting stays "defined by what it is, not by
who touches it") — so it's a separate parameter here rather than a JobPosting
field, supplied by the caller from observation/read_clock.py, same as
flow/probe_site.py hands its own clock reading down rather than letting an
effect reach for the time itself.
"""

from cv_scrape.state.job_posting import JobPosting
from cv_scrape.state.store import connect


def save_job_posting(job: JobPosting, fetched_at: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO job_posting
                (url, source_domain, title, company, description, location, posted_at, last_fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                source_domain=excluded.source_domain,
                title=excluded.title,
                company=excluded.company,
                description=excluded.description,
                location=excluded.location,
                posted_at=excluded.posted_at,
                last_fetched_at=excluded.last_fetched_at
            """,
            (
                job.url,
                job.source_domain,
                job.title,
                job.company,
                job.description,
                job.location,
                job.posted_at,
                fetched_at,
            ),
        )
