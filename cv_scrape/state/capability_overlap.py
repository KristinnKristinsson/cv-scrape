"""State: the reduced result of comparing one posting's technologies/cloud platforms
against the candidate's capability profile — produced by
logic/summarize_capability_overlap.py. A multi-field record, not a bare Enum, so it
lives here rather than colocated with its producing logic, same as
state/framework_signals.py.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilityOverlap:
    strong_matches: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    partial_matches: tuple[str, ...] = ()
