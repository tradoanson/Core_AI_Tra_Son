"""Fail-closed release-candidate gate over explicit independent evidence."""
from dataclasses import dataclass

REQUIRED=("linux_311","linux_312","linux_313","windows_native","wheel_sha256","windows_exe","synthetic_quality","security_review")

@dataclass(frozen=True)
class CandidateVerdict:
    status: str
    missing: tuple[str,...]
    failed: tuple[str,...]
    checked: int
    action_executed: bool = False

def evaluate_candidate(evidence):
    if type(evidence) is not dict or any(type(k) is not str or type(v) is not bool for k,v in evidence.items()):
        raise ValueError("evidence must map string keys to booleans")
    if set(evidence)-set(REQUIRED):
        raise ValueError("unknown evidence key")
    missing=tuple(k for k in REQUIRED if k not in evidence)
    failed=tuple(k for k in REQUIRED if evidence.get(k) is False)
    return CandidateVerdict("READY_FOR_REVIEW" if not missing and not failed else "BLOCKED",
                            missing,failed,len(evidence))
