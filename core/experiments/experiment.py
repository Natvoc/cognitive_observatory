"""Experiment Runner (spec §9): reproducible, seeded end-to-end runs.

The seed is mandatory - re-running an Experiment with the same seed must
produce identical GroundTruth/Observation traces (World and Sensor are
themselves deterministic given a seed) and therefore identical persisted
JSON.
"""

import dataclasses
import json
from pathlib import Path
from typing import Any, TypedDict

from core.observer.agent import Observer
from core.observer.observation import Observation
from core.observer.sensor import Sensor
from core.world.base import World
from core.world.ground_truth import GroundTruth


class BeliefRecord(TypedDict):
    predicted_hidden_state: str
    confidence: float | None


@dataclasses.dataclass
class Experiment:
    name: str
    seed: int
    steps: int
    world: World
    sensor: Sensor
    agents: dict[str, Observer]
    config: dict[str, Any]

    def run(self) -> "ExperimentResult":
        ground_truth_trace: list[GroundTruth] = []
        observation_trace: list[Observation] = []
        beliefs: dict[str, list[BeliefRecord]] = {name: [] for name in self.agents}

        for _ in range(self.steps):
            self.world.step()
            ground_truth = self.world.get_state()
            observation = self.sensor.observe(ground_truth)

            ground_truth_trace.append(ground_truth)
            observation_trace.append(observation)

            for agent_name, agent in self.agents.items():
                action = agent.act(observation)
                predicted_hidden_state = action.name.removeprefix("guess_")
                world_model = getattr(agent, "world_model", None)
                confidence = (
                    max(world_model.belief_a, world_model.belief_b)
                    if world_model is not None
                    else None
                )
                beliefs[agent_name].append(
                    BeliefRecord(
                        predicted_hidden_state=predicted_hidden_state,
                        confidence=confidence,
                    )
                )

        return ExperimentResult(
            config=self.config,
            ground_truth_trace=ground_truth_trace,
            observation_trace=observation_trace,
            beliefs=beliefs,
        )


@dataclasses.dataclass
class ExperimentResult:
    config: dict[str, Any]
    ground_truth_trace: list[GroundTruth]
    observation_trace: list[Observation]
    beliefs: dict[str, list[BeliefRecord]]

    def save(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        _write_json(output_dir / "config.json", self.config)
        _write_json(
            output_dir / "ground_truth.json",
            [dataclasses.asdict(gt) for gt in self.ground_truth_trace],
        )
        _write_json(
            output_dir / "observations.json",
            [dataclasses.asdict(obs) for obs in self.observation_trace],
        )
        _write_json(output_dir / "beliefs.json", self.beliefs)


def _write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
