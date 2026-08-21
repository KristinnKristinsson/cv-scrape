"""Effect: convergent upsert — safe to repeat."""

import json

from cv_scrape.state.job_signals import JobSignals
from cv_scrape.state.store import connect


def save_job_signals(signals: JobSignals) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO job_signals (
                job_url, role_family, seniority, language_requirement, education_requirement,
                company_type, technologies, cloud_platforms, years_experience_required, salary_mentioned
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_url) DO UPDATE SET
                role_family=excluded.role_family,
                seniority=excluded.seniority,
                language_requirement=excluded.language_requirement,
                education_requirement=excluded.education_requirement,
                company_type=excluded.company_type,
                technologies=excluded.technologies,
                cloud_platforms=excluded.cloud_platforms,
                years_experience_required=excluded.years_experience_required,
                salary_mentioned=excluded.salary_mentioned
            """,
            (
                signals.job_url,
                signals.role_family,
                signals.seniority,
                signals.language_requirement,
                signals.education_requirement,
                signals.company_type,
                json.dumps(
                    [{"technology": t.technology, "strength": t.strength} for t in signals.technologies]
                ),
                json.dumps(signals.cloud_platforms),
                signals.years_experience_required,
                signals.salary_mentioned,
            ),
        )
