"""Agent 0 - Reactive (spec §5): observation -> rule -> action, no memory, no model."""

from core.actions.action import Action
from core.observer.agent import Observer
from core.observer.observation import Observation


class ReactiveAgent(Observer):
    def __init__(self, light_threshold: float = 0.5) -> None:
        self._light_threshold = light_threshold

    def act(self, observation: Observation) -> Action:
        if observation.light >= self._light_threshold:
            return Action(name="guess_A")
        return Action(name="guess_B")
