import pytest

from cv_scrape.logic.map_technology_to_capability_name import map_technology_to_capability_name


@pytest.mark.parametrize(
    "technology,expected",
    [
        ("python", "Python"),
        ("sql", "SQL"),
        ("airflow", "Airflow"),
        ("git", "Git"),
        ("linux", "Linux"),
        ("docker", "Docker"),
        ("mysql", "MySQL"),
        ("java", "Java"),
        ("spark", "Spark"),
        ("kubernetes", "Kubernetes"),
        ("terraform", "Terraform"),
        ("dbt", "dbt"),
        ("postgres", "PostgreSQL"),
        ("postgresql", "PostgreSQL"),
        ("c#", "CSharp"),
        ("gcp", "GCP"),
        ("azure", "Azure"),
        ("ci/cd", "CI_CD"),
        ("continuous integration", "CI_CD"),
        ("continuous deployment", "CI_CD"),
        ("continuous delivery", "CI_CD"),
        ("github actions", "CI_CD"),
        ("gitlab ci", "CI_CD"),
        ("circleci", "CI_CD"),
        ("jenkins", "CI_CD"),
        ("azure devops", "CI_CD"),
        ("argocd", "CI_CD"),
        ("bitbucket pipelines", "CI_CD"),
        ("teamcity", "CI_CD"),
        ("bamboo", "CI_CD"),
    ],
)
def test_known_technologies_map_to_capability_name(technology, expected):
    assert map_technology_to_capability_name(technology) == expected


@pytest.mark.parametrize(
    "technology",
    ["scala", "kafka", "snowflake", "databricks", "bigquery", "redshift", "hadoop", ".net", "django", "aws"],
)
def test_technologies_with_no_matching_capability_map_to_none(technology):
    assert map_technology_to_capability_name(technology) is None


def test_unrecognized_technology_maps_to_none():
    assert map_technology_to_capability_name("cobol") is None
