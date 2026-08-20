from cv_scrape.logic.extract_salary_mentioned import extract_salary_mentioned
from cv_scrape.state.job_posting import JobPosting


def _job(description: str) -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title="Data Engineer", company="Acme", description=description)


def test_matches_a_monthly_salary_figure():
    assert extract_salary_mentioned(_job("Lönen är 42 000 kr/mån enligt överenskommelse.")) == "42 000 kr/mån"


def test_no_figure_returns_none():
    assert extract_salary_mentioned(_job("Lön enligt överenskommelse.")) is None
