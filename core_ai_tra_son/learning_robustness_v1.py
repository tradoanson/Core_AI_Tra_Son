"""Offline robustness gate across independent SHADOW scenarios; no promotion."""
from __future__ import annotations
from dataclasses import dataclass
import math
from .shadow_benchmark_v1 import run_shadow_benchmark

@dataclass(frozen=True)
class RobustnessReport:
    scenarios: int
    selected_model: str
    worst_regression_percent: float
    mean_improvement_percent: float
    accepted: bool
    promoted: bool = False

def evaluate_learning_robustness(scenarios, *, min_scenarios=3,
                                 min_test_samples=20, max_regression_percent=0.0,
                                 min_mean_improvement_percent=5.0):
    if (type(min_scenarios) is not int or not 2 <= min_scenarios <= 100
            or type(min_test_samples) is not int or not 1 <= min_test_samples <= 10000
            or type(max_regression_percent) not in (int, float)
            or not math.isfinite(max_regression_percent) or not 0 <= max_regression_percent <= 100
            or type(min_mean_improvement_percent) not in (int, float)
            or not math.isfinite(min_mean_improvement_percent)
            or not 0 <= min_mean_improvement_percent <= 100):
        raise ValueError("invalid robustness policy")
    if type(scenarios) not in (tuple, list) or not min_scenarios <= len(scenarios) <= 100:
        raise ValueError("insufficient scenarios")
    reports = [run_shadow_benchmark(rows, min_test_samples=min_test_samples)
               for rows in scenarios]
    if len({r.dataset_sha256 for r in reports}) != len(reports):
        raise ValueError("duplicate scenario")
    # One candidate must generalize across ALL scenarios; no per-scenario cherry-picking.
    candidates = {"adaptive-v3": "adaptive_mae_seconds", "tiny-ml-v1": "tiny_ml_mae_seconds"}
    outcomes = []
    for name, attr in candidates.items():
        improvements = []
        regressions = []
        for r in reports:
            baseline = r.baseline_mae_seconds
            candidate = getattr(r, attr)
            if baseline == 0:
                improvements.append(0.0 if candidate == 0 else -100.0)
                regressions.append(0.0 if candidate == 0 else 100.0)
            else:
                improvements.append(100.0 * (baseline - candidate) / baseline)
                regressions.append(100.0 * max(0.0, candidate - baseline) / baseline)
        mean = sum(improvements) / len(improvements)
        worst = max(regressions)
        if worst <= max_regression_percent and mean >= min_mean_improvement_percent:
            outcomes.append((name, mean, worst))
    if not outcomes:
        return RobustnessReport(len(reports), "baseline", 0.0, 0.0, False)
    name, mean, worst = sorted(outcomes, key=lambda x: (-x[1], x[0]))[0]
    return RobustnessReport(len(reports), name, worst, mean, True)
