"""Verified-outcome, bounded, immutable SHADOW preference learning.

This module does not persist data, read host applications or execute actions.
The caller owns the state and must explicitly attest outcome verification.
"""
from dataclasses import dataclass, asdict
import math

LEARNABLE = frozenset({"REVIEW_GATHER", "REVIEW_RETURN"})
MAX_SAMPLES = 1000000
MAX_ADJUSTMENT = 0.08
STEP = 0.02


@dataclass(frozen=True)
class DecisionLearningState:
    namespace: str = "vtnd"
    gather_adjustment: float = 0.0
    return_adjustment: float = 0.0
    gather_samples: int = 0
    return_samples: int = 0

    def to_dict(self):
        return asdict(self)


class DecisionLearner:
    """Apply only independently verified, explicitly supplied outcome labels."""
    @staticmethod
    def valid(state):
        return (type(state) is DecisionLearningState and state.namespace == "vtnd"
                and all(type(n) is int and 0 <= n <= MAX_SAMPLES
                        for n in (state.gather_samples, state.return_samples))
                and all(type(v) in (float, int) and math.isfinite(v)
                        and abs(v) <= MAX_ADJUSTMENT
                        for v in (state.gather_adjustment, state.return_adjustment)))

    def observe(self, state, option, *, successful, verified=False):
        if not self.valid(state):
            raise ValueError("invalid learning state")
        if verified is not True:
            return state
        if type(option) is not str or option not in LEARNABLE:
            raise ValueError("only approved review options can learn")
        if type(successful) is not bool:
            raise ValueError("outcome must be a verified boolean")
        attr = "gather" if option == "REVIEW_GATHER" else "return"
        count_name = attr + "_samples"
        bias_name = attr + "_adjustment"
        count = getattr(state, count_name)
        if count >= MAX_SAMPLES:
            return state
        delta = STEP if successful else -STEP
        value = round(max(-MAX_ADJUSTMENT, min(MAX_ADJUSTMENT,
                          getattr(state, bias_name) + delta)), 6)
        from dataclasses import replace
        return replace(state, **{count_name: count + 1, bias_name: value})

    @classmethod
    def adjustment(cls, state, option):
        if state is None:
            return 0.0
        if not cls.valid(state):
            raise ValueError("invalid learning state")
        if option == "REVIEW_GATHER":
            return float(state.gather_adjustment)
        if option == "REVIEW_RETURN":
            return float(state.return_adjustment)
        return 0.0
