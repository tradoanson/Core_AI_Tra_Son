"""Strict opt-in read-only VTND observation boundary, synthetic inputs only."""
from dataclasses import dataclass
from .advanced_reasoning import AdvancedReasoner

_FIELDS=frozenset({"march_available","march_capacity","resource_available","eta_seconds","return_buffer_seconds"})

@dataclass(frozen=True)
class AdapterResult:
    status: str
    selected: str | None
    action_executed: bool = False

def shadow_adapter(observation, *, verified=False):
    if type(observation) is not dict or set(observation) - _FIELDS:
        raise ValueError("unknown or sensitive adapter field")
    if verified is not True:
        return AdapterResult("UNRESOLVED",None)
    # Copy values: no mutation of caller data, no reference to host process.
    signals=dict(observation)
    result=AdvancedReasoner().rank(signals,verified=True,options=["WAIT","REVIEW_GATHER","REVIEW_RETURN"])
    return AdapterResult(result.status,result.selected)
