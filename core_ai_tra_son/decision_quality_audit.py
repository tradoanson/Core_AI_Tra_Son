"""Offline decision-quality audit against explicit synthetic expected outcomes.

This is not real-world accuracy or calibrated confidence.
"""
from dataclasses import dataclass
from .advanced_reasoning import AdvancedReasoner

@dataclass(frozen=True)
class QualityAudit:
    total: int
    matched: int
    mismatch_ids: tuple[str,...]
    agreement_rate: float
    status: str
    dataset_kind: str = "SYNTHETIC"
    action_executed: bool = False

def audit_synthetic_decisions():
    fixtures=(
        ("no_march",{"march_available":0},"WAIT"),
        ("no_resource",{"march_available":1,"resource_available":False},"WAIT"),
        ("unknown_resource",{"march_available":1},"WAIT"),
        ("gather_ready",{"march_available":1,"resource_available":True},"REVIEW_GATHER"),
        ("gather_ready_two",{"march_available":2,"resource_available":True},"REVIEW_GATHER"),
    )
    engine=AdvancedReasoner()
    failures=[]
    for case_id,signals,expected in fixtures:
        try:
            result=engine.rank(signals,verified=True,options=["WAIT","REVIEW_GATHER","REVIEW_RETURN"])
            if result.selected != expected or result.action_executed:
                failures.append(case_id)
        except (TypeError,ValueError,KeyError):
            failures.append(case_id)
    matched=len(fixtures)-len(failures)
    return QualityAudit(len(fixtures),matched,tuple(failures),round(matched/len(fixtures),3),
                        "PASS" if not failures else "FAIL")
