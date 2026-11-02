"""Fail-closed offline learning pipeline; never activates a model."""
from __future__ import annotations
from dataclasses import dataclass
from .learning_foundation import validate_dataset, dataset_digest
from .learning_data_quality_v1 import evaluate_learning_data_quality
from .shadow_benchmark_v1 import run_shadow_benchmark

@dataclass(frozen=True)
class LearningPipelineReport:
    dataset_sha256: str
    quality_accepted: bool
    quality_reason: str
    benchmark_executed: bool
    recommended_candidate: str
    promoted: bool = False

def run_learning_pipeline(rows, *, min_train_samples=10, min_test_samples=20,
                          max_anomaly_fraction=0.10, max_absolute_error_seconds=600.0):
    """Validate -> quality gate -> SHADOW benchmark, stopping on quality failure.

    No mutation, model deployment, persistence or access to real systems.
    """
    validate_dataset(rows)
    quality = evaluate_learning_data_quality(
        rows, min_train_samples=min_train_samples,
        max_anomaly_fraction=max_anomaly_fraction,
        max_absolute_error_seconds=max_absolute_error_seconds)
    if not quality.accepted:
        return LearningPipelineReport(quality.dataset_sha256, False,
                                      quality.reason, False, "baseline")
    benchmark = run_shadow_benchmark(rows, min_test_samples=min_test_samples)
    if benchmark.dataset_sha256 != quality.dataset_sha256:
        raise ValueError("dataset changed during pipeline")
    return LearningPipelineReport(quality.dataset_sha256, True,
                                  quality.reason, True,
                                  benchmark.recommended_candidate)
