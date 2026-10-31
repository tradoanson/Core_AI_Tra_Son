"""Synthetic, holdout-only SHADOW evaluation and explicit immutable rollback.

Outcomes are caller-attested labels. No training on evaluation cases, IO or actions.
"""
from dataclasses import dataclass, asdict
from .advanced_reasoning import AdvancedReasoner, ALLOWED_OPTIONS
from .decision_learning import DecisionLearner, DecisionLearningState

MAX_CASES = 512
MIN_EVALUATED = 8


@dataclass(frozen=True)
class DecisionCase:
    case_id: str
    signals: dict
    expected_option: str
    verified: bool = True
    options: tuple[str, ...] = ("WAIT", "REVIEW_GATHER", "REVIEW_RETURN")


@dataclass(frozen=True)
class QualityReport:
    total: int
    evaluated: int
    baseline_correct: int
    adapted_correct: int
    baseline_accuracy: float
    adapted_accuracy: float
    delta: float
    regressions: tuple[str, ...]
    improvements: tuple[str, ...]
    abstained: tuple[str, ...]
    status: str
    action_executed: bool = False

    def to_dict(self):
        result = asdict(self)
        for name in ("regressions", "improvements", "abstained"):
            result[name] = list(getattr(self, name))
        return result


def evaluate_quality(cases, learning_state, *, max_regressions=0, min_delta=0.0):
    """Compare identical verified holdout cases against fixed-policy baseline.

    Fail closed if a case is invalid or evaluation is too small. Labels are
    independent synthetic fixtures; this is not a calibrated performance claim.
    """
    if type(cases) not in (tuple, list) or not MIN_EVALUATED <= len(cases) <= MAX_CASES:
        raise ValueError("holdout must contain 8..512 cases")
    if not DecisionLearner.valid(learning_state):
        raise ValueError("invalid learning state")
    if type(max_regressions) is not int or not 0 <= max_regressions <= MAX_CASES:
        raise ValueError("invalid regression budget")
    if type(min_delta) not in (int, float) or not -1.0 <= min_delta <= 1.0:
        raise ValueError("invalid delta threshold")
    import math
    if not math.isfinite(min_delta):
        raise ValueError("nonfinite threshold")
    seen = set()
    reasoner = AdvancedReasoner()
    baseline_correct = adapted_correct = 0
    regressions, improvements, abstained = [], [], []
    for case in cases:
        if (type(case) is not DecisionCase or type(case.case_id) is not str
                or not 1 <= len(case.case_id) <= 64
                or not all(c.isalnum() or c in "_-" for c in case.case_id)
                or case.case_id in seen or case.verified is not True
                or type(case.signals) is not dict
                or type(case.options) not in (tuple, list)
                or len(case.options) != len(set(case.options))
                or not 1 <= len(case.options) <= 3
                or any(type(o) is not str or o not in ALLOWED_OPTIONS for o in case.options)
                or case.expected_option not in case.options):
            raise ValueError("invalid or duplicate verified holdout case")
        seen.add(case.case_id)
        before = reasoner.rank(case.signals, verified=True, options=case.options)
        after = reasoner.rank(case.signals, verified=True, options=case.options, learning_state=learning_state)
        if before.action_executed or after.action_executed:
            raise ValueError("host action forbidden")
        if before.status == "UNRESOLVED" or after.status == "UNRESOLVED":
            abstained.append(case.case_id)
            continue
        b = before.selected == case.expected_option
        a = after.selected == case.expected_option
        baseline_correct += b
        adapted_correct += a
        if b and not a:
            regressions.append(case.case_id)
        if a and not b:
            improvements.append(case.case_id)
    evaluated = len(cases) - len(abstained)
    if evaluated < MIN_EVALUATED:
        return QualityReport(len(cases), evaluated, baseline_correct, adapted_correct,
                             0.0, 0.0, 0.0, tuple(regressions), tuple(improvements),
                             tuple(abstained), "INSUFFICIENT_EVIDENCE")
    baseline_accuracy = baseline_correct / evaluated
    adapted_accuracy = adapted_correct / evaluated
    delta = adapted_accuracy - baseline_accuracy
    status = ("PASS" if len(regressions) <= max_regressions and delta >= min_delta
              else "DEGRADED")
    return QualityReport(len(cases), evaluated, baseline_correct, adapted_correct,
                         round(baseline_accuracy, 6), round(adapted_accuracy, 6),
                         round(delta, 6), tuple(regressions), tuple(improvements),
                         tuple(abstained), status)


def rollback_on_degradation(current, previous, report):
    """Return previous caller-owned state on quality degradation; never mutate IO."""
    if not DecisionLearner.valid(current) or not DecisionLearner.valid(previous):
        raise ValueError("invalid learning state")
    if type(report) is not QualityReport or report.action_executed:
        raise ValueError("invalid quality report")
    if report.status == "DEGRADED":
        return previous
    if report.status == "PASS":
        return current
    raise ValueError("insufficient evidence: manual review required")
