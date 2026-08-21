import cv_scrape.flow.evaluate_candidate_fit as evaluate_candidate_fit_module
from cv_scrape.state.candidate_profile import CandidateCapability, CandidateProfile
from cv_scrape.state.job_posting import JobPosting
from cv_scrape.state.job_signals import JobSignals, TechnologyRequirement

_PROFILE = CandidateProfile(capabilities=(CandidateCapability(name="Python", level_0_to_5=4.0, evidence_classes=("A",)),))


def _job(url: str, title: str, company: str = "Acme") -> JobPosting:
    return JobPosting(url=url, source_domain="example.com", title=title, company=company, description="")


def _signals(job_url: str, role_family: str) -> JobSignals:
    return JobSignals(
        job_url=job_url,
        role_family=role_family,
        seniority="MID_OR_SENIOR",
        language_requirement="NONE_STATED",
        education_requirement="UNSTATED",
        company_type="DIRECT_EMPLOYER",
        technologies=(TechnologyRequirement(technology="python", strength="REQUIRED"),),
    )


def test_unmatched_role_family_is_excluded(monkeypatch):
    monkeypatch.setattr(evaluate_candidate_fit_module, "parse_candidate_profile", lambda: _PROFILE)
    monkeypatch.setattr(
        evaluate_candidate_fit_module,
        "read_stored_jobs",
        lambda: [_job("https://example.com/1", "Data Engineer"), _job("https://example.com/2", "Warehouse Person")],
    )
    monkeypatch.setattr(
        evaluate_candidate_fit_module,
        "read_stored_job_signals",
        lambda: [_signals("https://example.com/1", "DATA_ENGINEER"), _signals("https://example.com/2", "UNMATCHED")],
    )
    saved = []
    monkeypatch.setattr(evaluate_candidate_fit_module, "save_candidate_fit_evaluation", saved.append)

    evaluations = evaluate_candidate_fit_module.evaluate_candidate_fit()

    assert len(evaluations) == 1
    assert evaluations[0].job_url == "https://example.com/1"
    assert len(saved) == 1


def test_duplicate_postings_collapse_to_one_evaluation(monkeypatch):
    monkeypatch.setattr(evaluate_candidate_fit_module, "parse_candidate_profile", lambda: _PROFILE)
    monkeypatch.setattr(
        evaluate_candidate_fit_module,
        "read_stored_jobs",
        lambda: [
            _job("https://arbetsformedlingen.se/1", "Data Engineer", company="Acme"),
            _job("https://jobbsafari.se/1", "Data Engineer", company="Acme"),
        ],
    )
    monkeypatch.setattr(
        evaluate_candidate_fit_module,
        "read_stored_job_signals",
        lambda: [
            _signals("https://arbetsformedlingen.se/1", "DATA_ENGINEER"),
            _signals("https://jobbsafari.se/1", "DATA_ENGINEER"),
        ],
    )
    monkeypatch.setattr(evaluate_candidate_fit_module, "save_candidate_fit_evaluation", lambda evaluation: None)

    evaluations = evaluate_candidate_fit_module.evaluate_candidate_fit()

    assert len(evaluations) == 1
