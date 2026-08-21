from cv_scrape.logic.classify_candidate_capability_strength import (
    CapabilityStrengthTag,
    classify_candidate_capability_strength,
)
from cv_scrape.state.candidate_profile import CandidateCapability, CandidateProfile

_PROFILE = CandidateProfile(
    capabilities=(
        CandidateCapability(name="Python", level_0_to_5=4.0, evidence_classes=("A", "B")),
        CandidateCapability(name="PostgreSQL", level_0_to_5=2.0, evidence_classes=("C",)),
        CandidateCapability(name="Terraform", level_0_to_5=0.5, evidence_classes=("E",)),
        CandidateCapability(name="dbt", level_0_to_5=3.0, evidence_classes=()),
    )
)


def test_high_level_capability_is_strong():
    assert classify_candidate_capability_strength("Python", _PROFILE) is CapabilityStrengthTag.STRONG


def test_low_level_capability_is_zero():
    assert classify_candidate_capability_strength("Terraform", _PROFILE) is CapabilityStrengthTag.ZERO


def test_mid_level_capability_is_partial():
    assert classify_candidate_capability_strength("PostgreSQL", _PROFILE) is CapabilityStrengthTag.PARTIAL


def test_empty_evidence_classes_overrides_level():
    assert classify_candidate_capability_strength("dbt", _PROFILE) is CapabilityStrengthTag.ZERO


def test_none_capability_name_is_zero():
    assert classify_candidate_capability_strength(None, _PROFILE) is CapabilityStrengthTag.ZERO


def test_capability_absent_from_profile_is_zero():
    assert classify_candidate_capability_strength("Scala", _PROFILE) is CapabilityStrengthTag.ZERO
