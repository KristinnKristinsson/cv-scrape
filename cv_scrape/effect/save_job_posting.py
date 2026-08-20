"""Effect: convergent upsert — safe to repeat."""

from cv_scrape.state.job_posting import JobPosting
from cv_scrape.state.store import connect


def save_job_posting(job: JobPosting) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO job_posting (url, source_domain, title, company, description, location, posted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                source_domain=excluded.source_domain,
                title=excluded.title,
                company=excluded.company,
                description=excluded.description,
                location=excluded.location,
                posted_at=excluded.posted_at
            """,
            (job.url, job.source_domain, job.title, job.company, job.description, job.location, job.posted_at),
        )
