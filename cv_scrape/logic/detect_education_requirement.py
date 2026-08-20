"""Logic: whether a posting states a degree requirement. Pure keyword match over
an already-fetched JobPosting's description.
"""

from enum import Enum, auto

from cv_scrape.state.job_posting import JobPosting


class EducationRequirement(Enum):
    DEGREE_REQUIRED = auto()
    DEGREE_PREFERRED = auto()
    UNSTATED = auto()


_DEGREE_REQUIRED_MARKERS = (
    "kandidatexamen krävs",
    "civilingenjör krävs",
    "degree is required",
    "bachelor's degree required",
    "master's degree required",
    "akademisk examen krävs",
)
_DEGREE_PREFERRED_MARKERS = (
    "meriterande med examen",
    "meriterande med en examen",
    "degree is a plus",
    "civilingenjör",
    "kandidatexamen",
    "master's degree",
    "bachelor's degree",
    "m.sc",
    "b.sc",
    "utbildning inom",
)


def detect_education_requirement(job: JobPosting) -> EducationRequirement:
    text = job.description.lower()

    if any(marker in text for marker in _DEGREE_REQUIRED_MARKERS):
        return EducationRequirement.DEGREE_REQUIRED
    if any(marker in text for marker in _DEGREE_PREFERRED_MARKERS):
        return EducationRequirement.DEGREE_PREFERRED
    return EducationRequirement.UNSTATED
