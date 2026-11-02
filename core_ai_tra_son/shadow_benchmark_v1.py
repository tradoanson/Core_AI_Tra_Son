"""Read-only offline SHADOW benchmark; models never auto-promoted."""
from __future__ import annotations

from dataclasses import dataclass
import math

from .learning_foundation import validate_dataset, evaluate_baseline, dataset_digest
from .adaptive_learning_v3 import train_adaptive_v3, evaluate_adaptive_v3
from .tiny_ml_v1 import train_tiny_ml_v1, evaluate_tiny_ml_v1
from .model_governance_v1 import ModelQualityReport, evaluate_model_governance


@dataclass(frozen=True)
class ShadowBenchmarkReport:
    dataset_sha256: str
    train_samples: int
    test_samples: int
    baseline_mae_seconds: float
    adaptive_mae_seconds: float
    tiny_ml_mae_seconds: float
    adaptive_gate_passed: bool
    tiny_ml_gate_passed: bool
    recommended_candidate: str
    promoted: bool = False


def run_shadow_benchmark(rows, *, min_test_samples=20):
    """Train on train split, score untouched test split, return recommendation only."""
    validate_dataset(rows)
    if type(min_test_samples) is not int or not 1 <= min_test_samples <= 10000:
        raise ValueError("invalid sample policy")
    train = sum(r.split == "train" for r in rows)
    test = sum(r.split == "test" for r in rows)
    if train < 2 or test < min_test_samples:
        raise ValueError("insufficient train/test samples")
    baseline = evaluate_baseline(rows)
    adaptive = evaluate_adaptive_v3(rows, train_adaptive_v3(rows, epochs=3))
    tiny = evaluate_tiny_ml_v1(rows, train_tiny_ml_v1(rows))
    digest = dataset_digest(rows)
    def gate(name, mae, p95):
        return evaluate_model_governance(
            ModelQualityReport(name, digest, test, baseline["mae_seconds"], mae,
                               baseline["p95_absolute_error_seconds"], p95),
            min_samples=min_test_samples).accepted
    ag = gate("adaptive-v3", adaptive["adaptive_mae_seconds"], adaptive["adaptive_p95_seconds"])
    tg = gate("tiny-ml-v1", tiny["tiny_ml_mae_seconds"], tiny["tiny_ml_p95_seconds"])
    candidates = []
    if ag:
        candidates.append(("adaptive-v3", adaptive["adaptive_mae_seconds"]))
    if tg:
        candidates.append(("tiny-ml-v1", tiny["tiny_ml_mae_seconds"]))
    recommended = min(candidates, key=lambda x: (x[1], x[0]))[0] if candidates else "baseline"
    return ShadowBenchmarkReport(digest, train, test, baseline["mae_seconds"],
                                 adaptive["adaptive_mae_seconds"], tiny["tiny_ml_mae_seconds"],
                                 ag, tg, recommended)
