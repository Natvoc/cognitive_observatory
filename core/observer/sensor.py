"""Sensors: the lossy bridge between World and Observer (spec §4.2)."""

import random
from abc import ABC, abstractmethod

from core.observer.observation import Observation
from core.world.ground_truth import GroundTruth


class Sensor(ABC):
    @abstractmethod
    def observe(self, ground_truth: GroundTruth) -> Observation:
        """Build an Observation from a GroundTruth, deliberately dropping
        anything not explicitly picked - most importantly causal_state."""


class PerfectSensor(Sensor):
    def observe(self, ground_truth: GroundTruth) -> Observation:
        return Observation(
            temperature=ground_truth.variables["temperature"],
            light=ground_truth.variables["light"],
            object_position=ground_truth.entities["object_position"],
        )


class NoisySensor(Sensor):
    def __init__(self, noise_std: float, seed: int) -> None:
        self._noise_std = noise_std
        self._rng = random.Random(seed)

    def observe(self, ground_truth: GroundTruth) -> Observation:
        temperature = ground_truth.variables["temperature"] + self._rng.gauss(0.0, self._noise_std)
        light = ground_truth.variables["light"] + self._rng.gauss(0.0, self._noise_std)
        return Observation(
            temperature=temperature,
            light=_clamp(light, 0.0, 1.0),
            object_position=ground_truth.entities["object_position"],
        )


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
