"""Offline holdout leakage audit: conservative exact normalized signal matching.

Only synthetic/caller-approved cases; no raw signals written or network calls.
"""
import hashlib
import json
from dataclasses import dataclass
from .decision_quality import DecisionCase


@dataclass(frozen=True)
class LeakageReport:
    status: str
    training_count: int
    holdout_count: int
    duplicate_training: int
    duplicate_holdout: int
    cross_split_duplicates: int
    action_executed: bool = False


def _signature(case):
    if type(case) is not DecisionCase:
        raise ValueError("expected DecisionCase")
    if case.verified is not True:
        raise ValueError("unverified case")
    # Canonical JSON preserves typed numeric values; this is exact structural
    # duplication, not approximate or semantic similarity detection.
    raw=json.dumps({"signals":case.signals,"options":case.options},
                   sort_keys=True,separators=(",",":"),allow_nan=False)
    if len(raw) > 16384:
        raise ValueError("case too large")
    return hashlib.sha256(raw.encode()).hexdigest()


def audit_holdout_leakage(training, holdout):
    if type(training) not in (list,tuple) or type(holdout) not in (list,tuple):
        raise ValueError("case sequences required")
    if not 8 <= len(training) <= 512 or not 8 <= len(holdout) <= 512:
        raise ValueError("bounded splits required")
    for cases in (training,holdout):
        ids=[c.case_id for c in cases if type(c) is DecisionCase]
        if len(ids) != len(cases) or len(set(ids)) != len(ids):
            raise ValueError("invalid or duplicate case IDs")
    if set(c.case_id for c in training) & set(c.case_id for c in holdout):
        raise ValueError("case ID overlaps across splits")
    left=[_signature(c) for c in training]
    right=[_signature(c) for c in holdout]
    dt=len(left)-len(set(left))
    dh=len(right)-len(set(right))
    cross=sum(1 for x in right if x in set(left))
    status="PASS" if not (dt or dh or cross) else "BLOCKED"
    return LeakageReport(status,len(left),len(right),dt,dh,cross)
