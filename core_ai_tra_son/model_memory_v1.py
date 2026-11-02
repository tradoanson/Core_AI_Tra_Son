"""Pure, immutable offline model memory; no file or host access."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math


@dataclass(frozen=True)
class ModelMemoryEvent:
    event_id: str
    model_version: str
    dataset_sha256: str
    metric_name: str
    metric_value: float


@dataclass(frozen=True)
class ModelMemoryRecord:
    event: ModelMemoryEvent
    previous_hash: str
    record_hash: str


@dataclass(frozen=True)
class ModelMemoryV1:
    records: tuple[ModelMemoryRecord, ...] = ()


def _valid_event(e):
    if type(e) is not ModelMemoryEvent:
        return False
    if any(type(s) is not str or not 1 <= len(s) <= 96 or not s.isascii()
           for s in (e.event_id, e.model_version, e.metric_name)):
        return False
    if (type(e.dataset_sha256) is not str or len(e.dataset_sha256) != 64
            or any(c not in "0123456789abcdef" for c in e.dataset_sha256)):
        return False
    return (type(e.metric_value) in (int, float) and math.isfinite(e.metric_value)
            and 0 <= e.metric_value <= 604800)


def _hash_event(e, previous):
    payload = {"event_id": e.event_id, "model_version": e.model_version,
               "dataset_sha256": e.dataset_sha256, "metric_name": e.metric_name,
               "metric_value": e.metric_value, "previous_hash": previous}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def verify_model_memory(memory):
    if type(memory) is not ModelMemoryV1 or len(memory.records) > 10000:
        raise ValueError("invalid memory")
    previous = "0" * 64
    ids = set()
    for record in memory.records:
        if type(record) is not ModelMemoryRecord or not _valid_event(record.event):
            raise ValueError("invalid record")
        if record.event.event_id in ids or record.previous_hash != previous:
            raise ValueError("duplicate or broken chain")
        if record.record_hash != _hash_event(record.event, previous):
            raise ValueError("hash mismatch")
        ids.add(record.event.event_id)
        previous = record.record_hash
    return True


def remember_model_event(memory, event):
    """Append a verified-structure event; identical replay is idempotent."""
    verify_model_memory(memory)
    if not _valid_event(event):
        raise ValueError("invalid event")
    for record in memory.records:
        if record.event.event_id == event.event_id:
            if record.event == event:
                return memory
            raise ValueError("conflicting event id")
    if len(memory.records) >= 10000:
        raise ValueError("memory full")
    previous = memory.records[-1].record_hash if memory.records else "0" * 64
    record = ModelMemoryRecord(event, previous, _hash_event(event, previous))
    return ModelMemoryV1(memory.records + (record,))
