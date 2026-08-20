"""Logic: pure decision — is there a CV to match jobs against? ParsedCv | None already
in hand (from observation), no fetch, no mutation.
"""

from enum import Enum, auto

from cv_scrape.state.cv import ParsedCv


class CvAvailability(Enum):
    PRESENT = auto()
    MISSING = auto()


def check_cv_availability(cv: ParsedCv | None) -> CvAvailability:
    return CvAvailability.MISSING if cv is None else CvAvailability.PRESENT
