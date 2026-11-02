"""Tiny ML V1: dependency-free offline linear residual model, never auto-promoted."""
from __future__ import annotations

from dataclasses import dataclass
import math

from .learning_foundation import evaluate_baseline, validate_dataset

MAX_BIAS = 300.0
MAX_SLOPE = 0.5


@dataclass(frozen=True)
class TinyMLModelV1:
    bias_seconds: float
    slope: float
    trained_samples: int


def train_tiny_ml_v1(rows):
    """Fit bounded least-squares residual on train split only."""
    validate_dataset(rows)
    train = [r for r in rows if r.split == "train"]
    if len(train) < 2:
        raise ValueError("at least two train samples required")
    train.sort(key=lambda r: r.sample_id)
    x = [r.predicted_seconds for r in train]
    y = [r.actual_seconds - r.predicted_seconds for r in train]
    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    variance = sum((v - mx) ** 2 for v in x)
    slope = (sum((a - mx) * (b - my) for a, b in zip(x, y)) / variance
             if variance > 1e-9 else 0.0)
    slope = max(-MAX_SLOPE, min(MAX_SLOPE, slope))
    bias = max(-MAX_BIAS, min(MAX_BIAS, my - slope * mx))
    return TinyMLModelV1(round(bias, 6), round(slope, 9), len(train))


def predict_tiny_ml_v1(model, base_seconds):
    if (type(model) is not TinyMLModelV1
            or type(model.bias_seconds) not in (int, float)
            or type(model.slope) not in (int, float)
            or not math.isfinite(model.bias_seconds) or not math.isfinite(model.slope)
            or abs(model.bias_seconds) > MAX_BIAS or abs(model.slope) > MAX_SLOPE
            or type(model.trained_samples) is not int or model.trained_samples < 2
            or type(base_seconds) not in (int, float)
            or not math.isfinite(base_seconds) or not 0 <= base_seconds <= 604800):
        raise ValueError("invalid model or input")
    return max(0.0, base_seconds * (1.0 + model.slope) + model.bias_seconds)


def evaluate_tiny_ml_v1(rows, model, *, split="test"):
    baseline = evaluate_baseline(rows, split=split)
    selected = [r for r in rows if r.split == split]
    errors = sorted(abs(predict_tiny_ml_v1(model, r.predicted_seconds) - r.actual_seconds)
                    for r in selected)
    n = len(errors)
    mae = sum(errors) / n
    return {"split": split, "samples": n, "baseline_mae_seconds": baseline["mae_seconds"],
            "tiny_ml_mae_seconds": mae,
            "tiny_ml_rmse_seconds": math.sqrt(sum(e * e for e in errors) / n),
            "tiny_ml_p95_seconds": errors[math.ceil(0.95 * n) - 1],
            "improvement_percent": (100 * (baseline["mae_seconds"] - mae) / baseline["mae_seconds"]
                                    if baseline["mae_seconds"] else 0.0),
            "dataset_sha256": baseline["dataset_sha256"], "promoted": False}
