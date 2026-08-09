import pytest

from dashboard.api.agent_info import AgentTypeNotFoundError, get_agent_self_model


def test_get_agent_self_model_returns_metacognitive_description() -> None:
    description = get_agent_self_model("metacognitive")

    assert description.capabilities
    assert description.limitations
    assert any("hidden_state" in limitation for limitation in description.limitations)


def test_get_agent_self_model_raises_for_unknown_type() -> None:
    with pytest.raises(AgentTypeNotFoundError):
        get_agent_self_model("does_not_exist")
