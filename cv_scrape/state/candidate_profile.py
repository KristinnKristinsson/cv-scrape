"""State: the candidate's evidence-graded capability profile — parsed from
candidate.yaml's `capability_model.capabilities` section by
interaction/parse_candidate_profile.py. Nothing else in that file (target
constraints, market positioning, salary floor, work authorization, self-assessed
gaps) is represented here — this project's code only ever reasons over the
capability list, not the rest of the candidate's personal data.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateCapability:
    name: str
    level_0_to_5: float
    evidence_classes: tuple[str, ...] = ()


@dataclass(frozen=True)
class CandidateProfile:
    capabilities: tuple[CandidateCapability, ...] = ()
