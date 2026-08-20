"""State: one page of results from Arbetsförmedlingen's JobSearch API, already
parsed into JobPostings. `total` is the API's own count of all matching ads across
every page, carried alongside the page so flow/fetch_jobs_from_api.py can decide
when to stop paginating without re-reading the raw JSON a second time.
"""

from dataclasses import dataclass

from cv_scrape.state.job_posting import JobPosting


@dataclass(frozen=True)
class JobSearchApiPage:
    postings: tuple[JobPosting, ...]
    total: int
