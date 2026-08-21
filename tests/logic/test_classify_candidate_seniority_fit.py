from cv_scrape.logic.classify_candidate_seniority_fit import SeniorityFit, classify_candidate_seniority_fit
from cv_scrape.state.job_posting import JobPosting


def _job(title: str) -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title=title, company="Acme", description="")


def test_senior_title_is_senior_title():
    assert classify_candidate_seniority_fit(_job("Senior Data Engineer"), None) is SeniorityFit.SENIOR_TITLE


def test_senior_title_wins_regardless_of_years():
    assert classify_candidate_seniority_fit(_job("Senior Data Engineer"), 1.0) is SeniorityFit.SENIOR_TITLE


def test_high_years_with_plain_title_is_high_years():
    assert classify_candidate_seniority_fit(_job("Data Engineer"), 5.0) is SeniorityFit.HIGH_YEARS


def test_moderate_years_with_plain_title_is_within_reach():
    assert classify_candidate_seniority_fit(_job("Data Engineer"), 3.0) is SeniorityFit.WITHIN_REACH


def test_no_years_and_plain_title_is_within_reach():
    assert classify_candidate_seniority_fit(_job("Data Engineer"), None) is SeniorityFit.WITHIN_REACH
