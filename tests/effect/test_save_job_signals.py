import cv_scrape.state.store as store_module
from cv_scrape.effect.save_job_signals import save_job_signals
from cv_scrape.observation.read_stored_job_signals import read_stored_job_signals
from cv_scrape.state.job_signals import JobSignals, TechnologyRequirement


def _signals() -> JobSignals:
    return JobSignals(
        job_url="https://example.com/job/1",
        role_family="DATA_ENGINEER",
        seniority="MID_OR_SENIOR",
        language_requirement="NONE_STATED",
        education_requirement="UNSTATED",
        company_type="DIRECT_EMPLOYER",
        technologies=(
            TechnologyRequirement(technology="python", strength="REQUIRED"),
            TechnologyRequirement(technology="dbt", strength="PREFERRED"),
            TechnologyRequirement(technology="kubernetes", strength="MENTIONED"),
        ),
        cloud_platforms=("gcp",),
        years_experience_required=3.0,
        salary_mentioned=None,
    )


def test_technology_requirements_round_trip_through_save_and_read(tmp_path, monkeypatch):
    monkeypatch.setattr(store_module, "DB_PATH", tmp_path / "cv_scrape.db")

    save_job_signals(_signals())

    [loaded] = read_stored_job_signals()
    assert loaded.technologies == (
        TechnologyRequirement(technology="python", strength="REQUIRED"),
        TechnologyRequirement(technology="dbt", strength="PREFERRED"),
        TechnologyRequirement(technology="kubernetes", strength="MENTIONED"),
    )


def test_save_is_a_convergent_upsert(tmp_path, monkeypatch):
    monkeypatch.setattr(store_module, "DB_PATH", tmp_path / "cv_scrape.db")

    save_job_signals(_signals())
    save_job_signals(_signals())

    assert len(read_stored_job_signals()) == 1
