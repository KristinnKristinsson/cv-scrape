"""Logic: which of the Stockholm-benchmark's seven role families a posting's title
matches, per the boundaries drafted in Objectives.md. Pure decision over a
JobPosting already in hand — formalizes the keyword rules used for the manual
2026-08-20 sample curation (see Objectives.md's "Step 2 collection log") into a
real piece instead of one-off SQL.
"""

from enum import Enum, auto

from cv_scrape.state.job_posting import JobPosting


class RoleFamily(Enum):
    DATA_ENGINEER = auto()
    ANALYTICS_ENGINEER = auto()
    ETL_INTEGRATION = auto()
    DATA_PLATFORM = auto()
    PYTHON_DATA_DEVELOPER = auto()
    DATA_HEAVY_BACKEND = auto()
    UNMATCHED = auto()


_DATA_ENGINEER_TITLE_MARKERS = ("data engineer", "dataingenjör")
_ANALYTICS_ENGINEER_TITLE_MARKERS = ("analytics engineer",)
_ETL_INTEGRATION_TITLE_MARKERS = (
    "etl",
    "integrationsutvecklare",
    "data integration",
    "integration developer",
    "integration engineer",
)
_DATA_PLATFORM_TITLE_MARKERS = ("data platform", "cloud data engineer", "gcp data engineer")
_PYTHON_TITLE_MARKER = "python"
_BACKEND_TITLE_MARKERS = ("backend", "back-end")

# Family 5/6's boundary rule (Objectives.md): a Python/backend title only counts if
# the posting shows an actual data-handling responsibility, not just the title word.
# Deliberately specific, not bare "data" or "analytics" — a first pass using those
# matched almost every posting (game studios included) on incidental mentions like
# "player data" or GDPR boilerplate, making the boundary rule ineffective.
_DATA_HANDLING_HINTS = (
    "etl",
    "data pipeline",
    "data pipelines",
    "dataintegration",
    "data integration",
    "data warehouse",
    "dataplattform",
    "data platform",
    "data engineering",
    "data lake",
    "datakvalitet",
    "big data",
    "snowflake",
    "databricks",
    "dbt",
    "airflow",
)


def classify_role_family(job: JobPosting) -> RoleFamily:
    title = job.title.lower()
    description = job.description.lower()

    if any(marker in title for marker in _DATA_ENGINEER_TITLE_MARKERS):
        return RoleFamily.DATA_ENGINEER
    if any(marker in title for marker in _ANALYTICS_ENGINEER_TITLE_MARKERS):
        return RoleFamily.ANALYTICS_ENGINEER
    if any(marker in title for marker in _ETL_INTEGRATION_TITLE_MARKERS):
        return RoleFamily.ETL_INTEGRATION
    if any(marker in title for marker in _DATA_PLATFORM_TITLE_MARKERS):
        return RoleFamily.DATA_PLATFORM
    if _PYTHON_TITLE_MARKER in title and any(hint in description for hint in _DATA_HANDLING_HINTS):
        return RoleFamily.PYTHON_DATA_DEVELOPER
    if any(marker in title for marker in _BACKEND_TITLE_MARKERS) and any(
        hint in description for hint in _DATA_HANDLING_HINTS
    ):
        return RoleFamily.DATA_HEAVY_BACKEND
    return RoleFamily.UNMATCHED
