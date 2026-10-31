"""Bounded explainability summary for deterministic SHADOW rankings."""
from dataclasses import dataclass
from .advanced_reasoning import RankingResult

@dataclass(frozen=True)
class DecisionExplanation:
    status: str
    selected: str | None
    confidence_kind: str
    confidence_value: float
    reasons: tuple[str, ...]
    rejected: tuple[str, ...]
    action_executed: bool = False

def explain_ranking(result):
    if type(result) is not RankingResult or result.action_executed:
        raise ValueError("invalid ranking")
    if result.status == "UNRESOLVED":
        return DecisionExplanation("UNRESOLVED",None,"HEURISTIC_UNCALIBRATED",0.0,tuple(result.reason_codes),())
    selected=next((x for x in result.alternatives if x.option == result.selected),None)
    if selected is None or selected.rank != 1 or len(result.alternatives) > 8:
        raise ValueError("inconsistent ranking")
    blocked=tuple(x.option for x in result.alternatives if x.score <= 0)
    return DecisionExplanation(result.status,result.selected,"HEURISTIC_UNCALIBRATED",
                               result.confidence,tuple(selected.reason_codes),blocked)
