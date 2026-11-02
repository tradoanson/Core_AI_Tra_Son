"""Offline, dependency-free learning foundation; no host reads or model promotion."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

MAX_ROWS = 10000
MAX_ETA = 604800


@dataclass(frozen=True)
class LearningExample:
    sample_id: str
    group_id: str
    split: str
    predicted_seconds: float
    actual_seconds: float
    independently_verified: bool


def validate_dataset(rows):
    """Fail closed on invalid labels, duplicate IDs and group leakage."""
    if type(rows) not in (list, tuple) or not 1 <= len(rows) <= MAX_ROWS:
        raise ValueError("invalid dataset size")
    ids = set()
    groups = {}
    for row in rows:
        if type(row) is not LearningExample:
            raise ValueError("invalid example type")
        if any(type(v) is not str or not v or len(v) > 96 or not v.isascii()
               for v in (row.sample_id, row.group_id)):
            raise ValueError("invalid identifier")
        if row.split not in ("train", "validation", "test"):
            raise ValueError("invalid split")
        if row.independently_verified is not True:
            raise ValueError("unverified label")
        if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= MAX_ETA
               for v in (row.predicted_seconds, row.actual_seconds)):
            raise ValueError("invalid ETA")
        if row.sample_id in ids:
            raise ValueError("duplicate sample")
        ids.add(row.sample_id)
        previous = groups.setdefault(row.group_id, row.split)
        if previous != row.split:
            raise ValueError("group leakage")
    return True


def dataset_digest(rows):
    validate_dataset(rows)
    records = [dict(sample_id=r.sample_id, group_id=r.group_id, split=r.split,
                    predicted_seconds=r.predicted_seconds, actual_seconds=r.actual_seconds,
                    independently_verified=True) for r in rows]
    canonical = json.dumps(sorted(records, key=lambda x: x["sample_id"]),
                           sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def evaluate_baseline(rows, *, split="test"):
    validate_dataset(rows)
    if split not in ("train", "validation", "test"):
        raise ValueError("invalid split")
    selected = [r for r in rows if r.split == split]
    if not selected:
        raise ValueError("empty evaluation split")
    errors = sorted(abs(r.predicted_seconds - r.actual_seconds) for r in selected)
    count = len(errors)
    return {"split": split, "samples": count,
            "mae_seconds": sum(errors) / count,
            "rmse_seconds": math.sqrt(sum(e * e for e in errors) / count),
            "p95_absolute_error_seconds": errors[math.ceil(0.95 * count) - 1],
            "dataset_sha256": dataset_digest(rows)}
