"""Abstract World: independent of any Observer.

Concrete worlds (e.g. environments/hidden_variable) implement the causal
rules; this base class only fixes the contract every World must satisfy.
"""

from abc import ABC, abstractmethod

from core.world.ground_truth import GroundTruth


class World(ABC):
    time: int

    @abstractmethod
    def step(self) -> None:
        """Advance the world by one timestep, mutating its internal state."""

    @abstractmethod
    def get_state(self) -> GroundTruth:
        """Return the complete, real state of the world (never partial)."""
