"""Interaction: boundary for the user's own candidate.yaml file. Same category as
the CV-parsing boundary this replaces (structure.md's "the user's own file" case) —
uncontrolled shape that must be validated/rejected before a CandidateProfile is
trusted downstream. Only capability_model.capabilities is extracted: nothing else in
the file (target constraints, market positioning, salary floor, work authorization,
self-assessed gaps) is read by code, so the genuinely sensitive fields never leave
the file at all — consistent with why the file is gitignored in the first place.
"""

from pathlib import Path

import yaml

from cv_scrape.state.candidate_profile import CandidateCapability, CandidateProfile

DEFAULT_CANDIDATE_PROFILE_PATH = Path(__file__).resolve().parent.parent.parent / "candidate.yaml"


class RejectedCandidateProfile(Exception):
    """Raised when candidate.yaml is missing or doesn't hold a usable capability model."""


def parse_candidate_profile(path: Path = DEFAULT_CANDIDATE_PROFILE_PATH) -> CandidateProfile:
    if not path.exists():
        raise RejectedCandidateProfile(f"{path}: no such file")

    try:
        document = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise RejectedCandidateProfile(f"{path}: not valid YAML ({exc})") from exc

    try:
        capabilities = document["candidate_profile"]["capability_model"]["capabilities"]
    except (KeyError, TypeError) as exc:
        raise RejectedCandidateProfile(
            f"{path}: missing candidate_profile.capability_model.capabilities"
        ) from exc

    if not isinstance(capabilities, dict):
        raise RejectedCandidateProfile(f"{path}: capability_model.capabilities must be a mapping")

    return CandidateProfile(
        capabilities=tuple(
            CandidateCapability(
                name=name,
                level_0_to_5=float(entry.get("level_0_to_5", 0)),
                evidence_classes=tuple(entry.get("evidence_class", ())),
            )
            for name, entry in capabilities.items()
        )
    )
