import pytest

from cv_scrape.interaction.parse_candidate_profile import RejectedCandidateProfile, parse_candidate_profile
from cv_scrape.state.candidate_profile import CandidateCapability

_VALID_YAML = """
candidate_profile:
  capability_model:
    capabilities:
      Python:
        level_0_to_5: 4
        evidence_class: ["A", "B"]
      dbt:
        level_0_to_5: 0
        evidence_class: []
"""


def test_valid_profile_is_parsed(tmp_path):
    path = tmp_path / "candidate.yaml"
    path.write_text(_VALID_YAML)

    profile = parse_candidate_profile(path)

    assert CandidateCapability(name="Python", level_0_to_5=4.0, evidence_classes=("A", "B")) in profile.capabilities
    assert CandidateCapability(name="dbt", level_0_to_5=0.0, evidence_classes=()) in profile.capabilities


def test_missing_file_is_rejected(tmp_path):
    with pytest.raises(RejectedCandidateProfile):
        parse_candidate_profile(tmp_path / "does-not-exist.yaml")


def test_missing_capability_model_is_rejected(tmp_path):
    path = tmp_path / "candidate.yaml"
    path.write_text("candidate_profile:\n  target: {}\n")

    with pytest.raises(RejectedCandidateProfile):
        parse_candidate_profile(path)
