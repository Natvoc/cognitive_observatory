"""Fase 2.3 - barrido de memory_capacity sobre el experimento hidden_variable.

Corre el mismo mundo/seed con distintos memory_capacity, persiste cada
corrida bajo experiments/, y junta sus metrics.json/beliefs.json en una
tabla de accuracy final vs. capacity - ver 01_spec_proyecto.md §8
(hipotesis de overfitting por memoria excesiva). El resultado puede
confirmar o refutar la hipotesis; lo que importa es que el barrido corrio
y produjo el dato.
"""

import csv
from datetime import date
from pathlib import Path

from agents.memory import MemoryAgent
from core.experiments.experiment import Experiment, ExperimentResult
from core.observer.sensor import NoisySensor
from environments.hidden_variable import (
    HiddenState,
    HiddenVariableWorld,
    HiddenVariableWorldConfig,
)

SEED = 42
STEPS = 10_000
HIDDEN_STATE: HiddenState = "A"
# Sensor noise deliberately high: with the default 0.05 the raw signal is
# already clean enough that every capacity converges to ~perfect accuracy,
# leaving nothing for memory to average out. A noisier sensor is what
# actually exercises the "does more memory help" question.
NOISE_STD = 0.3
MEMORY_CAPACITIES = [0, 10, 50, 100, 500]
EARLY_WINDOW = (0, 100)
FINAL_WINDOW = 1000


def _run_one(capacity: int) -> tuple[str, ExperimentResult]:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=SEED, hidden_state=HIDDEN_STATE))
    sensor = NoisySensor(noise_std=NOISE_STD, seed=SEED + 1)
    agent_name = f"agent_1_memory_capacity_{capacity}"
    experiment_name = f"memory_sweep_capacity_{capacity}"

    experiment = Experiment(
        name=experiment_name,
        seed=SEED,
        steps=STEPS,
        world=world,
        sensor=sensor,
        agents={agent_name: MemoryAgent(capacity=capacity)},
        config={
            "name": experiment_name,
            "seed": SEED,
            "steps": STEPS,
            "hidden_state": HIDDEN_STATE,
            "sensor_noise_std": NOISE_STD,
            "memory_capacity": capacity,
        },
    )
    result = experiment.run()

    output_dir = Path("experiments") / f"{date.today().isoformat()}_{experiment_name}_{SEED}"
    result.save(output_dir)

    return agent_name, result


def _window_accuracy(result: ExperimentResult, agent_name: str, lo: int, hi: int) -> float:
    predictions = result.beliefs[agent_name][lo:hi]
    ground_truth_window = result.ground_truth_trace[lo:hi]
    truths: list[str] = [gt.causal_state["hidden_state"] for gt in ground_truth_window]
    correct = sum(p["predicted_hidden_state"] == t for p, t in zip(predictions, truths))
    return correct / len(truths)


def main() -> None:
    rows = []
    for capacity in MEMORY_CAPACITIES:
        agent_name, result = _run_one(capacity)
        early_accuracy = _window_accuracy(result, agent_name, *EARLY_WINDOW)
        final_accuracy = _window_accuracy(result, agent_name, -FINAL_WINDOW, STEPS)
        final_avg_error = sum(result.metrics[agent_name][-FINAL_WINDOW:]) / FINAL_WINDOW
        rows.append(
            {
                "memory_capacity": capacity,
                "early_accuracy_first_100": early_accuracy,
                "final_accuracy_last_1000": final_accuracy,
                "final_avg_error_last_1000": final_avg_error,
            }
        )

    header = (
        f"{'capacity':>10} | {'accuracy (first 100)':>22} | "
        f"{'accuracy (last 1000)':>22} | {'avg error (last 1000)':>22}"
    )
    print(header)
    for row in rows:
        print(
            f"{row['memory_capacity']:>10} | {row['early_accuracy_first_100']:>22.4f} | "
            f"{row['final_accuracy_last_1000']:>22.4f} | {row['final_avg_error_last_1000']:>22.4f}"
        )

    summary_path = Path("experiments") / f"{date.today().isoformat()}_memory_sweep_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "memory_capacity",
            "early_accuracy_first_100",
            "final_accuracy_last_1000",
            "final_avg_error_last_1000",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nsummary -> {summary_path}")


if __name__ == "__main__":
    main()
