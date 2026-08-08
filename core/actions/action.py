"""Action: what an Observer emits at the end of a step (spec §4.8).

For the hidden_variable experiment an action is a guess about which
hidden_state produced the observed effects - the thing being measured
is how good that guess gets as the cognitive architecture improves.
"""

from dataclasses import dataclass
from typing import Literal

ActionName = Literal["guess_A", "guess_B"]


@dataclass(frozen=True)
class Action:
    name: ActionName
