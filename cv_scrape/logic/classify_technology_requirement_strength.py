"""Logic: how strongly a specific already-matched technology is required by a
posting, not just whether it's mentioned at all. Pure decision over an
already-fetched JobPosting's text plus a technology name already known (via
extract_technologies_mentioned) to appear in it — same "value already in hand"
shape as classify_seniority taking an already-derived years-required figure.

First-pass heuristic, same framing extract_technologies_mentioned.py already uses
for itself: real postings structure requirements as headed bullet lists
("Requirements:" / "Meriterande:") far more often than inline sentences, so this
walks the description line by line and tracks which section a line falls under,
rather than only checking same-line proximity. A neutral-section marker (e.g. "about
us") resets the tracked section, so a technology mentioned in a later, unrelated
paragraph doesn't inherit an earlier requirements section's strength indefinitely.
Marker lists are a starting point, meant to be tuned against real postings the same
way classify_role_family.py's hint list was (see Objectives.md's "data"/"analytics"
false-positive note) — not treated as final on first write.
"""

from enum import Enum, auto

from cv_scrape.state.job_posting import JobPosting


class RequirementStrength(Enum):
    REQUIRED = auto()
    PREFERRED = auto()
    MENTIONED = auto()


_STRENGTH_RANK = {
    RequirementStrength.REQUIRED: 2,
    RequirementStrength.PREFERRED: 1,
    RequirementStrength.MENTIONED: 0,
}

_REQUIRED_SECTION_MARKERS = (
    "krav",
    "kravprofil",
    "requirements",
    "required",
    "must have",
    "you must",
    "we require",
    "vi söker dig som",
    "du behöver",
    "ska ha",
    "qualifications",
)
_PREFERRED_SECTION_MARKERS = (
    "meriterande",
    "nice to have",
    "good to have",
    "a plus",
    "is a plus",
    "bonus",
    "gärna",
    "det är ett plus",
)
_NEUTRAL_SECTION_MARKERS = (
    "about us",
    "about the company",
    "om oss",
    "om företaget",
    "we offer",
    "vi erbjuder",
    "benefits",
    "how to apply",
    "ansökan",
)


def _line_section(line: str) -> RequirementStrength | None:
    """Which section a header-like line switches into, or None if it isn't one."""
    if any(marker in line for marker in _REQUIRED_SECTION_MARKERS):
        return RequirementStrength.REQUIRED
    if any(marker in line for marker in _PREFERRED_SECTION_MARKERS):
        return RequirementStrength.PREFERRED
    if any(marker in line for marker in _NEUTRAL_SECTION_MARKERS):
        return RequirementStrength.MENTIONED
    return None


def classify_technology_requirement_strength(job: JobPosting, technology: str) -> RequirementStrength:
    text = f"{job.title}\n{job.description}".lower()
    technology = technology.lower()

    best = RequirementStrength.MENTIONED
    section = None
    for line in text.split("\n"):
        header = _line_section(line)
        if header is not None:
            section = header

        if technology not in line:
            continue

        occurrence = header if header is not None else (section or RequirementStrength.MENTIONED)
        if _STRENGTH_RANK[occurrence] > _STRENGTH_RANK[best]:
            best = occurrence

    return best
