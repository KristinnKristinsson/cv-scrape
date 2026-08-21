"""Logic: which known technologies are named in a posting's text. Pure keyword
match over an already-fetched JobPosting — a first pass, not NLP; see
Objectives.md's "inferred fields" note on why this is heuristic, not exhaustive.
"""

from cv_scrape.state.job_posting import JobPosting

_TECHNOLOGY_KEYWORDS = (
    "python",
    "sql",
    "scala",
    "java",
    "spark",
    "airflow",
    "dbt",
    "kafka",
    "docker",
    "kubernetes",
    "linux",
    "snowflake",
    "databricks",
    "postgres",
    "postgresql",
    "mysql",
    "terraform",
    "git",
    "bigquery",
    "redshift",
    "hadoop",
    ".net",
    "c#",
    "django",
    "ci/cd",
    "continuous integration",
    "continuous deployment",
    "continuous delivery",
    "github actions",
    "gitlab ci",
    "circleci",
    "jenkins",
    "azure devops",
    "argocd",
    "bitbucket pipelines",
    "teamcity",
    "bamboo",
    "power bi",
    "powerbi",
    "looker",
    "tableau",
    "sql server",
    "mssql",
    "oracle",
    "mongodb",
    "redis",
    "fivetran",
    "matillion",
    "ssis",
    "azure data factory",
    "azure synapse",
    "synapse",
    "delta lake",
    "iceberg",
    "flink",
    "graphql",
    "typescript",
    "lambda",
    "glue",
    "grafana",
)
# Deliberately absent, not an omission: "rust", "go", "sap", "excel", "nifi" — all
# checked against the curated Stockholm sample (Objectives.md's "technology/
# role-family keyword lists" revisit) and found to be near-total false-positive
# traps as bare substrings ("trusted"/"trust" for rust, "excellent"/"excellence"
# for excel, "significant" for nifi, "ASAP" for sap, "go deep"/"going" for go) —
# same "single common word is a coin flip" lesson as classify_role_family.py's
# original "data"/"analytics" hint list (see Objectives.md's step-3 note). Each had
# at most one genuine hit in 71 curated postings, not enough signal to justify the
# false-positive rate a bare-word marker would add.


def extract_technologies_mentioned(job: JobPosting) -> tuple[str, ...]:
    text = f"{job.title}\n{job.description}".lower()
    return tuple(keyword for keyword in _TECHNOLOGY_KEYWORDS if keyword in text)
