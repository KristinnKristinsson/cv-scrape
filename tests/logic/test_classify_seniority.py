from cv_scrape.logic.classify_seniority import SeniorityTag, classify_seniority
from cv_scrape.state.job_posting import JobPosting


def _job(title: str, description: str = "") -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title=title, company="Acme", description=description)


def test_junior_title_with_no_experience_requirement_is_junior_friendly():
    assert classify_seniority(_job("Junior Data Engineer"), years_experience_required=None) is SeniorityTag.JUNIOR_FRIENDLY


def test_junior_title_but_significant_experience_required_is_mid_or_senior():
    job = _job("Junior Data Engineer", "You'll need 5+ years of experience.")
    assert classify_seniority(job, years_experience_required=5.0) is SeniorityTag.MID_OR_SENIOR


def test_senior_marker_is_mid_or_senior():
    assert classify_seniority(_job("Senior Data Engineer"), years_experience_required=None) is SeniorityTag.MID_OR_SENIOR


def test_no_signal_is_unclear():
    assert classify_seniority(_job("Data Engineer"), years_experience_required=None) is SeniorityTag.UNCLEAR
