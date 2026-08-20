"""Logic: a raw salary-like substring pulled from a posting's text, if present.
Best-effort regex capture, not structured salary parsing — Swedish ads rarely
state a figure at all, so this only needs to catch the ones that do.
"""

import re

from cv_scrape.state.job_posting import JobPosting

_SALARY_PATTERN = re.compile(r"\d[\d\s]{3,}\s?(?:kr|sek)(?:\s?/?\s?(?:mån|month|år|year))?", re.IGNORECASE)


def extract_salary_mentioned(job: JobPosting) -> str | None:
    match = _SALARY_PATTERN.search(job.description)
    return match.group(0).strip() if match else None
