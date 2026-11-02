"""Pure offline learning data quality gate; no training or host IO."""
from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median

from .learning_foundation import validate_dataset, dataset_digest


@dataclass(frozen=True)
class DataQualityReport:
    dataset_sha256: str
    train_samples: int
    anomaly_count: int
    anomaly_fraction: float
    accepted: bool
    reason: str


def evaluate_learning_data_quality(rows, *, min_train_samples=10,
                                   max_anomaly_fraction=0.10,
                                   max_absolute_error_seconds=600.0):
    """Reject extreme training residuals using median absolute deviation.

    A zero-MAD group is checked against the explicit absolute error limit.
    The report is advisory and never alters the input or trains a model.
    """
    validate_dataset(rows)
    if (type(min_train_samples) is not int or not 2 <= min_train_samples <= 10000
            or type(max_anomaly_fraction) not in (int, float)
            or not math.isfinite(max_anomaly_fraction)
            or not 0 <= max_anomaly_fraction <= 1
            or type(max_absolute_error_seconds) not in (int, float)
            or not math.isfinite(max_absolute_error_seconds)
            or not 0 < max_absolute_error_seconds <= 604800):
        raise ValueError("invalid quality policy")
    train = [r for r in rows if r.split == "train"]
    if len(train) < min_train_samples:
        return DataQualityReport(dataset_digest(rows), len(train), 0, 0.0,
                                 False, "insufficient_training_samples")
    residuals = [r.actual_seconds - r.predicted_seconds for r in train]
    center = median(residuals)
    mad = median([abs(v - center) for v in residuals])
    anomalies = sum(abs(v) > max_absolute_error_seconds or
                    (mad > 1e-9 and abs(v - center) > 6 * 1.4826 * mad)
                    for v in residuals)
    fraction = anomalies / len(train)
    accepted = fraction <= max_anomaly_fraction
    return DataQualityReport(dataset_digest(rows), len(train), anomalies,
                             fraction, accepted,
                             "quality_passed" if accepted else "excessive_anomalies")
