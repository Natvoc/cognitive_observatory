"""Agent 2 - Predictive (spec §5): observation -> attend -> world model -> prediction -> action.

Belief is updated with a simple Bayesian rule over the observed light
level: hidden_state=A pulls light toward `light_mean_a`, hidden_state=B
pulls it toward `light_mean_b`. This is deliberately crude - it does not
try to learn the environment's drift/noise parameters, only to show that
integrating evidence over time beats reacting to a single observation.

Attention (spec §4.3) sits between the raw observation and the belief
update: each likelihood is raised to the attention weight before being
fed to WorldModel.update(). weight=1.0 (UniformAttention, the default)
leaves the likelihood unchanged; weight=0.0 makes it 1.0 for both
hypotheses, i.e. no update at all - a continuous dial on how much of this
observation actually gets processed, not a hard include/exclude switch.
"""

from core.actions.action import Action
from core.cognition.likelihood import gaussian_likelihood
from core.cognition.prediction import PredictedState, Prediction
from core.cognition.world_model import WorldModel
from core.observer.agent import Observer
from core.observer.attention import AttentionSystem, UniformAttention
from core.observer.observation import Observation


class PredictiveAgent(Observer):
    def __init__(
        self,
        light_mean_a: float = 0.75,
        light_mean_b: float = 0.25,
        light_std: float = 0.2,
        attention: AttentionSystem | None = None,
    ) -> None:
        self.world_model = WorldModel()
        self._light_mean_a = light_mean_a
        self._light_mean_b = light_mean_b
        self._light_std = light_std
        self._attention: AttentionSystem = attention or UniformAttention()
        self._previous_observation: Observation | None = None

    def act(self, observation: Observation) -> Action:
        attention_result = self._attention.select(observation, self._previous_observation)
        self._previous_observation = observation

        likelihood_a = gaussian_likelihood(observation.light, self._light_mean_a, self._light_std)
        likelihood_b = gaussian_likelihood(observation.light, self._light_mean_b, self._light_std)
        weight = attention_result.weight
        self.world_model.update(likelihood_a**weight, likelihood_b**weight)

        prediction = self.predict(horizon=1)
        return Action(name="guess_A" if prediction.predicted_hidden_state == "A" else "guess_B")

    def predict(self, horizon: int = 1) -> Prediction:
        if horizon != 1:
            raise NotImplementedError("Fase 1 solo soporta horizon=1")
        model = self.world_model
        predicted: PredictedState = "A" if model.belief_a >= model.belief_b else "B"
        confidence = max(self.world_model.belief_a, self.world_model.belief_b)
        return Prediction(horizon=horizon, predicted_hidden_state=predicted, confidence=confidence)
