"""Bounded adversarial regression matrix for offline SHADOW advisory."""
from dataclasses import dataclass
from .advanced_reasoning import AdvancedReasoner

@dataclass(frozen=True)
class AdversarialReport:
    total: int
    passed: int
    failed_cases: tuple[str,...]
    status: str
    action_executed: bool = False

def run_adversarial_matrix():
    cases=(
        ("unverified",{"march_available":1},False,"UNRESOLVED"),
        ("missing_march",{},True,"UNRESOLVED"),
        ("negative_march",{"march_available":-1},True,"UNRESOLVED"),
        ("string_march",{"march_available":"1"},True,"UNRESOLVED"),
        ("bool_march",{"march_available":True},True,"UNRESOLVED"),
        ("empty_march",{"march_available":0},True,"WAITING"),
        ("resource_false",{"march_available":1,"resource_available":False},True,"WAITING"),
        ("resource_unknown",{"march_available":1},True,"WAITING"),
        ("available",{"march_available":1,"resource_available":True},True,"REVIEW"),
    )
    reasoner=AdvancedReasoner()
    failures=[]
    for name,signals,verified,expected in cases:
        try:
            result=reasoner.rank(signals,verified=verified,options=["WAIT","REVIEW_GATHER","REVIEW_RETURN"])
            if result.status != expected or result.action_executed:
                failures.append(name)
        except (ValueError,TypeError,KeyError):
            failures.append(name)
    return AdversarialReport(len(cases),len(cases)-len(failures),tuple(failures),
                             "PASS" if not failures else "FAIL")
