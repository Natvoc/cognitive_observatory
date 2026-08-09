"""Static, architecture-level agent metadata (roadmap Fase 6.3).

Self-model capabilities/limitations don't vary per run - they're fixed
by the agent's architecture (spec §5.1) - so this reads them straight
from the agent class via its self_model_description() classmethod,
never from a persisted run, and never touches Experiment.run().
"""

from agents.metacognitive import MetacognitiveAgent, SelfModelDescription

AGENT_SELF_MODELS: dict[str, SelfModelDescription] = {
    "metacognitive": MetacognitiveAgent.self_model_description(),
}


class AgentTypeNotFoundError(Exception):
    def __init__(self, agent_type: str) -> None:
        super().__init__(f"no self-model description for agent type: {agent_type!r}")
        self.agent_type = agent_type


def get_agent_self_model(agent_type: str) -> SelfModelDescription:
    if agent_type not in AGENT_SELF_MODELS:
        raise AgentTypeNotFoundError(agent_type)
    return AGENT_SELF_MODELS[agent_type]
