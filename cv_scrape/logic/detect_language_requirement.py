"""Logic: whether a posting requires Swedish or states English is enough. Pure
keyword match over an already-fetched JobPosting's description.
"""

from enum import Enum, auto

from cv_scrape.state.job_posting import JobPosting


class LanguageRequirement(Enum):
    SWEDISH_REQUIRED = auto()
    ENGLISH_OK = auto()
    UNSTATED = auto()


_SWEDISH_REQUIRED_MARKERS = (
    "flytande svenska",
    "svenska i tal och skrift",
    "goda kunskaper i svenska",
    "fluent swedish",
    "fluent in swedish",
    "swedish is required",
    "svenska krävs",
)
_ENGLISH_OK_MARKERS = (
    "engelska räcker",
    "english is enough",
    "working language is english",
    "arbetsspråk är engelska",
    "engelska som arbetsspråk",
)


def detect_language_requirement(job: JobPosting) -> LanguageRequirement:
    text = job.description.lower()

    if any(marker in text for marker in _SWEDISH_REQUIRED_MARKERS):
        return LanguageRequirement.SWEDISH_REQUIRED
    if any(marker in text for marker in _ENGLISH_OK_MARKERS):
        return LanguageRequirement.ENGLISH_OK
    return LanguageRequirement.UNSTATED
