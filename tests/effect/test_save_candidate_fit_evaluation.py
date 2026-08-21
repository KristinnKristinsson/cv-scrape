import cv_scrape.state.store as store_module
from cv_scrape.effect.save_candidate_fit_evaluation import save_candidate_fit_evaluation
from cv_scrape.observation.read_stored_candidate_fit_evaluations import read_stored_candidate_fit_evaluations
from cv_scrape.state.candidate_fit_evaluation import CandidateFitEvaluation


def _evaluation() -> CandidateFitEvaluation:
    return CandidateFitEvaluation(
        job_url="https://example.com/job/1",
        role_family="DATA_ENGINEER",
        recommendation="APPLY_STRETCH",
        strong_matches=("Python", "SQL"),
        blockers=("dbt",),
        partial_matches=("PostgreSQL",),
        reasons=("Strong-evidence overlap: Python, SQL",),
    )


def test_evaluation_round_trips_through_save_and_read(tmp_path, monkeypatch):
    monkeypatch.setattr(store_module, "DB_PATH", tmp_path / "cv_scrape.db")

    save_candidate_fit_evaluation(_evaluation())

    [loaded] = read_stored_candidate_fit_evaluations()
    assert loaded == _evaluation()


def test_save_is_a_convergent_upsert(tmp_path, monkeypatch):
    monkeypatch.setattr(store_module, "DB_PATH", tmp_path / "cv_scrape.db")

    save_candidate_fit_evaluation(_evaluation())
    save_candidate_fit_evaluation(_evaluation())

    assert len(read_stored_candidate_fit_evaluations()) == 1
