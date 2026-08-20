"""Flow: CLI-triggered. Sequences observation x2 -> logic -> effect. No decision, no
mutation of its own.
"""

from cv_scrape.effect.save_match_score import save_match_score
from cv_scrape.logic.score_match import score_match
from cv_scrape.observation.read_stored_cv import read_stored_cv
from cv_scrape.observation.read_stored_jobs import read_stored_jobs


def match_jobs_to_cv() -> None:
    cv = read_stored_cv()
    if cv is None:
        raise RuntimeError("No CV stored. Run `cv_scrape ingest-cv <path>` first.")
    for job in read_stored_jobs():
        save_match_score(score_match(cv, job))
