from core.world import GroundTruth
from environments.hidden_variable import (
    HiddenState,
    HiddenVariableWorld,
    HiddenVariableWorldConfig,
)


def _run(seed: int, steps: int = 1000, hidden_state: HiddenState = "A") -> list[GroundTruth]:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=seed, hidden_state=hidden_state))
    trace: list[GroundTruth] = []
    for _ in range(steps):
        world.step()
        trace.append(world.get_state())
    return trace


def test_step_advances_time() -> None:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=1))
    assert world.time == 0
    world.step()
    assert world.time == 1


def test_1000_steps_deterministic_given_seed() -> None:
    trace_a = _run(seed=42)
    trace_b = _run(seed=42)
    assert len(trace_a) == 1000
    assert trace_a == trace_b


def test_different_seed_diverges() -> None:
    trace_a = _run(seed=42)
    trace_b = _run(seed=43)
    assert trace_a != trace_b


def test_hidden_state_never_leaks_outside_causal_state() -> None:
    world = HiddenVariableWorld(HiddenVariableWorldConfig(seed=1))
    world.step()
    state = world.get_state()
    assert "hidden_state" not in state.variables
    assert "hidden_state" not in state.entities
    assert state.causal_state["hidden_state"] == "A"


def test_hidden_state_a_pushes_light_and_position_up() -> None:
    trace = _run(seed=7, steps=1000, hidden_state="A")
    assert trace[-1].entities["object_position"][1] == 1000


def test_hidden_state_b_pushes_light_and_position_down() -> None:
    trace = _run(seed=7, steps=1000, hidden_state="B")
    assert trace[-1].entities["object_position"][1] == -1000
