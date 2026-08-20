from cv_scrape.logic.extract_cloud_platforms_mentioned import extract_cloud_platforms_mentioned
from cv_scrape.state.job_posting import JobPosting


def _job(description: str) -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title="Data Engineer", company="Acme", description=description)


def test_matches_named_cloud_platforms():
    assert extract_cloud_platforms_mentioned(_job("We run on Google Cloud and a bit of Azure.")) == ("gcp", "azure")


def test_no_matches_returns_empty_tuple():
    assert extract_cloud_platforms_mentioned(_job("On-prem only.")) == ()
