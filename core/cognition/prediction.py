"""Prediction Engine output - minimal version (spec §4.6).

Fase 1 only supports horizon=1: a guess at the current hidden_state plus
the confidence (belief) behind it.
"""

from dataclasses import dataclass
from typing import Literal

PredictedState = Literal["A", "B"]


@dataclass(frozen=True)
class Prediction:
    horizon: int
    predicted_hidden_state: PredictedState
    confidence: float
