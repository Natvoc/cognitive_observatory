"""The hidden_variable environment (01_spec_proyecto.md §6).

hidden_state = A -> light tends to increase, object moves north (+y)
hidden_state = B -> light tends to decrease, object moves south (-y)

hidden_state itself is never exposed through Observation - only its
indirect effects on light and object_position are observable.
"""

import random
from dataclasses import dataclass
from typing import Literal

from core.world.base import World
from core.world.ground_truth import GroundTruth

HiddenState = Literal["A", "B"]
Position = tuple[int, int]


@dataclass
class HiddenVariableWorldConfig:
    seed: int
    hidden_state: HiddenState = "A"
    initial_temperature: float = 20.0
    initial_light: float = 0.5
    initial_position: Position = (0, 0)
    temperature_noise_std: float = 0.1
    light_noise_std: float = 0.05
    light_drift: float = 0.01


class HiddenVariableWorld(World):
    def __init__(self, config: HiddenVariableWorldConfig) -> None:
        self._config = config
        self._rng = random.Random(config.seed)
        self.time = 0
        self.hidden_state: HiddenState = config.hidden_state
        self.temperature = config.initial_temperature
        self.light = config.initial_light
        self.object_position = config.initial_position

    def step(self) -> None:
        self.time += 1
        direction = 1 if self.hidden_state == "A" else -1
        self.light = _clamp(
            self.light
            + direction * self._config.light_drift
            + self._rng.gauss(0.0, self._config.light_noise_std),
            0.0,
            1.0,
        )
        self.temperature += self._rng.gauss(0.0, self._config.temperature_noise_std)
        x, y = self.object_position
        self.object_position = (x, y + direction)

    def get_state(self) -> GroundTruth:
        return GroundTruth(
            timestamp=self.time,
            variables={"temperature": self.temperature, "light": self.light},
            entities={"object_position": self.object_position},
            causal_state={"hidden_state": self.hidden_state},
        )


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
