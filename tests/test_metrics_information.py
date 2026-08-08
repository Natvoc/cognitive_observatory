import math

from metrics import reality_model_divergence


def test_model_matches_reality_has_zero_divergence() -> None:
    assert reality_model_divergence({"A": 1.0, "B": 0.0}, "A") == 0.0


def test_model_confidently_wrong_has_max_divergence() -> None:
    assert math.isclose(reality_model_divergence({"A": 1.0, "B": 0.0}, "B"), math.sqrt(2))


def test_uninformed_prior_has_intermediate_divergence() -> None:
    assert math.isclose(reality_model_divergence({"A": 0.5, "B": 0.5}, "A"), math.sqrt(0.5))
