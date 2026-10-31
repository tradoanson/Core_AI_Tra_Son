"""Deterministic benchmark evaluation; confidence diagnostics, not probability calibration.

Only synthetic, caller-supplied allowlisted signal cases. No file/network writes.
"""
from dataclasses import dataclass, asdict
from .reasoning import ReasoningEngine

STATUSES = frozenset({"WAITING", "REVIEW", "UNRESOLVED"})
MAX_CASES = 512


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    signals: dict
    verified: bool
    expected_status: str


@dataclass(frozen=True)
class BenchmarkReport:
    total: int
    matched: int
    agreement: float
    by_confidence: dict
    mismatches: tuple[str, ...]

    def to_dict(self):
        result = asdict(self)
        result["mismatches"] = list(self.mismatches)
        return result


def validate_benchmark(cases, engine=None):
    """Compare decisions with labelled expected statuses.

    Confidence bins show *agreement* only; confidence is NOT calibrated as
    probability and benchmark labels are not real-world ground truth.
    """
    if type(cases) not in (list, tuple) or not 1 <= len(cases) <= MAX_CASES:
        raise ValueError("benchmark must contain 1..512 cases")
    agent = engine if engine is not None else ReasoningEngine()
    seen = set()
    matches = 0
    buckets = {}
    mismatches = []
    for case in cases:
        if not isinstance(case, BenchmarkCase) or type(case.case_id) is not str or not (
                1 <= len(case.case_id) <= 64) or not all(c.isalnum() or c in "-_" for c in case.case_id):
            raise ValueError("invalid benchmark case ID")
        if case.case_id in seen or case.expected_status not in STATUSES or type(case.verified) is not bool:
            raise ValueError("duplicate ID or invalid expected status/verification")
        seen.add(case.case_id)
        result = agent.evaluate(case.signals, verified=case.verified)
        if result.action_executed:
            raise ValueError("benchmark cannot evaluate action-executing engine")
        ok = result.status == case.expected_status
        matches += int(ok)
        if not ok:
            mismatches.append(case.case_id)
        bucket = f"{result.confidence:.1f}"
        row = buckets.setdefault(bucket, {"total": 0, "matched": 0})
        row["total"] += 1
        row["matched"] += int(ok)
    by_confidence = {
        key: {"total": buckets[key]["total"], "matched": buckets[key]["matched"],
              "agreement": round(buckets[key]["matched"] / buckets[key]["total"], 4)}
        for key in sorted(buckets)
    }
    return BenchmarkReport(len(cases), matches, round(matches / len(cases), 4),
                           by_confidence, tuple(mismatches))
