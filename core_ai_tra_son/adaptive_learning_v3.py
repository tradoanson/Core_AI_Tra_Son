"""Deterministic offline ETA adaptive learner; no host IO or model promotion."""
from __future__ import annotations

from dataclasses import dataclass
import math

from .learning_foundation import LearningExample, evaluate_baseline, validate_dataset

MAX_BIAS_SECONDS = 300.0
MAX_STEP_SECONDS = 30.0
MAX_EPOCHS = 10


@dataclass(frozen=True)
class AdaptiveModelV3:
    bias_seconds: float = 0.0
    samples: int = 0
    epochs: int = 0


def train_adaptive_v3(rows, *, epochs=1, initial=None):
    """Train only on verified training split; never inspect validation/test labels."""
    validate_dataset(rows)
    if type(epochs) is not int or not 1 <= epochs <= MAX_EPOCHS:
        raise ValueError("invalid epochs")
    model = AdaptiveModelV3() if initial is None else initial
    if (type(model) is not AdaptiveModelV3 or type(model.bias_seconds) not in (int, float)
            or not math.isfinite(model.bias_seconds) or abs(model.bias_seconds) > MAX_BIAS_SECONDS
            or type(model.samples) is not int or model.samples < 0
            or type(model.epochs) is not int or model.epochs < 0):
        raise ValueError("invalid initial model")
    train = sorted((r for r in rows if r.split == "train"), key=lambda r: r.sample_id)
    if not train:
        raise ValueError("empty training split")
    bias = float(model.bias_seconds)
    for _ in range(epochs):
        for r in train:
            error = r.actual_seconds - (r.predicted_seconds + bias)
            step = max(-MAX_STEP_SECONDS, min(MAX_STEP_SECONDS, error * 0.1))
            bias = max(-MAX_BIAS_SECONDS, min(MAX_BIAS_SECONDS, bias + step))
    return AdaptiveModelV3(round(bias, 6), model.samples + len(train) * epochs, model.epochs + epochs)


def evaluate_adaptive_v3(rows, model, *, split="test"):
    """Independent comparison; does not update model or dataset."""
    baseline = evaluate_baseline(rows, split=split)
    if type(model) is not AdaptiveModelV3 or not math.isfinite(model.bias_seconds) or abs(model.bias_seconds) > MAX_BIAS_SECONDS:
        raise ValueError("invalid model")
    selected = [r for r in rows if r.split == split]
    errors = sorted(abs(max(0.0, r.predicted_seconds + model.bias_seconds) - r.actual_seconds) for r in selected)
    count = len(errors)
    return {"split": split, "samples": count, "baseline_mae_seconds": baseline["mae_seconds"],
            "adaptive_mae_seconds": sum(errors) / count,
            "adaptive_rmse_seconds": math.sqrt(sum(e * e for e in errors) / count),
            "adaptive_p95_seconds": errors[math.ceil(0.95 * count) - 1],
            "improvement_percent": (100.0 * (baseline["mae_seconds"] - sum(errors) / count) / baseline["mae_seconds"]
                                    if baseline["mae_seconds"] > 0 else 0.0),
            "dataset_sha256": baseline["dataset_sha256"],
            "promoted": False}
