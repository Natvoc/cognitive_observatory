import math

from agents.predictive import PredictiveAgent
from core.observer import Observation, SalienceAttention, UniformAttention


def _obs(light: float) -> Observation:
    return Observation(temperature=20.0, light=light, object_position=(0, 0))


def test_uniform_attention_always_full_weight() -> None:
    attention = UniformAttention()
    assert attention.select(_obs(0.5), None).weight == 1.0
    assert attention.select(_obs(0.9), _obs(0.1)).weight == 1.0


def test_salience_attention_first_observation_gets_full_weight() -> None:
    attention = SalienceAttention()
    assert attention.select(_obs(0.5), None).weight == 1.0


def test_salience_attention_no_change_gets_zero_weight() -> None:
    attention = SalienceAttention(saturation_delta=0.1)
    result = attention.select(_obs(0.5), _obs(0.5))
    assert result.weight == 0.0


def test_salience_attention_weight_scales_with_delta_up_to_saturation() -> None:
    attention = SalienceAttention(saturation_delta=0.1)

    small_change = attention.select(_obs(0.55), _obs(0.5))
    assert math.isclose(small_change.weight, 0.5)

    saturating_change = attention.select(_obs(0.7), _obs(0.5))
    assert saturating_change.weight == 1.0


def test_same_raw_observations_yield_different_beliefs_under_different_attention() -> None:
    # Fase 4.2 DoD: two observers fed the exact same raw data end up with
    # different internal models purely because of how they attend to it.
    uniform_agent = PredictiveAgent()
    salience_agent = PredictiveAgent(attention=SalienceAttention(saturation_delta=0.6))

    observations = [_obs(light) for light in [0.55, 0.55, 0.55, 0.95, 0.55, 0.55, 0.55]]
    for observation in observations:
        uniform_agent.act(observation)
        salience_agent.act(observation)

    assert uniform_agent.world_model.belief_a != salience_agent.world_model.belief_a
