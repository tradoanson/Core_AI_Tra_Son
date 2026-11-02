"""Read-only learning audit across independent synthetic scenarios."""
from __future__ import annotations

from dataclasses import dataclass

from .shadow_benchmark_v1 import run_shadow_benchmark


@dataclass(frozen=True)
class LearningAuditReport:
    scenario_count: int
    improved_scenarios: int
    regressed_scenarios: int
    baseline_selected_scenarios: int
    mean_baseline_mae_seconds: float
    mean_recommended_mae_seconds: float
    accepted: bool
    promoted: bool = False


def audit_learning_scenarios(scenarios, *, min_scenarios=3, min_test_samples=20):
    """Evaluate independent scenarios; reject regressions and baseline-only wins.

    A recommendation is not deployment approval. No model or data is modified.
    """
    if type(min_scenarios) is not int or not 1 <= min_scenarios <= 100:
        raise ValueError("invalid scenario policy")
    if type(scenarios) not in (list, tuple) or not min_scenarios <= len(scenarios) <= 100:
        raise ValueError("insufficient scenarios")
    digests = set()
    baselines = []
    recommended = []
    improved = regressed = baseline_only = 0
    for rows in scenarios:
        report = run_shadow_benchmark(rows, min_test_samples=min_test_samples)
        if report.dataset_sha256 in digests:
            raise ValueError("duplicate scenario dataset")
        digests.add(report.dataset_sha256)
        baseline = report.baseline_mae_seconds
        choices = {"baseline": baseline,
                   "adaptive-v3": report.adaptive_mae_seconds,
                   "tiny-ml-v1": report.tiny_ml_mae_seconds}
        selected = choices[report.recommended_candidate]
        if report.recommended_candidate == "baseline":
            baseline_only += 1
        elif selected < baseline:
            improved += 1
        elif selected > baseline:
            regressed += 1
        baselines.append(baseline)
        recommended.append(selected)
    mean_base = sum(baselines) / len(baselines)
    mean_selected = sum(recommended) / len(recommended)
    return LearningAuditReport(len(scenarios), improved, regressed, baseline_only,
                               mean_base, mean_selected,
                               improved > 0 and regressed == 0 and mean_selected < mean_base)
