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

from core.actions.action import Action
from core.observer.agent import Observer
from core.observer.observation import Observation
from core.observer.sensor import Sensor
from core.world.base import World
from core.world.ground_truth import GroundTruth
from metrics.information import reality_model_divergence
from metrics.prediction import prediction_error


class BeliefRecord(TypedDict):
    predicted_hidden_state: str
    confidence: float


def _belief_distribution(agent: Observer, action: Action) -> dict[str, float]:
    """P(hidden_state=A/B) - from the agent's world model if it has one,
    otherwise the degenerate one-hot distribution implied by its hard guess."""
    world_model = getattr(agent, "world_model", None)
    if world_model is not None:
        return {"A": world_model.belief_a, "B": world_model.belief_b}
    guessed = action.name.removeprefix("guess_")
    return {"A": 1.0 if guessed == "A" else 0.0, "B": 1.0 if guessed == "B" else 0.0}


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
        metrics: dict[str, list[float]] = {name: [] for name in self.agents}
        divergence: dict[str, list[float]] = {name: [] for name in self.agents}

        for _ in range(self.steps):
            self.world.step()
            ground_truth = self.world.get_state()
            observation = self.sensor.observe(ground_truth)
            actual_hidden_state = ground_truth.causal_state["hidden_state"]

            ground_truth_trace.append(ground_truth)
            observation_trace.append(observation)

            for agent_name, agent in self.agents.items():
                action = agent.act(observation)
                distribution = _belief_distribution(agent, action)

                beliefs[agent_name].append(
                    BeliefRecord(
                        predicted_hidden_state=action.name.removeprefix("guess_"),
                        confidence=max(distribution.values()),
                    )
                )
                metrics[agent_name].append(prediction_error(distribution, actual_hidden_state))
                divergence[agent_name].append(
                    reality_model_divergence(distribution, actual_hidden_state)
                )

        return ExperimentResult(
            config=self.config,
            ground_truth_trace=ground_truth_trace,
            observation_trace=observation_trace,
            beliefs=beliefs,
            metrics=metrics,
            divergence=divergence,
        )


@dataclasses.dataclass
class ExperimentResult:
    config: dict[str, Any]
    ground_truth_trace: list[GroundTruth]
    observation_trace: list[Observation]
    beliefs: dict[str, list[BeliefRecord]]
    metrics: dict[str, list[float]]
    divergence: dict[str, list[float]]

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
        _write_json(output_dir / "metrics.json", self.metrics)
        _write_json(output_dir / "divergence.json", self.divergence)


def _write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
