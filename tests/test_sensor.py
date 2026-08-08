import dataclasses

from core.observer import NoisySensor, Observation, PerfectSensor
from core.world import GroundTruth
from environments.hidden_variable import HiddenVariableWorld, HiddenVariableWorldConfig


def _ground_truth(seed: int = 1) -> GroundTruth:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=seed))
    world.step()
    return world.get_state()


def test_observation_fields_never_include_hidden_state() -> None:
    field_names = {f.name for f in dataclasses.fields(Observation)}
    assert not any("hidden" in name for name in field_names)


def test_perfect_sensor_observation_has_no_hidden_trace() -> None:
    obs = PerfectSensor().observe(_ground_truth())
    assert not hasattr(obs, "hidden_state")
    assert not hasattr(obs, "hidden_variable")
    assert "hidden" not in str(dataclasses.asdict(obs))


def test_noisy_sensor_observation_has_no_hidden_trace() -> None:
    obs = NoisySensor(noise_std=0.2, seed=99).observe(_ground_truth())
    assert not hasattr(obs, "hidden_state")
    assert "hidden" not in str(dataclasses.asdict(obs))


def test_noisy_sensor_deterministic_given_seed() -> None:
    ground_truth = _ground_truth()
    obs_a = NoisySensor(noise_std=0.2, seed=99).observe(ground_truth)
    obs_b = NoisySensor(noise_std=0.2, seed=99).observe(ground_truth)
    assert obs_a == obs_b


def test_noisy_sensor_adds_noise_relative_to_perfect() -> None:
    ground_truth = _ground_truth()
    perfect = PerfectSensor().observe(ground_truth)
    noisy = NoisySensor(noise_std=0.5, seed=99).observe(ground_truth)
    assert perfect.temperature != noisy.temperature
