"""Offline verified-outcome drift detector; recommends pause, never acts."""
from dataclasses import dataclass

@dataclass(frozen=True)
class DriftSignal:
    status: str
    baseline_rate: float
    recent_rate: float
    delta: float
    pause_recommended: bool
    action_executed: bool = False

def detect_outcome_drift(baseline, recent, *, minimum_samples=20, tolerance=0.15):
    if type(baseline) not in (tuple,list) or type(recent) not in (tuple,list):
        raise ValueError("verified outcome sequences required")
    if type(minimum_samples) is not int or not 8 <= minimum_samples <= 512:
        raise ValueError("invalid sample minimum")
    if type(tolerance) not in (float,int) or not 0 < tolerance < 1:
        raise ValueError("invalid tolerance")
    for seq in (baseline,recent):
        if len(seq) > 512 or any(type(x) is not bool for x in seq):
            raise ValueError("bounded verified boolean outcomes required")
    if min(len(baseline),len(recent)) < minimum_samples:
        return DriftSignal("INSUFFICIENT_EVIDENCE",0.0,0.0,0.0,True)
    before=sum(baseline)/len(baseline)
    after=sum(recent)/len(recent)
    delta=after-before
    drift=delta < -tolerance
    return DriftSignal("DRIFT" if drift else "STABLE",before,after,delta,drift)
