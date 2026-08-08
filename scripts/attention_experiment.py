"""Fase 4.2 - experimento de atencion: mismos datos crudos, comparar
modelos internos resultantes segun como se atienden.

Dos PredictiveAgent reciben exactamente la misma secuencia de
observaciones (mismo mundo/seed/sensor, en el mismo Experiment) - uno con
UniformAttention (default, sin atencion real) y otro con
SalienceAttention. La comparacion es sobre los beliefs resultantes en el
tiempo, no solo sobre accuracy final (spec §4.3).
"""

from datetime import date
from pathlib import Path

from agents.predictive import PredictiveAgent
from core.experiments.experiment import BeliefRecord, Experiment
from core.observer.agent import Observer
from core.observer.attention import SalienceAttention
from core.observer.sensor import NoisySensor
from environments.hidden_variable import (
    HiddenState,
    HiddenVariableWorld,
    HiddenVariableWorldConfig,
)

SEED = 42
STEPS = 10_000
HIDDEN_STATE: HiddenState = "A"
NOISE_STD = 0.3
# Set well above the typical noise-driven step-to-step jump (~noise_std),
# so most observations only get partial weight instead of saturating to
# 1.0 like they would with a small saturation_delta.
SALIENCE_SATURATION_DELTA = 0.6


def _belief_a_trace(agent_beliefs: list[BeliefRecord]) -> list[float]:
    trace = []
    for record in agent_beliefs:
        confidence = record["confidence"]
        belief_a = confidence if record["predicted_hidden_state"] == "A" else 1.0 - confidence
        trace.append(belief_a)
    return trace


def main() -> None:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=SEED, hidden_state=HIDDEN_STATE))
    sensor = NoisySensor(noise_std=NOISE_STD, seed=SEED + 1)

    agents: dict[str, Observer] = {
        "uniform_attention": PredictiveAgent(),
        "salience_attention": PredictiveAgent(
            attention=SalienceAttention(saturation_delta=SALIENCE_SATURATION_DELTA)
        ),
    }

    experiment_name = "attention_experiment"
    experiment = Experiment(
        name=experiment_name,
        seed=SEED,
        steps=STEPS,
        world=world,
        sensor=sensor,
        agents=agents,
        config={
            "name": experiment_name,
            "seed": SEED,
            "steps": STEPS,
            "hidden_state": HIDDEN_STATE,
            "sensor_noise_std": NOISE_STD,
            "salience_saturation_delta": SALIENCE_SATURATION_DELTA,
        },
    )
    result = experiment.run()

    output_dir = Path("experiments") / f"{date.today().isoformat()}_{experiment_name}_{SEED}"
    result.save(output_dir)

    uniform_trace = _belief_a_trace(result.beliefs["uniform_attention"])
    salience_trace = _belief_a_trace(result.beliefs["salience_attention"])

    belief_diffs = [abs(u - s) for u, s in zip(uniform_trace, salience_trace)]
    max_diff = max(belief_diffs)
    max_diff_step = belief_diffs.index(max_diff)
    mean_diff_overall = sum(belief_diffs) / len(belief_diffs)
    mean_diff_first_100 = sum(belief_diffs[:100]) / 100

    guess_disagreements = sum(
        u["predicted_hidden_state"] != s["predicted_hidden_state"]
        for u, s in zip(result.beliefs["uniform_attention"], result.beliefs["salience_attention"])
    )

    print(f"belief_a final: uniform={uniform_trace[-1]:.4f}  salience={salience_trace[-1]:.4f}")
    print(f"mean |belief_a diff| over the run: {mean_diff_overall:.4f}")
    print(f"mean |belief_a diff| over the first 100 steps: {mean_diff_first_100:.4f}")
    print(f"max |belief_a diff|: {max_diff:.4f} at step {max_diff_step}")
    print(
        f"  uniform belief_a there = {uniform_trace[max_diff_step]:.4f}, "
        f"salience belief_a there = {salience_trace[max_diff_step]:.4f}"
    )
    print(f"guess disagreements (hard guess_A/guess_B differs): {guess_disagreements}/{STEPS}")
    print(f"\nfull run -> {output_dir}")


if __name__ == "__main__":
    main()
