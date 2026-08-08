"""Gaussian likelihood - shared by any agent doing a Bayesian belief
update over a continuous observation (light, in the hidden_variable
environment)."""

import math


def gaussian_likelihood(x: float, mean: float, std: float) -> float:
    variance = std**2
    return math.exp(-((x - mean) ** 2) / (2 * variance)) / math.sqrt(2 * math.pi * variance)
