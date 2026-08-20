from cv_scrape.logic.detect_language_requirement import LanguageRequirement, detect_language_requirement
from cv_scrape.state.job_posting import JobPosting


def _job(description: str) -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title="Data Engineer", company="Acme", description=description)


def test_swedish_required_marker():
    assert detect_language_requirement(_job("Vi ser att du har flytande svenska.")) is LanguageRequirement.SWEDISH_REQUIRED


def test_english_ok_marker():
    assert detect_language_requirement(_job("Our working language is English.")) is LanguageRequirement.ENGLISH_OK


def test_no_marker_is_unstated():
    assert detect_language_requirement(_job("We value clear communication.")) is LanguageRequirement.UNSTATED
