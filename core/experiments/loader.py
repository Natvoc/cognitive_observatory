"""Builds an Experiment from a YAML config file (spec §9).

Fase 1 only needs to build the hidden_variable environment with a
perfect/noisy sensor and any mix of the reactive/predictive agents - no
plugin registry yet, that belongs to whenever more environments/agents
actually exist.
"""

from pathlib import Path
from typing import Any

import yaml

from agents.predictive import PredictiveAgent
from agents.reactive import ReactiveAgent
from core.experiments.experiment import Experiment
from core.observer.agent import Observer
from core.observer.sensor import NoisySensor, PerfectSensor, Sensor
from environments.hidden_variable import HiddenVariableWorld, HiddenVariableWorldConfig


def load_experiment(config_path: Path) -> Experiment:
    with config_path.open(encoding="utf-8") as f:
        config: dict[str, Any] = yaml.safe_load(f)

    seed: int = config["seed"]

    return Experiment(
        name=config["name"],
        seed=seed,
        steps=config["steps"],
        world=_build_world(config["world"], seed),
        sensor=_build_sensor(config["sensor"], seed),
        agents=_build_agents(config["agents"]),
        config=config,
    )


def _build_world(world_config: dict[str, Any], seed: int) -> HiddenVariableWorld:
    return HiddenVariableWorld(HiddenVariableWorldConfig(seed=seed, **world_config))


def _build_sensor(sensor_config: dict[str, Any], seed: int) -> Sensor:
    sensor_type = sensor_config.get("type", "perfect")
    if sensor_type == "perfect":
        return PerfectSensor()
    if sensor_type == "noisy":
        return NoisySensor(noise_std=sensor_config["noise_std"], seed=seed)
    raise ValueError(f"unknown sensor type: {sensor_type!r}")


def _build_agents(agents_config: list[dict[str, Any]]) -> dict[str, Observer]:
    agents: dict[str, Observer] = {}
    for entry in agents_config:
        agent_type = entry["type"]
        name = entry.get("name", agent_type)
        if agent_type == "reactive":
            agents[name] = ReactiveAgent()
        elif agent_type == "predictive":
            agents[name] = PredictiveAgent()
        else:
            raise ValueError(f"unknown agent type: {agent_type!r}")
    return agents
