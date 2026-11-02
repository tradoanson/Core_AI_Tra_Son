"""Pure offline model governance: decisions only, no automatic deployment."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ModelQualityReport:
    model_id: str
    dataset_sha256: str
    samples: int
    baseline_mae_seconds: float
    candidate_mae_seconds: float
    baseline_p95_seconds: float
    candidate_p95_seconds: float


@dataclass(frozen=True)
class GovernanceDecision:
    accepted: bool
    reason: str
    selected_model_id: str


def _valid(report):
    if type(report) is not ModelQualityReport:
        return False
    if (type(report.model_id) is not str or not 1 <= len(report.model_id) <= 96
            or not report.model_id.isascii()):
        return False
    if (type(report.dataset_sha256) is not str or len(report.dataset_sha256) != 64
            or any(c not in "0123456789abcdef" for c in report.dataset_sha256)):
        return False
    if type(report.samples) is not int or not 1 <= report.samples <= 10000:
        return False
    metrics = (report.baseline_mae_seconds, report.candidate_mae_seconds,
               report.baseline_p95_seconds, report.candidate_p95_seconds)
    return all(type(x) in (int, float) and math.isfinite(x) and 0 <= x <= 604800 for x in metrics)


def evaluate_model_governance(report, *, fallback_model_id="baseline",
                              min_improvement_percent=5.0, max_p95_regression_percent=5.0,
                              min_samples=20):
    """Recommend candidate only if prespecified MAE and tail gates pass.

    Return a decision, never activate/deploy a model.
    """
    if (type(fallback_model_id) is not str or not 1 <= len(fallback_model_id) <= 96
            or not fallback_model_id.isascii()):
        raise ValueError("invalid fallback")
    if (type(min_improvement_percent) not in (int, float)
            or not math.isfinite(min_improvement_percent) or not 0 <= min_improvement_percent <= 100
            or type(max_p95_regression_percent) not in (int, float)
            or not math.isfinite(max_p95_regression_percent) or not 0 <= max_p95_regression_percent <= 100
            or type(min_samples) is not int or not 1 <= min_samples <= 10000):
        raise ValueError("invalid governance policy")
    if not _valid(report):
        raise ValueError("invalid quality report")
    if report.samples < min_samples:
        return GovernanceDecision(False, "insufficient_samples", fallback_model_id)
    if report.baseline_mae_seconds <= 0:
        return GovernanceDecision(False, "zero_baseline_error", fallback_model_id)
    improvement = 100 * (report.baseline_mae_seconds - report.candidate_mae_seconds) / report.baseline_mae_seconds
    if improvement < min_improvement_percent:
        return GovernanceDecision(False, "insufficient_improvement", fallback_model_id)
    if report.baseline_p95_seconds <= 0:
        if report.candidate_p95_seconds > 0:
            return GovernanceDecision(False, "tail_regression", fallback_model_id)
    elif report.candidate_p95_seconds > report.baseline_p95_seconds * (1 + max_p95_regression_percent / 100):
        return GovernanceDecision(False, "tail_regression", fallback_model_id)
    return GovernanceDecision(True, "quality_gates_passed", report.model_id)


def choose_rollback(active_model_id, fallback_model_id, *, drift_detected=False):
    """Return a rollback recommendation, never mutate active state."""
    for value in (active_model_id, fallback_model_id):
        if type(value) is not str or not 1 <= len(value) <= 96 or not value.isascii():
            raise ValueError("invalid model id")
    if type(drift_detected) is not bool:
        raise ValueError("invalid drift flag")
    return GovernanceDecision(not drift_detected, "drift_detected" if drift_detected else "stable",
                              fallback_model_id if drift_detected else active_model_id)
