from agents.memory import MemoryAgent
from agents.reactive import ReactiveAgent
from core.observer import NoisySensor
from environments.hidden_variable import HiddenVariableWorld, HiddenVariableWorldConfig


def test_capacity_zero_matches_reactive_agent_step_by_step() -> None:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=1, hidden_state="A"))
    sensor = NoisySensor(noise_std=0.3, seed=2)
    reactive = ReactiveAgent()
    memory_agent = MemoryAgent(capacity=0)

    for _ in range(500):
        world.step()
        observation = sensor.observe(world.get_state())
        assert memory_agent.act(observation) == reactive.act(observation)


def test_high_capacity_converges_faster_than_reactive_under_noise() -> None:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=3, hidden_state="A"))
    sensor = NoisySensor(noise_std=0.3, seed=4)
    reactive = ReactiveAgent()
    memory_agent = MemoryAgent(capacity=50)

    reactive_correct = 0
    memory_correct = 0
    steps = 2000
    for _ in range(steps):
        world.step()
        observation = sensor.observe(world.get_state())
        reactive_correct += reactive.act(observation).name == "guess_A"
        memory_correct += memory_agent.act(observation).name == "guess_A"

    reactive_accuracy = reactive_correct / steps
    memory_accuracy = memory_correct / steps
    assert memory_accuracy > reactive_accuracy
