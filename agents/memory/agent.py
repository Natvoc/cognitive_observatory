"""Agent 1 - Memory (spec §5): observation -> memory -> action.

Same threshold rule as Agent 0, but voting over the average light in a
working-memory buffer of recent observations instead of reacting to a
single one. With capacity=0 the buffer never retains anything, so the
average collapses to the latest observation and behavior is identical to
Agent 0 - that equivalence is the Fase 2 DoD for this agent.
"""

from core.actions.action import Action
from core.memory.working_memory import WorkingMemory
from core.observer.agent import Observer
from core.observer.observation import Observation


class MemoryAgent(Observer):
    def __init__(self, capacity: int, light_threshold: float = 0.5) -> None:
        self._memory: WorkingMemory[Observation] = WorkingMemory(capacity)
        self._light_threshold = light_threshold

    def act(self, observation: Observation) -> Action:
        self._memory.add(observation)
        remembered = list(self._memory) or [observation]
        average_light = sum(obs.light for obs in remembered) / len(remembered)

        if average_light >= self._light_threshold:
            return Action(name="guess_A")
        return Action(name="guess_B")
