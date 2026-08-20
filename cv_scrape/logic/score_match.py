"""Logic: pure decision — ParsedCv + JobPosting in hand, no fetch, no mutation."""

from cv_scrape.state.cv import ParsedCv
from cv_scrape.state.job_posting import JobPosting
from cv_scrape.state.match_score import MatchScore


def score_match(cv: ParsedCv, job: JobPosting) -> MatchScore:
    raise NotImplementedError
