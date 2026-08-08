from metrics import prediction_error


def test_confident_and_correct_has_zero_error() -> None:
    assert prediction_error({"A": 1.0, "B": 0.0}, "A") == 0.0


def test_confident_and_wrong_has_max_error() -> None:
    assert prediction_error({"A": 1.0, "B": 0.0}, "B") == 1.0


def test_uninformed_prior_has_intermediate_error() -> None:
    assert prediction_error({"A": 0.5, "B": 0.5}, "A") == 0.25
