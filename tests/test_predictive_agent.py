from agents.predictive import PredictiveAgent
from core.observer import NoisySensor
from environments.hidden_variable import HiddenState, HiddenVariableWorld, HiddenVariableWorldConfig


def _run_belief_trace(seed: int, hidden_state: HiddenState, steps: int = 10_000) -> list[float]:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=seed, hidden_state=hidden_state))
    sensor = NoisySensor(noise_std=0.05, seed=seed + 1)
    agent = PredictiveAgent()

    belief_trace = []
    for _ in range(steps):
        world.step()
        observation = sensor.observe(world.get_state())
        agent.act(observation)
        belief_trace.append(agent.world_model.belief_a)
    return belief_trace


def test_predict_rejects_horizon_other_than_one() -> None:
    agent = PredictiveAgent()
    try:
        agent.predict(horizon=5)
    except NotImplementedError:
        pass
    else:
        raise AssertionError("expected NotImplementedError for horizon != 1")


def test_belief_converges_to_correct_hidden_state_a() -> None:
    trace = _run_belief_trace(seed=10, hidden_state="A")
    assert trace[-1] > 0.95


def test_belief_converges_to_correct_hidden_state_b() -> None:
    trace = _run_belief_trace(seed=10, hidden_state="B")
    assert trace[-1] < 0.05


def test_belief_is_less_confident_early_than_late() -> None:
    trace = _run_belief_trace(seed=10, hidden_state="A")
    assert trace[9] < trace[-1]
