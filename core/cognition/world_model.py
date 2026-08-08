"""Internal World Model - minimal version (spec §4.5).

Fase 1 only needs a belief over the hidden_state: P(A) and P(B) = 1 -
P(A), updated with a simple Bayesian rule (posterior ∝ likelihood * prior).
"""

from dataclasses import dataclass


@dataclass
class WorldModel:
    belief_a: float = 0.5

    @property
    def belief_b(self) -> float:
        return 1.0 - self.belief_a

    def update(self, likelihood_a: float, likelihood_b: float) -> None:
        unnormalized_a = likelihood_a * self.belief_a
        unnormalized_b = likelihood_b * self.belief_b
        total = unnormalized_a + unnormalized_b
        if total > 0:
            self.belief_a = unnormalized_a / total
