"""Logic: best-effort years-of-experience requirement parsed from a posting's
text. Pure regex decision over an already-fetched JobPosting.
"""

import re

from cv_scrape.state.job_posting import JobPosting

_PATTERNS = (
    re.compile(r"(\d+)\+?\s*(?:years?|års?)\s*(?:of\s*)?(?:experience|erfarenhet)", re.IGNORECASE),
    re.compile(r"minst\s*(\d+)\s*års?\s*erfarenhet", re.IGNORECASE),
)


def extract_years_experience_required(job: JobPosting) -> float | None:
    for pattern in _PATTERNS:
        match = pattern.search(job.description)
        if match:
            return float(match.group(1))
    return None
