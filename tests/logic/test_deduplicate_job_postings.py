from cv_scrape.logic.deduplicate_job_postings import deduplicate_job_postings
from cv_scrape.state.job_posting import JobPosting


def _job(url: str, title: str = "Data Engineer", company: str = "Acme", posted_at: str | None = None) -> JobPosting:
    return JobPosting(
        url=url, source_domain="example.com", title=title, company=company, description="", posted_at=posted_at
    )


def test_no_duplicates_returns_all_jobs_unchanged():
    jobs = [_job("https://example.com/1"), _job("https://example.com/2", title="Analytics Engineer")]
    assert deduplicate_job_postings(jobs) == jobs


def test_same_title_and_company_across_urls_collapses_to_one():
    jobs = [
        _job("https://arbetsformedlingen.se/platsbanken/annonser/1", posted_at="2026-06-01T10:02:11"),
        _job("https://arbetsformedlingen.se/platsbanken/annonser/2", posted_at="2026-06-01T10:01:30"),
    ]
    result = deduplicate_job_postings(jobs)
    assert len(result) == 1
    assert result[0].url == "https://arbetsformedlingen.se/platsbanken/annonser/2"


def test_cross_source_repost_keeps_the_earlier_posted_at():
    jobs = [
        _job("https://jobbsafari.se/jobb/x", posted_at="2026-04-26T22:00:01.000Z"),
        _job("https://arbetsformedlingen.se/platsbanken/annonser/x", posted_at="2026-04-27T11:45:47"),
    ]
    result = deduplicate_job_postings(jobs)
    assert len(result) == 1
    assert result[0].url == "https://jobbsafari.se/jobb/x"


def test_title_and_company_matching_is_case_and_whitespace_insensitive():
    jobs = [
        _job("https://example.com/1", title="Data Engineer", company="Acme AB"),
        _job("https://example.com/2", title=" data engineer ", company="ACME AB"),
    ]
    assert len(deduplicate_job_postings(jobs)) == 1


def test_missing_posted_at_keeps_the_first_seen_copy():
    jobs = [
        _job("https://example.com/1", posted_at=None),
        _job("https://example.com/2", posted_at="2026-06-01T10:00:00"),
    ]
    result = deduplicate_job_postings(jobs)
    assert result[0].url == "https://example.com/1"


def test_different_companies_with_the_same_title_are_not_duplicates():
    jobs = [
        _job("https://example.com/1", title="Backend Developer", company="Snowprint Studios AB"),
        _job("https://example.com/2", title="Backend Developer", company="Validio AB"),
    ]
    assert deduplicate_job_postings(jobs) == jobs
