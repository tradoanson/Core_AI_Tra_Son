"""Conservative offline adaptive learning V2 advisory, without autonomous writes."""
from dataclasses import dataclass
from .learning_drift import detect_outcome_drift

@dataclass(frozen=True)
class AdaptiveAdvice:
    status: str
    learning_allowed: bool
    proposed_delta: float
    reason: str
    action_executed: bool = False

def advise_adaptation(baseline, recent, *, current_delta=0.0, maximum_step=0.05):
    if type(current_delta) not in (float,int) or type(maximum_step) not in (float,int):
        raise ValueError("numeric bounded parameters required")
    if not -1 <= current_delta <= 1 or not 0 < maximum_step <= 0.05:
        raise ValueError("out of bounds")
    drift=detect_outcome_drift(baseline,recent)
    if drift.pause_recommended:
        return AdaptiveAdvice("FROZEN",False,0.0,drift.status)
    # No automatic tuning: propose zero until independently validated
    # performance and provenance gates are supplied by a future caller.
    return AdaptiveAdvice("REVIEW_REQUIRED",False,0.0,"human review required before learning")
