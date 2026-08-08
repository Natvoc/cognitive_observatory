from agents.predictive import PredictiveAgent
from core.observer import NoisySensor, Observation, SalienceAttention, UniformAttention
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


def test_default_attention_is_a_no_op_equivalent_to_explicit_uniform_attention() -> None:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=10, hidden_state="A"))
    sensor = NoisySensor(noise_std=0.05, seed=11)
    default_agent = PredictiveAgent()
    explicit_agent = PredictiveAgent(attention=UniformAttention())

    for _ in range(2000):
        world.step()
        observation = sensor.observe(world.get_state())
        default_action = default_agent.act(observation)
        explicit_action = explicit_agent.act(observation)
        assert default_action == explicit_action
        assert default_agent.world_model.belief_a == explicit_agent.world_model.belief_a


def test_zero_attention_weight_leaves_belief_unchanged() -> None:
    # SalienceAttention gives zero weight to an unchanging signal - an
    # agent fed the exact same observation over and over should never
    # move off its 0.5/0.5 prior, unlike the default (Uniform) agent.
    agent = PredictiveAgent(attention=SalienceAttention(saturation_delta=0.1))
    still_observation = Observation(temperature=20.0, light=0.5, object_position=(0, 0))

    for _ in range(50):
        agent.act(still_observation)

    assert agent.world_model.belief_a == 0.5
