from cv_scrape.logic.classify_technology_requirement_strength import (
    RequirementStrength,
    classify_technology_requirement_strength,
)
from cv_scrape.state.job_posting import JobPosting


def _job(description: str) -> JobPosting:
    return JobPosting(url="https://example.com/1", source_domain="example.com", title="Data Engineer", company="Acme", description=description)


def test_technology_under_requirements_header_is_required():
    job = _job("Requirements:\n- Python\n- SQL\n\nNice to have:\n- dbt")
    assert classify_technology_requirement_strength(job, "python") is RequirementStrength.REQUIRED
    assert classify_technology_requirement_strength(job, "sql") is RequirementStrength.REQUIRED


def test_technology_under_meriterande_header_is_preferred():
    job = _job("Krav:\n- SQL\n\nMeriterande:\n- dbt\n- Snowflake")
    assert classify_technology_requirement_strength(job, "dbt") is RequirementStrength.PREFERRED
    assert classify_technology_requirement_strength(job, "snowflake") is RequirementStrength.PREFERRED


def test_inline_marker_overrides_section():
    job = _job("Meriterande:\n- SQL\n- Docker is a plus\n\nKafka experience is required for this role.")
    assert classify_technology_requirement_strength(job, "kafka") is RequirementStrength.REQUIRED
    assert classify_technology_requirement_strength(job, "docker") is RequirementStrength.PREFERRED


def test_no_marker_defaults_to_mentioned():
    job = _job("We work with Docker in a fast-paced team.")
    assert classify_technology_requirement_strength(job, "docker") is RequirementStrength.MENTIONED


def test_neutral_section_does_not_inherit_earlier_requirement():
    job = _job("Requirements:\n- Python\n\nAbout us:\nWe also use Kubernetes internally.")
    assert classify_technology_requirement_strength(job, "kubernetes") is RequirementStrength.MENTIONED


def test_strongest_occurrence_wins_across_multiple_mentions():
    job = _job("Requirements:\n- Python\n\nAbout us:\nWe love Python here too.")
    assert classify_technology_requirement_strength(job, "python") is RequirementStrength.REQUIRED
