from agents.reactive import ReactiveAgent
from core.observer import NoisySensor, Observation
from environments.hidden_variable import HiddenVariableWorld, HiddenVariableWorldConfig


def test_reactive_agent_runs_1000_steps_and_produces_one_action_per_step() -> None:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=1, hidden_state="A"))
    sensor = NoisySensor(noise_std=0.1, seed=2)
    agent = ReactiveAgent()

    actions = []
    for _ in range(1000):
        world.step()
        observation = sensor.observe(world.get_state())
        actions.append(agent.act(observation))

    assert len(actions) == 1000
    assert all(action.name in ("guess_A", "guess_B") for action in actions)


def test_reactive_agent_rule_depends_only_on_last_observation() -> None:
    agent = ReactiveAgent(light_threshold=0.5)

    high_light = Observation(temperature=20.0, light=0.9, object_position=(0, 0))
    low_light = Observation(temperature=20.0, light=0.1, object_position=(0, 0))

    assert agent.act(high_light).name == "guess_A"
    assert agent.act(low_light).name == "guess_B"
