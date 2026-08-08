"""Attention (spec §4.3): available information != processed information.

AttentionSystem decides how much of an Observation actually gets used,
as a continuous weight in [0, 1] rather than a hard include/exclude
choice - 0 means "didn't process this at all", 1 means "fully processed".
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.observer.observation import Observation


@dataclass(frozen=True)
class AttentionResult:
    weight: float


class AttentionSystem(ABC):
    @abstractmethod
    def select(
        self, observation: Observation, previous_observation: Observation | None
    ) -> AttentionResult:
        """previous_observation is None on the very first call."""


class UniformAttention(AttentionSystem):
    """Baseline: every observation gets full weight - equivalent to not
    having attention at all."""

    def select(
        self, observation: Observation, previous_observation: Observation | None
    ) -> AttentionResult:
        return AttentionResult(weight=1.0)


class SalienceAttention(AttentionSystem):
    """Weighs by how much `light` changed since the previous observation.
    A change of `saturation_delta` or more gets full weight; the very
    first observation (nothing to compare against yet) also gets full
    weight."""

    def __init__(self, saturation_delta: float = 0.1) -> None:
        self._saturation_delta = saturation_delta

    def select(
        self, observation: Observation, previous_observation: Observation | None
    ) -> AttentionResult:
        if previous_observation is None:
            return AttentionResult(weight=1.0)
        delta = abs(observation.light - previous_observation.light)
        return AttentionResult(weight=min(delta / self._saturation_delta, 1.0))
