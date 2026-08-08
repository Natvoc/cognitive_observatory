"""Agent 2 - Predictive (spec §5): observation -> world model -> prediction -> action.

Belief is updated with a simple Bayesian rule over the observed light
level: hidden_state=A pulls light toward `light_mean_a`, hidden_state=B
pulls it toward `light_mean_b`. This is deliberately crude - it does not
try to learn the environment's drift/noise parameters, only to show that
integrating evidence over time beats reacting to a single observation.
"""

import math

from core.actions.action import Action
from core.cognition.prediction import PredictedState, Prediction
from core.cognition.world_model import WorldModel
from core.observer.agent import Observer
from core.observer.observation import Observation


def _gaussian_likelihood(x: float, mean: float, std: float) -> float:
    variance = std**2
    return math.exp(-((x - mean) ** 2) / (2 * variance)) / math.sqrt(2 * math.pi * variance)


class PredictiveAgent(Observer):
    def __init__(
        self,
        light_mean_a: float = 0.75,
        light_mean_b: float = 0.25,
        light_std: float = 0.2,
    ) -> None:
        self.world_model = WorldModel()
        self._light_mean_a = light_mean_a
        self._light_mean_b = light_mean_b
        self._light_std = light_std

    def act(self, observation: Observation) -> Action:
        likelihood_a = _gaussian_likelihood(observation.light, self._light_mean_a, self._light_std)
        likelihood_b = _gaussian_likelihood(observation.light, self._light_mean_b, self._light_std)
        self.world_model.update(likelihood_a, likelihood_b)

        prediction = self.predict(horizon=1)
        return Action(name="guess_A" if prediction.predicted_hidden_state == "A" else "guess_B")

    def predict(self, horizon: int = 1) -> Prediction:
        if horizon != 1:
            raise NotImplementedError("Fase 1 solo soporta horizon=1")
        model = self.world_model
        predicted: PredictedState = "A" if model.belief_a >= model.belief_b else "B"
        confidence = max(self.world_model.belief_a, self.world_model.belief_b)
        return Prediction(horizon=horizon, predicted_hidden_state=predicted, confidence=confidence)
