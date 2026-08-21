"""Logic: how strong the candidate's evidence is for one named capability. Pure
decision over a capability name (already resolved by
map_technology_to_capability_name.py) plus the CandidateProfile already in hand —
same "value already in hand" shape as classify_seniority taking an already-derived
years figure. Thresholds are exactly what both prior candidate-placement passes
validated by hand (Candidate Placement Findings.md's "Strong (class A/B, level ≥3)",
"Zero (evidence_class [] or level ≤1)").
"""

from enum import Enum, auto

from cv_scrape.state.candidate_profile import CandidateProfile

_STRONG_LEVEL_THRESHOLD = 3.0
_ZERO_LEVEL_THRESHOLD = 1.0


class CapabilityStrengthTag(Enum):
    STRONG = auto()
    PARTIAL = auto()
    ZERO = auto()


def classify_candidate_capability_strength(
    capability_name: str | None, profile: CandidateProfile
) -> CapabilityStrengthTag:
    if capability_name is None:
        return CapabilityStrengthTag.ZERO

    capability = next((c for c in profile.capabilities if c.name == capability_name), None)
    if capability is None or not capability.evidence_classes or capability.level_0_to_5 <= _ZERO_LEVEL_THRESHOLD:
        return CapabilityStrengthTag.ZERO
    if capability.level_0_to_5 >= _STRONG_LEVEL_THRESHOLD:
        return CapabilityStrengthTag.STRONG
    return CapabilityStrengthTag.PARTIAL
