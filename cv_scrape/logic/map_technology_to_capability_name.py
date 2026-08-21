"""Logic: which candidate.yaml capability (if any) a job-posting technology keyword
corresponds to. Pure lookup over a static table — a fact about the two vocabularies
(extract_technologies_mentioned.py's keyword list and candidate.yaml's capability
names), not a decision that needs a CandidateProfile in hand, so it's independent of
classify_candidate_capability_strength.py despite feeding it. Deliberately built by
hand rather than derived (e.g. by casefolding), since the two vocabularies don't
line up 1:1 — this is exactly the ad-hoc mapping gap that caused the postgres/
postgresql double-count Candidate Placement Findings.md flagged.
"""

_TECHNOLOGY_TO_CAPABILITY = {
    "python": "Python",
    "sql": "SQL",
    "airflow": "Airflow",
    "git": "Git",
    "linux": "Linux",
    "docker": "Docker",
    "mysql": "MySQL",
    "java": "Java",
    "spark": "Spark",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",
    "dbt": "dbt",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "c#": "CSharp",
    "gcp": "GCP",
    "azure": "Azure",
    "ci/cd": "CI_CD",
    "continuous integration": "CI_CD",
    "continuous deployment": "CI_CD",
    "continuous delivery": "CI_CD",
    "github actions": "CI_CD",
    "gitlab ci": "CI_CD",
    "circleci": "CI_CD",
    "jenkins": "CI_CD",
    "azure devops": "CI_CD",
    "argocd": "CI_CD",
    "bitbucket pipelines": "CI_CD",
    "teamcity": "CI_CD",
    "bamboo": "CI_CD",
}
# Deliberately absent, not an omission: scala, kafka, snowflake, databricks,
# bigquery, redshift, hadoop, .net, django, aws — candidate.yaml lists no matching
# capability for any of these. Falling through to None for them is the correct,
# deliberate answer, not a gap to fill in later.
#
# The CI/CD-tool entries above all collapse to the same "CI_CD" capability name
# deliberately — candidate.yaml grades CI/CD as one ownership-experience capability,
# not per-tool, so a posting naming Jenkins vs. GitHub Actions is the same
# determination against the candidate's profile (same "same thing" test
# classify_role_family.py's hint list already follows).


def map_technology_to_capability_name(technology: str) -> str | None:
    return _TECHNOLOGY_TO_CAPABILITY.get(technology.lower())
