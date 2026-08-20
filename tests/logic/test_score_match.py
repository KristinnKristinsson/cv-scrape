"""Logic tests need no fixtures or mocks — everything a logic piece reasons over
arrives as a plain argument.
"""

from cv_scrape.logic.score_match import score_match
from cv_scrape.state.cv import ParsedCv
from cv_scrape.state.job_posting import JobPosting


def test_score_match_not_yet_implemented():
    cv = ParsedCv(raw_text="", skills=(), titles_held=())
    job = JobPosting(url="https://example.com/1", source_domain="example.com", title="", company="", description="")
    try:
        score_match(cv, job)
    except NotImplementedError:
        pass
    else:
        raise AssertionError("expected NotImplementedError until score_match is implemented")
