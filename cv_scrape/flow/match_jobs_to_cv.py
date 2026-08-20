"""Flow: CLI-triggered. Sequences observation -> logic -> effect. No decision, no
mutation of its own — routes on the tag check_cv_availability returns instead of
inspecting the observed value itself.
"""

from cv_scrape.effect.save_match_score import save_match_score
from cv_scrape.logic.check_cv_availability import CvAvailability, check_cv_availability
from cv_scrape.logic.score_match import score_match
from cv_scrape.observation.read_stored_cv import read_stored_cv
from cv_scrape.observation.read_stored_jobs import read_stored_jobs


def match_jobs_to_cv() -> None:
    cv = read_stored_cv()
    if check_cv_availability(cv) is CvAvailability.MISSING:
        raise RuntimeError("No CV stored. Run `cv_scrape ingest-cv <path>` first.")
    for job in read_stored_jobs():
        save_match_score(score_match(cv, job))
