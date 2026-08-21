"""Observation: read-only query against the persisted store."""

import json

from cv_scrape.state.job_signals import JobSignals, TechnologyRequirement
from cv_scrape.state.store import connect


def read_stored_job_signals() -> list[JobSignals]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT job_url, role_family, seniority, language_requirement, education_requirement,
                   company_type, technologies, cloud_platforms, years_experience_required, salary_mentioned
            FROM job_signals
            """
        ).fetchall()
    return [
        JobSignals(
            job_url=row[0],
            role_family=row[1],
            seniority=row[2],
            language_requirement=row[3],
            education_requirement=row[4],
            company_type=row[5],
            technologies=tuple(
                TechnologyRequirement(technology=t["technology"], strength=t["strength"])
                for t in json.loads(row[6])
            ),
            cloud_platforms=tuple(json.loads(row[7])),
            years_experience_required=row[8],
            salary_mentioned=row[9],
        )
        for row in rows
    ]
