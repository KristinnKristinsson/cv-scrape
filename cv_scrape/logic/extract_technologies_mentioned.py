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
)


def extract_technologies_mentioned(job: JobPosting) -> tuple[str, ...]:
    text = f"{job.title}\n{job.description}".lower()
    return tuple(keyword for keyword in _TECHNOLOGY_KEYWORDS if keyword in text)
