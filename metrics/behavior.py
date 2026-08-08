"""Calibration (spec §7): if the observer says 80% confidence, does it
turn out right ~80% of the time? Buckets (confidence, correct) pairs into
fixed-width bins and reports empirical accuracy per bin - a reliability
diagram in table form.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationBucket:
    bucket_lo: float
    bucket_hi: float
    predicted_confidence_avg: float
    empirical_accuracy: float
    count: int


def calibration(
    confidences: list[float], correct: list[bool], num_buckets: int = 10
) -> list[CalibrationBucket]:
    if len(confidences) != len(correct):
        raise ValueError("confidences and correct must have the same length")

    bucket_width = 1.0 / num_buckets
    buckets: list[list[tuple[float, bool]]] = [[] for _ in range(num_buckets)]
    for confidence, is_correct in zip(confidences, correct):
        index = min(int(confidence / bucket_width), num_buckets - 1)
        buckets[index].append((confidence, is_correct))

    result = []
    for index, bucket in enumerate(buckets):
        if not bucket:
            continue
        bucket_confidences = [confidence for confidence, _ in bucket]
        bucket_correctness = [is_correct for _, is_correct in bucket]
        result.append(
            CalibrationBucket(
                bucket_lo=index * bucket_width,
                bucket_hi=(index + 1) * bucket_width,
                predicted_confidence_avg=sum(bucket_confidences) / len(bucket_confidences),
                empirical_accuracy=sum(bucket_correctness) / len(bucket_correctness),
                count=len(bucket),
            )
        )
    return result
