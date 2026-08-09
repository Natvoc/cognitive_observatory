"""Fase 7.1 - batch runner: convierte el proyecto de "simulador de una
arquitectura" a "buscador de arquitecturas" (spec §11).

Corre una grilla de arquitectura x sensor_noise, desatendido, vía la
misma API de Python que ya usan scripts/memory_sweep.py,
scripts/four_agent_comparison.py y scripts/attention_experiment.py - no
la CLI/YAML, para poder incluir attention_strategy sin tocar
core/experiments/loader.py.

Para cada nivel de ruido se corre un unico Experiment con las 7
arquitecturas como agentes, todas viendo exactamente el mismo mundo/seed
y la misma secuencia de observaciones (igual que
four_agent_comparison.py) - así la comparación es justa dentro de cada
nivel de ruido. Cada corrida se persiste en experiments/ como cualquier
otra; scripts/analyze_batch.py (Fase 7.2) las lee de ahí.
"""

from datetime import date
from pathlib import Path

from agents.memory import MemoryAgent
from agents.metacognitive import MetacognitiveAgent
from agents.predictive import PredictiveAgent
from agents.reactive import ReactiveAgent
from core.experiments.experiment import Experiment
from core.observer.agent import Observer
from core.observer.attention import SalienceAttention, UniformAttention
from core.observer.sensor import NoisySensor
from environments.hidden_variable import (
    HiddenState,
    HiddenVariableWorld,
    HiddenVariableWorldConfig,
)

SEED = 42
STEPS = 10_000
HIDDEN_STATE: HiddenState = "A"
SENSOR_NOISE_LEVELS = [0.3, 0.6, 0.9]


def _build_agents() -> dict[str, Observer]:
    return {
        "agent_0_reactive": ReactiveAgent(),
        "agent_1_memory_cap0": MemoryAgent(capacity=0),
        "agent_1_memory_cap50": MemoryAgent(capacity=50),
        "agent_1_memory_cap200": MemoryAgent(capacity=200),
        "agent_2_predictive_uniform": PredictiveAgent(attention=UniformAttention()),
        "agent_2_predictive_salience": PredictiveAgent(attention=SalienceAttention()),
        "agent_3_metacognitive": MetacognitiveAgent(seed=SEED + 1),
    }


def _noise_slug(noise_std: float) -> str:
    return f"{noise_std:.2f}".replace(".", "p")


def main() -> None:
    for noise_std in SENSOR_NOISE_LEVELS:
        world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=SEED, hidden_state=HIDDEN_STATE))
        sensor = NoisySensor(noise_std=noise_std, seed=SEED + 1)
        agents = _build_agents()
        experiment_name = f"batch_sensor_noise_{_noise_slug(noise_std)}"

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
                "sensor_noise_std": noise_std,
                "agents": list(agents),
            },
        )

        print(f"running {experiment_name} ({STEPS} steps, {len(agents)} agents)...")
        result = experiment.run()

        output_dir = Path("experiments") / f"{date.today().isoformat()}_{experiment_name}_{SEED}"
        result.save(output_dir)
        print(f"  -> {output_dir}")

    print("\nbatch done.")


if __name__ == "__main__":
    main()
