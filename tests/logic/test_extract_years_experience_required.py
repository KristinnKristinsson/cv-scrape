from cv_scrape.logic.extract_years_experience_required import extract_years_experience_required
from cv_scrape.state.job_posting import JobPosting


def _job(description: str) -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title="Data Engineer", company="Acme", description=description)


def test_matches_english_years_of_experience_phrasing():
    assert extract_years_experience_required(_job("You have 5+ years of experience with Python.")) == 5.0


def test_matches_swedish_minst_phrasing():
    assert extract_years_experience_required(_job("Du har minst 3 års erfarenhet av SQL.")) == 3.0


def test_no_match_returns_none():
    assert extract_years_experience_required(_job("We value curiosity and a growth mindset.")) is None
