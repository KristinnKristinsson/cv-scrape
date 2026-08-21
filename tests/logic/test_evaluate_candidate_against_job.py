import pytest

from cv_scrape.logic.classify_candidate_seniority_fit import SeniorityFit
from cv_scrape.logic.evaluate_candidate_against_job import evaluate_candidate_against_job
from cv_scrape.state.capability_overlap import CapabilityOverlap
from cv_scrape.state.job_signals import JobSignals

_SIGNALS = JobSignals(
    job_url="https://example.com/1",
    role_family="DATA_ENGINEER",
    seniority="MID_OR_SENIOR",
    language_requirement="NONE_STATED",
    education_requirement="UNSTATED",
    company_type="DIRECT_EMPLOYER",
)


def _overlap(strong: int, blockers: int) -> CapabilityOverlap:
    return CapabilityOverlap(
        strong_matches=tuple(f"strong-{i}" for i in range(strong)),
        blockers=tuple(f"blocker-{i}" for i in range(blockers)),
    )


@pytest.mark.parametrize(
    "strong,blockers,expected",
    [
        (0, 0, "SKIP"),
        (0, 5, "SKIP"),
        (1, 0, "LOW_PRIORITY"),
        (1, 2, "LOW_PRIORITY"),
        (1, 3, "SKIP"),
        (2, 0, "APPLY"),
        (2, 2, "APPLY_STRETCH"),
        (2, 3, "LOW_PRIORITY"),
        (4, 0, "APPLY"),
    ],
)
def test_base_recommendation_table(strong, blockers, expected):
    evaluation = evaluate_candidate_against_job(_SIGNALS, _overlap(strong, blockers), SeniorityFit.WITHIN_REACH)
    assert evaluation.recommendation == expected


def test_high_years_demotes_by_one_tier():
    evaluation = evaluate_candidate_against_job(_SIGNALS, _overlap(4, 0), SeniorityFit.HIGH_YEARS)
    assert evaluation.recommendation == "APPLY_STRETCH"


def test_high_years_demotes_low_priority_to_skip():
    evaluation = evaluate_candidate_against_job(_SIGNALS, _overlap(1, 0), SeniorityFit.HIGH_YEARS)
    assert evaluation.recommendation == "SKIP"


def test_senior_title_is_a_hard_skip_regardless_of_overlap():
    evaluation = evaluate_candidate_against_job(_SIGNALS, _overlap(4, 0), SeniorityFit.SENIOR_TITLE)
    assert evaluation.recommendation == "SKIP"


def test_evaluation_carries_job_url_and_role_family():
    evaluation = evaluate_candidate_against_job(_SIGNALS, _overlap(2, 0), SeniorityFit.WITHIN_REACH)
    assert evaluation.job_url == "https://example.com/1"
    assert evaluation.role_family == "DATA_ENGINEER"
