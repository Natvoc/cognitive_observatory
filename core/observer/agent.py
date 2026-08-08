"""Observer: the base contract every agent architecture implements."""

from abc import ABC, abstractmethod

from core.actions.action import Action
from core.observer.observation import Observation


class Observer(ABC):
    @abstractmethod
    def act(self, observation: Observation) -> Action:
        """Turn the latest Observation into an Action."""
