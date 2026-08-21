"""Logic: reduce a posting's technologies + cloud platforms, against the candidate's
profile, into one summary of what overlaps and what blocks. Pure decision over
values already in hand (JobSignals, CandidateProfile) via the already-derived
per-technology name mapping and strength classification — same "many small facts in
hand, one reduced record" shape as summarize_rate_limit_signals.py.

Two rules here are direct fixes of flaws found in the two prior hand/scratch-script
placement passes (Candidate Placement Findings.md):

- Dedup by resolved capability name, not raw keyword — "postgres" and "postgresql"
  both resolve to PostgreSQL and must count once, not twice.
- A blocker requires TechnologyRequirement.strength to be REQUIRED or PREFERRED —
  a bare MENTIONED zero-evidence technology is not a blocker. This is the resolved
  Scala finding (8 of 27 REQUIRED+PREFERRED vs. dbt's 24 of 35), now enforced in code
  instead of re-derived by hand a third time.

cloud_platforms entries only ever contribute to strong_matches, never to blockers —
extract_cloud_platforms_mentioned.py carries no requirement-strength data (that
extension was explicitly deferred when requirement-strength was built), so treating
a zero-evidence cloud mention as a blocker would repeat the exact mistake
requirement-strength was built to fix, just cloud-side.
"""

from cv_scrape.logic.classify_candidate_capability_strength import (
    CapabilityStrengthTag,
    classify_candidate_capability_strength,
)
from cv_scrape.logic.map_technology_to_capability_name import map_technology_to_capability_name
from cv_scrape.state.candidate_profile import CandidateProfile
from cv_scrape.state.capability_overlap import CapabilityOverlap
from cv_scrape.state.job_signals import JobSignals

_BLOCKING_STRENGTHS = ("REQUIRED", "PREFERRED")


def summarize_capability_overlap(job_signals: JobSignals, profile: CandidateProfile) -> CapabilityOverlap:
    strong_matches: set[str] = set()
    blockers: set[str] = set()
    partial_matches: set[str] = set()

    for requirement in job_signals.technologies:
        capability_name = map_technology_to_capability_name(requirement.technology)
        tag = classify_candidate_capability_strength(capability_name, profile)

        if tag is CapabilityStrengthTag.STRONG:
            strong_matches.add(capability_name)
        elif tag is CapabilityStrengthTag.PARTIAL:
            partial_matches.add(capability_name)
        elif capability_name is not None and requirement.strength in _BLOCKING_STRENGTHS:
            blockers.add(capability_name)

    for platform in job_signals.cloud_platforms:
        capability_name = map_technology_to_capability_name(platform)
        tag = classify_candidate_capability_strength(capability_name, profile)
        if tag is CapabilityStrengthTag.STRONG:
            strong_matches.add(capability_name)
        elif tag is CapabilityStrengthTag.PARTIAL:
            partial_matches.add(capability_name)

    return CapabilityOverlap(
        strong_matches=tuple(sorted(strong_matches)),
        blockers=tuple(sorted(blockers)),
        partial_matches=tuple(sorted(partial_matches)),
    )
