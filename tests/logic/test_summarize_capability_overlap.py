from cv_scrape.logic.summarize_capability_overlap import summarize_capability_overlap
from cv_scrape.state.candidate_profile import CandidateCapability, CandidateProfile
from cv_scrape.state.job_signals import JobSignals, TechnologyRequirement

_PROFILE = CandidateProfile(
    capabilities=(
        CandidateCapability(name="Python", level_0_to_5=4.0, evidence_classes=("A",)),
        CandidateCapability(name="GCP", level_0_to_5=3.0, evidence_classes=("A",)),
        CandidateCapability(name="PostgreSQL", level_0_to_5=2.0, evidence_classes=("C",)),
        CandidateCapability(name="dbt", level_0_to_5=0.0, evidence_classes=()),
    )
)


def _signals(technologies, cloud_platforms=()) -> JobSignals:
    return JobSignals(
        job_url="https://example.com/1",
        role_family="DATA_ENGINEER",
        seniority="MID_OR_SENIOR",
        language_requirement="NONE_STATED",
        education_requirement="UNSTATED",
        company_type="DIRECT_EMPLOYER",
        technologies=technologies,
        cloud_platforms=cloud_platforms,
    )


def test_required_zero_evidence_technology_is_a_blocker():
    signals = _signals(
        (
            TechnologyRequirement(technology="python", strength="REQUIRED"),
            TechnologyRequirement(technology="dbt", strength="REQUIRED"),
            TechnologyRequirement(technology="snowflake", strength="PREFERRED"),
            TechnologyRequirement(technology="scala", strength="MENTIONED"),
        ),
        cloud_platforms=("gcp",),
    )

    overlap = summarize_capability_overlap(signals, _PROFILE)

    assert overlap.strong_matches == ("GCP", "Python")
    assert overlap.blockers == ("dbt",)
    assert "Scala" not in overlap.blockers
    assert "Snowflake" not in overlap.blockers  # no matching capability at all -> not a blocker


def test_mentioned_only_zero_evidence_technology_is_not_a_blocker():
    signals = _signals((TechnologyRequirement(technology="dbt", strength="MENTIONED"),))

    overlap = summarize_capability_overlap(signals, _PROFILE)

    assert overlap.blockers == ()


def test_postgres_and_postgresql_are_deduped_to_one_partial_match():
    signals = _signals(
        (
            TechnologyRequirement(technology="postgres", strength="REQUIRED"),
            TechnologyRequirement(technology="postgresql", strength="REQUIRED"),
        )
    )

    overlap = summarize_capability_overlap(signals, _PROFILE)

    assert overlap.partial_matches == ("PostgreSQL",)


def test_cloud_platform_with_zero_evidence_is_not_a_blocker():
    signals = _signals((), cloud_platforms=("azure",))

    overlap = summarize_capability_overlap(signals, _PROFILE)

    assert overlap.blockers == ()
    assert overlap.strong_matches == ()
