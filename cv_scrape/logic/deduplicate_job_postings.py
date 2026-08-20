"""Logic: which postings in a collected batch are the same real vacancy seen more
than once, and which copy to keep. Pure decision over a list of JobPosting already
in hand — formalizes the 2026-08-20 spot-check (see Objectives.md) that found two
duplicate shapes in the raw sample: the same ad cross-posted on arbetsformedlingen.se
and jobbsafari.se, and the same employer submitting the same ad twice on Platsbanken
under two different ad IDs. Both produce distinct urls (the store's primary key), so
the store's own uniqueness can't catch this — it has to be decided here instead.
"""

from cv_scrape.state.job_posting import JobPosting


def _dedupe_key(job: JobPosting) -> tuple[str, str]:
    return (job.title.strip().casefold(), job.company.strip().casefold())


def deduplicate_job_postings(jobs: list[JobPosting]) -> list[JobPosting]:
    canonical_by_key: dict[tuple[str, str], JobPosting] = {}
    for job in jobs:
        key = _dedupe_key(job)
        current = canonical_by_key.get(key)
        if current is None or _is_earlier(job, current):
            canonical_by_key[key] = job

    kept_urls = {job.url for job in canonical_by_key.values()}
    return [job for job in jobs if job.url in kept_urls]


def _is_earlier(candidate: JobPosting, current: JobPosting) -> bool:
    if candidate.posted_at is None or current.posted_at is None:
        return False
    return candidate.posted_at < current.posted_at
