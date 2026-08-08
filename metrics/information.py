"""Reality-Model Divergence (spec §7.1): how far the observer's internal
model is from what actually happened.

Kept deliberately simple for Fase 3 - a plain Euclidean distance between
the belief distribution and the one-hot true state, not an
information-theoretic measure (KL divergence, mutual information, etc.).
That's future work if this simple version turns out not to be enough.
"""

import math


def reality_model_divergence(believed_state: dict[str, float], actual_state: str) -> float:
    return math.sqrt(
        sum(
            (probability - (1.0 if state == actual_state else 0.0)) ** 2
            for state, probability in believed_state.items()
        )
    )
