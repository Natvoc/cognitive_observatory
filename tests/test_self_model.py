from core.cognition import SelfModel


def test_evaluate_belief_returns_confidence_and_evidence() -> None:
    self_model = SelfModel()
    self_model.set_belief("object_is_north", confidence=0.73, evidence=["sensor_12", "memory_384"])

    evaluation = self_model.evaluate_belief("object_is_north")

    assert evaluation.belief_id == "object_is_north"
    assert evaluation.confidence == 0.73
    assert evaluation.evidence == ["sensor_12", "memory_384"]


def test_evaluate_unknown_belief_returns_zero_confidence_and_no_evidence() -> None:
    self_model = SelfModel()

    evaluation = self_model.evaluate_belief("never_set")

    assert evaluation.confidence == 0.0
    assert evaluation.evidence == []
