from cv_scrape.logic.classify_company_type import CompanyType, classify_company_type
from cv_scrape.state.job_posting import JobPosting


def _job(company: str, description: str = "") -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title="Data Engineer", company=company, description=description)


def test_known_agency_name_is_consultancy_or_staffing():
    assert classify_company_type(_job("Academic Work Sweden AB")) is CompanyType.CONSULTANCY_OR_STAFFING


def test_agency_phrasing_in_description_is_consultancy_or_staffing():
    job = _job("Some Recruiter AB", "Vi söker för kunds räkning en erfaren utvecklare.")
    assert classify_company_type(job) is CompanyType.CONSULTANCY_OR_STAFFING


def test_plain_company_name_is_direct_employer():
    assert classify_company_type(_job("Spotify AB")) is CompanyType.DIRECT_EMPLOYER


def test_no_company_is_unknown():
    assert classify_company_type(_job("")) is CompanyType.UNKNOWN
