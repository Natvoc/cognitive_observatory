import pytest

from metrics import calibration


def test_mismatched_lengths_raise() -> None:
    with pytest.raises(ValueError):
        calibration([0.5], [True, False])


def test_perfectly_calibrated_confidence_matches_empirical_accuracy() -> None:
    # Ten predictions all at 0.9 confidence, 9 of them correct: a
    # perfectly-calibrated observer's empirical accuracy in that bucket
    # should equal the confidence it reported.
    confidences = [0.9] * 10
    correct = [True] * 9 + [False]

    buckets = calibration(confidences, correct, num_buckets=10)

    assert len(buckets) == 1
    bucket = buckets[0]
    assert bucket.count == 10
    assert bucket.predicted_confidence_avg == 0.9
    assert bucket.empirical_accuracy == 0.9


def test_overconfident_agent_shows_gap_between_confidence_and_accuracy() -> None:
    # Always reports 1.0 confidence (a hard-guess agent, e.g. Agent 0/1)
    # but is only right half the time - a textbook overconfidence gap.
    confidences = [1.0] * 100
    correct = [i % 2 == 0 for i in range(100)]

    buckets = calibration(confidences, correct, num_buckets=10)

    assert len(buckets) == 1
    assert buckets[0].predicted_confidence_avg == 1.0
    assert buckets[0].empirical_accuracy == 0.5


def test_empty_buckets_are_omitted() -> None:
    buckets = calibration([0.05], [True], num_buckets=10)
    assert len(buckets) == 1
    assert buckets[0].bucket_lo == 0.0
    assert buckets[0].bucket_hi == 0.1
