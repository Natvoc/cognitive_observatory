"""GroundTruth: the complete, real state of a World at a given timestep.

The Observer never receives this directly (see 01_spec_proyecto.md §2) -
GroundTruth exists so experiments can compare what the observer believes
against what actually happened.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GroundTruth:
    timestamp: int
    variables: dict[str, Any]
    entities: dict[str, Any]
    causal_state: dict[str, Any]
