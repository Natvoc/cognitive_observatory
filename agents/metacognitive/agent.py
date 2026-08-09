"""Agent 3 - Metacognitive (spec §5): observation -> world model -> belief
-> confidence (SelfModel) -> action.

Same Bayesian belief update as Agent 2, but before acting it checks its
own confidence via SelfModel.evaluate_belief(): above the threshold it
exploits (guesses the higher-probability state, like Agent 2); below it,
it explores - samples a guess proportional to its own belief distribution
instead of blindly committing to whichever state is even slightly ahead.
"""

import random
from dataclasses import dataclass

from core.actions.action import Action
from core.cognition.likelihood import gaussian_likelihood
from core.cognition.prediction import PredictedState
from core.cognition.self_model import BeliefEvaluation, SelfModel
from core.cognition.world_model import WorldModel
from core.observer.agent import Observer
from core.observer.observation import Observation

BELIEF_ID = "hidden_state_is_a"


@dataclass(frozen=True)
class SelfModelDescription:
    capabilities: list[str]
    limitations: list[str]


class MetacognitiveAgent(Observer):
    def __init__(
        self,
        seed: int,
        confidence_threshold: float = 0.7,
        light_mean_a: float = 0.75,
        light_mean_b: float = 0.25,
        light_std: float = 0.2,
    ) -> None:
        self.world_model = WorldModel()
        self.self_model = SelfModel()
        self._declare_self_knowledge()
        self._rng = random.Random(seed)
        self._confidence_threshold = confidence_threshold
        self._light_mean_a = light_mean_a
        self._light_mean_b = light_mean_b
        self._light_std = light_std

    @classmethod
    def self_model_description(cls) -> SelfModelDescription:
        """Fixed, designer-known facts about this architecture (spec
        §5.1) - a classmethod because this metadata never depends on
        instance state (seed, thresholds, etc.), so callers who only
        want to know "what can this architecture do" shouldn't need to
        construct an agent to find out. This is the single source of
        truth _declare_self_knowledge() below feeds into a live
        SelfModel."""
        return SelfModelDescription(
            capabilities=[
                "maintains a probabilistic belief over hidden_state",
                "adjusts confidence-driven exploration vs. exploitation",
            ],
            limitations=[
                "hidden_state inaccessible: never present in Observation",
            ],
        )

    def _declare_self_knowledge(self) -> None:
        """Exposes the fixed description above as queryable SelfModel
        state - not something the agent discovered about itself. Pure
        metadata: touches only self.self_model, never anything act()
        reads."""
        description = self.self_model_description()
        for capability in description.capabilities:
            self.self_model.add_capability(capability)
        for limitation in description.limitations:
            self.self_model.add_limitation(limitation)

    def act(self, observation: Observation) -> Action:
        likelihood_a = gaussian_likelihood(observation.light, self._light_mean_a, self._light_std)
        likelihood_b = gaussian_likelihood(observation.light, self._light_mean_b, self._light_std)
        self.world_model.update(likelihood_a, likelihood_b)

        confidence = max(self.world_model.belief_a, self.world_model.belief_b)
        self.self_model.set_belief(
            BELIEF_ID,
            confidence=confidence,
            evidence=[f"observed_light={observation.light:.4f}"],
        )

        if confidence >= self._confidence_threshold:
            predicted: PredictedState = "A" if self.world_model.belief_a >= 0.5 else "B"
        else:
            predicted = "A" if self._rng.random() < self.world_model.belief_a else "B"

        return Action(name="guess_A" if predicted == "A" else "guess_B")

    def evaluate_belief(self, belief_id: str = BELIEF_ID) -> BeliefEvaluation:
        return self.self_model.evaluate_belief(belief_id)
