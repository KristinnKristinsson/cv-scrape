from cv_scrape.logic.detect_education_requirement import EducationRequirement, detect_education_requirement
from cv_scrape.state.job_posting import JobPosting


def _job(description: str) -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title="Data Engineer", company="Acme", description=description)


def test_degree_required_marker():
    assert (
        detect_education_requirement(_job("A bachelor's degree required for this role."))
        is EducationRequirement.DEGREE_REQUIRED
    )


def test_degree_preferred_marker():
    assert (
        detect_education_requirement(_job("Civilingenjör inom data eller motsvarande."))
        is EducationRequirement.DEGREE_PREFERRED
    )


def test_no_marker_is_unstated():
    assert detect_education_requirement(_job("We care about what you can do, not your diploma.")) is EducationRequirement.UNSTATED
