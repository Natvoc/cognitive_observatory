"""Self Model - minimal version (spec §4.7): metacognition.

Lets an agent go from "I believe the object is north" to "I believe that
I believe the object is north, with 73% confidence, based on this
evidence" - a belief about a belief, not just the belief itself.
Fase 3 only tracks beliefs + confidence + evidence; capabilities and
limitations are Fase 5.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BeliefEvaluation:
    belief_id: str
    confidence: float
    evidence: list[str]


@dataclass
class SelfModel:
    _confidence: dict[str, float] = field(default_factory=dict)
    _evidence: dict[str, list[str]] = field(default_factory=dict)

    def set_belief(self, belief_id: str, confidence: float, evidence: list[str]) -> None:
        self._confidence[belief_id] = confidence
        self._evidence[belief_id] = evidence

    def evaluate_belief(self, belief_id: str) -> BeliefEvaluation:
        return BeliefEvaluation(
            belief_id=belief_id,
            confidence=self._confidence.get(belief_id, 0.0),
            evidence=self._evidence.get(belief_id, []),
        )
