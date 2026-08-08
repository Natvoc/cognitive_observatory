"""Fase 3 - hito: Agent 0/1/2/3 compitiendo en el mismo experimento.

Corre los cuatro tipos de agente sobre el mismo mundo/seed y produce una
tabla comparativa de accuracy final + calibracion (spec §7: si el agente
dice "80% de confianza", acierta ~80% de las veces?).
"""

from collections.abc import Callable
from datetime import date
from pathlib import Path

from agents.memory import MemoryAgent
from agents.metacognitive import MetacognitiveAgent
from agents.predictive import PredictiveAgent
from agents.reactive import ReactiveAgent
from core.experiments.experiment import Experiment
from core.observer.agent import Observer
from core.observer.sensor import NoisySensor
from environments.hidden_variable import (
    HiddenState,
    HiddenVariableWorld,
    HiddenVariableWorldConfig,
)
from metrics import calibration

SEED = 42
STEPS = 10_000
HIDDEN_STATE: HiddenState = "A"
NOISE_STD = 0.3
FINAL_WINDOW = 1000

AGENT_FACTORIES: dict[str, Callable[[], Observer]] = {
    "agent_0_reactive": lambda: ReactiveAgent(),
    "agent_1_memory": lambda: MemoryAgent(capacity=50),
    "agent_2_predictive": lambda: PredictiveAgent(),
    "agent_3_metacognitive": lambda: MetacognitiveAgent(seed=SEED + 1),
}


def main() -> None:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=SEED, hidden_state=HIDDEN_STATE))
    sensor = NoisySensor(noise_std=NOISE_STD, seed=SEED + 1)
    agents = {name: factory() for name, factory in AGENT_FACTORIES.items()}

    experiment_name = "four_agent_comparison"
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
            "agents": list(AGENT_FACTORIES),
        },
    )
    result = experiment.run()

    output_dir = Path("experiments") / f"{date.today().isoformat()}_{experiment_name}_{SEED}"
    result.save(output_dir)

    truths = [gt.causal_state["hidden_state"] for gt in result.ground_truth_trace]
    window_truths = truths[-FINAL_WINDOW:]

    header = f"{'agent':>24} | {'accuracy (last 1000)':>22} | {'avg divergence (last 1000)':>28}"
    print(header)
    for agent_name in AGENT_FACTORIES:
        beliefs_window = result.beliefs[agent_name][-FINAL_WINDOW:]
        correct = [b["predicted_hidden_state"] == t for b, t in zip(beliefs_window, window_truths)]
        accuracy = sum(correct) / len(correct)
        avg_divergence = sum(result.divergence[agent_name][-FINAL_WINDOW:]) / FINAL_WINDOW
        print(f"{agent_name:>24} | {accuracy:>22.4f} | {avg_divergence:>28.4f}")

    print("\nCalibracion (confianza reportada vs. accuracy empirica, todo el run):")
    for agent_name in AGENT_FACTORIES:
        agent_beliefs = result.beliefs[agent_name]
        confidences = [record["confidence"] for record in agent_beliefs]
        correct_all = [
            record["predicted_hidden_state"] == truth
            for record, truth in zip(agent_beliefs, truths)
        ]
        buckets = calibration(confidences, correct_all, num_buckets=10)
        print(f"\n  {agent_name}:")
        for bucket in buckets:
            print(
                f"    [{bucket.bucket_lo:.1f}-{bucket.bucket_hi:.1f}) "
                f"n={bucket.count:>6}  avg_confidence={bucket.predicted_confidence_avg:.3f}  "
                f"empirical_accuracy={bucket.empirical_accuracy:.3f}"
            )

    print(f"\nfull run -> {output_dir}")


if __name__ == "__main__":
    main()
