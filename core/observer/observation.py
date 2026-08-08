"""Observation: what a Sensor hands to an Observer.

Fields are fixed and explicit on purpose - there is no passthrough of
GroundTruth.causal_state, so hidden variables cannot leak in even by
accident (see 01_spec_proyecto.md §2).
"""

from dataclasses import dataclass

Position = tuple[int, int]


@dataclass(frozen=True)
class Observation:
    temperature: float
    light: float
    object_position: Position
