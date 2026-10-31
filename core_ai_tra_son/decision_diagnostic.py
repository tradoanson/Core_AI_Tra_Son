"""Deterministic SHADOW decision diagnostic, never a calibrated probability."""
from dataclasses import dataclass
from .advanced_reasoning import AdvancedReasoner

@dataclass(frozen=True)
class DecisionDiagnostic:
    status: str
    selected: str | None
    margin: float
    conflict_codes: tuple[str,...]
    confidence_kind: str = "HEURISTIC_UNCALIBRATED"
    action_executed: bool = False

def diagnose_decision(signals, *, verified=False, options=("WAIT","REVIEW_GATHER","REVIEW_RETURN")):
    if type(signals) is not dict:
        raise ValueError("signals must be a dict")
    result=AdvancedReasoner().rank(signals,verified=verified,options=options)
    if result.status == "UNRESOLVED":
        return DecisionDiagnostic("UNRESOLVED",None,0.0,tuple(result.reason_codes))
    if not result.alternatives:
        return DecisionDiagnostic("UNRESOLVED",None,0.0,("NO_ALTERNATIVES",))
    margin=round(result.alternatives[0].score-(result.alternatives[1].score if len(result.alternatives)>1 else 0),3)
    if margin < 0:
        return DecisionDiagnostic("UNRESOLVED",None,0.0,("INVALID_RANKING",))
    conflicts=tuple(sorted({c for x in result.alternatives if x.score<=0 for c in x.reason_codes}))
    return DecisionDiagnostic(result.status,result.selected,margin,conflicts)
