"""Prediction error metric (spec §7): how good an observer's guess is.

Brier score between the observer's belief - a probability distribution
over discrete states - and the one-hot true state, normalized to [0, 1]
(0 = confident and correct, 1 = confident and wrong; the raw sum of
squared errors maxes out at 2 for any number of categories, hence /2).
A hard guess with no real uncertainty (e.g. a reactive agent) is just the
degenerate case where the distribution puts all its mass on one state.
"""


def prediction_error(predicted_state: dict[str, float], actual_state: str) -> float:
    squared_error_sum = sum(
        (probability - (1.0 if state == actual_state else 0.0)) ** 2
        for state, probability in predicted_state.items()
    )
    return squared_error_sum / 2
