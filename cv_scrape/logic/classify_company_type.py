"""Logic: whether a posting comes from a consultancy/staffing agency or reads as
a direct employer. Pure keyword match over an already-fetched JobPosting — a
heuristic against known agency names/phrasing, not a verified company-registry
lookup.
"""

from enum import Enum, auto

from cv_scrape.state.job_posting import JobPosting


class CompanyType(Enum):
    CONSULTANCY_OR_STAFFING = auto()
    DIRECT_EMPLOYER = auto()
    UNKNOWN = auto()


_AGENCY_COMPANY_NAME_MARKERS = (
    "academic work",
    "bravura",
    "tng",
    "adecco",
    "randstad",
    "poolia",
    "manpower",
    "experis",
    "kraftsam",
    "level recruitment",
    "envoke talent",
    "friday väst",
    "quest consulting",
    "a hub",
    "b3 consulting",
)
_AGENCY_PHRASE_MARKERS = (
    "på uppdrag av vår kund",
    "konsultuppdrag",
    "vi söker för kunds räkning",
    "bemanning och rekrytering",
    "our client is looking for",
)


def classify_company_type(job: JobPosting) -> CompanyType:
    company = job.company.lower()
    text = job.description.lower()

    if any(marker in company for marker in _AGENCY_COMPANY_NAME_MARKERS) or any(
        marker in text for marker in _AGENCY_PHRASE_MARKERS
    ):
        return CompanyType.CONSULTANCY_OR_STAFFING
    if company:
        return CompanyType.DIRECT_EMPLOYER
    return CompanyType.UNKNOWN
