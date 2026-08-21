"""Flow: CLI-triggered. Sequences observation -> logic -> effect over every stored
job posting, assembling JobSignals from the classify_*/detect_*/extract_* logic
pieces below — same shape as flow/probe_site.py assembling SiteProfile from its
own logic pieces. No decision, no mutation of its own: years_experience_required
is computed once and handed to classify_seniority rather than each piece
re-deriving it, and the matched technology names are computed once and handed to
classify_technology_requirement_strength once per name, but nothing here branches
on a raw value to reach a determination.
"""

from cv_scrape.effect.save_job_signals import save_job_signals
from cv_scrape.logic.classify_company_type import classify_company_type
from cv_scrape.logic.classify_role_family import classify_role_family
from cv_scrape.logic.classify_seniority import classify_seniority
from cv_scrape.logic.classify_technology_requirement_strength import (
    classify_technology_requirement_strength,
)
from cv_scrape.logic.detect_education_requirement import detect_education_requirement
from cv_scrape.logic.detect_language_requirement import detect_language_requirement
from cv_scrape.logic.extract_cloud_platforms_mentioned import extract_cloud_platforms_mentioned
from cv_scrape.logic.extract_salary_mentioned import extract_salary_mentioned
from cv_scrape.logic.extract_technologies_mentioned import extract_technologies_mentioned
from cv_scrape.logic.extract_years_experience_required import extract_years_experience_required
from cv_scrape.observation.read_stored_jobs import read_stored_jobs
from cv_scrape.state.job_signals import JobSignals, TechnologyRequirement


def extract_job_signals() -> int:
    extracted = 0
    for job in read_stored_jobs():
        years_experience_required = extract_years_experience_required(job)
        technologies_mentioned = extract_technologies_mentioned(job)
        signals = JobSignals(
            job_url=job.url,
            role_family=classify_role_family(job).name,
            seniority=classify_seniority(job, years_experience_required).name,
            language_requirement=detect_language_requirement(job).name,
            education_requirement=detect_education_requirement(job).name,
            company_type=classify_company_type(job).name,
            technologies=tuple(
                TechnologyRequirement(
                    technology=technology,
                    strength=classify_technology_requirement_strength(job, technology).name,
                )
                for technology in technologies_mentioned
            ),
            cloud_platforms=extract_cloud_platforms_mentioned(job),
            years_experience_required=years_experience_required,
            salary_mentioned=extract_salary_mentioned(job),
        )
        save_job_signals(signals)
        extracted += 1
    return extracted
