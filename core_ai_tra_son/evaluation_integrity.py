"""Fail-closed evaluation provenance and non-destructive persisted rollback.

Rollback is an authenticated, ledger-bound *selection override*, never deletion
or rewriting of verified learning history. All paths explicit, SHADOW only.
"""
import hashlib
import hmac
import json
import os
import re
import sqlite3
import tempfile
from dataclasses import asdict
from pathlib import Path

from .decision_learning import DecisionLearner, DecisionLearningState
from .decision_quality import DecisionCase, QualityReport, evaluate_quality
from .hardened_learning import HardenedLearningStore
from .secure_learning import SecureLearningStore

_CASE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


class EvaluationIntegrityStore(HardenedLearningStore):
    def __init__(self, db_path, checkpoint_path, key, evaluation_path, override_path):
        super().__init__(db_path, checkpoint_path, key)
        self.evaluation_path = Path(evaluation_path)
        self.override_path = Path(override_path)
        paths = [self.path.resolve(), self.checkpoint_path.resolve(),
                 self.lock_path.resolve(), self.evaluation_path.resolve(),
                 self.override_path.resolve()]
        if len(set(paths)) != len(paths):
            raise ValueError("all storage paths must be distinct")

    def _mac(self, payload):
        return hmac.new(self._key, _canonical(payload), hashlib.sha256).hexdigest()

    def _read_signed(self, path):
        if not path.is_file():
            raise FileNotFoundError("signed artifact missing")
        raw = path.read_bytes()
        if len(raw) > 16384:
            raise ValueError("signed artifact too large")
        doc = json.loads(raw)
        if type(doc) is not dict or set(doc) != {"payload", "mac"} or type(doc["mac"]) is not str:
            raise ValueError("invalid signed artifact")
        if not hmac.compare_digest(self._mac(doc["payload"]), doc["mac"]):
            raise ValueError("signed artifact authentication failed")
        return doc["payload"]

    def _write_signed_new(self, path, payload):
        """Create-only publication; never replace an existing report/override."""
        if path.exists():
            raise FileExistsError("signed artifact already exists")
        if not path.parent.is_dir():
            raise FileNotFoundError("artifact parent missing")
        data = _canonical({"payload": payload, "mac": self._mac(payload)})
        fd, tmp = tempfile.mkstemp(prefix=".evaluation-stage-", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(data)
                out.flush()
                os.fsync(out.fileno())
            os.link(tmp, path)  # atomic create-if-absent
            dfd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        finally:
            Path(tmp).unlink(missing_ok=True)

    def _ledger_identity(self, db):
        state, count, head = self._incremental(db)
        return state, count, head

    def evaluate_holdout(self, cases, *, max_regressions=0, min_delta=0.0):
        """Reject reused training IDs; sign only bounded summary, not raw signals."""
        with self._guard():
            with self._readonly() as db:
                state, count, head = self._ledger_identity(db)
                if type(cases) not in (tuple, list) or not 8 <= len(cases) <= 512:
                    raise ValueError("invalid holdout size")
                for case in cases:
                    if type(case) is not DecisionCase or not _CASE_ID.fullmatch(case.case_id):
                        raise ValueError("invalid holdout ID")
                ids = [case.case_id for case in cases]
                if len(set(ids)) != len(ids):
                    raise ValueError("duplicate holdout ID")
                # Exact identifier overlap check; caller must ensure identifiers
                # consistently represent real outcomes across train and holdout.
                for cid in ids:
                    if db.execute("SELECT 1 FROM learning_events WHERE event_id=?", (cid,)).fetchone():
                        raise ValueError("training/holdout identifier overlap")
                if self.override_path.exists():
                    raise ValueError("rollback override active: evaluation suspended")
                report = evaluate_quality(cases, state, max_regressions=max_regressions,
                                          min_delta=min_delta)
                digest = hashlib.sha256(_canonical([{
                    "case_id": c.case_id, "signals": c.signals,
                    "expected_option": c.expected_option, "verified": c.verified,
                    "options": c.options} for c in cases])).hexdigest()
                payload = {"version": 1, "ledger_count": count, "ledger_head": head,
                           "holdout_sha256": digest, "report": report.to_dict(),
                           "state": asdict(state)}
                self._write_signed_new(self.evaluation_path, payload)
                return report

    def verify_evaluation(self):
        with self._guard():
            payload = self._read_signed(self.evaluation_path)
            if type(payload) is not dict or set(payload) != {
                    "version", "ledger_count", "ledger_head", "holdout_sha256",
                    "report", "state"} or payload["version"] != 1:
                raise ValueError("unsupported evaluation format")
            with self._readonly() as db:
                state, count, head = self._ledger_identity(db)
            if payload["ledger_count"] != count or payload["ledger_head"] != head:
                raise ValueError("evaluation stale relative to ledger")
            if payload["state"] != asdict(state):
                raise ValueError("evaluation learning state mismatch")
            r = payload["report"]
            if type(r) is not dict or r.get("status") not in ("PASS", "DEGRADED", "INSUFFICIENT_EVIDENCE") or r.get("action_executed") is not False:
                raise ValueError("invalid evaluation result")
            return payload

    def activate_rollback(self, previous_state):
        """Persist a reversible override, only after signed DEGRADED evidence."""
        if not DecisionLearner.valid(previous_state):
            raise ValueError("invalid rollback target")
        with self._guard():
            payload = self._read_signed(self.evaluation_path)
            with self._readonly() as db:
                current, count, head = self._ledger_identity(db)
            if (payload.get("ledger_count") != count or payload.get("ledger_head") != head
                    or payload.get("state") != asdict(current)
                    or payload.get("report", {}).get("status") != "DEGRADED"):
                raise ValueError("authenticated degraded report required for current ledger")
            if previous_state.gather_samples > current.gather_samples or previous_state.return_samples > current.return_samples:
                raise ValueError("rollback target cannot be newer")
            override = {"version": 1, "ledger_count": count, "ledger_head": head,
                        "state": asdict(previous_state),
                        "evaluation_mac": self._mac(payload)}
            self._write_signed_new(self.override_path, override)
            return previous_state

    def effective_state(self):
        """Fail closed on stale/tampered override; do not silently use live state."""
        with self._guard():
            with self._readonly() as db:
                current, count, head = self._ledger_identity(db)
            if not self.override_path.exists():
                return current
            payload = self._read_signed(self.override_path)
            if (type(payload) is not dict or set(payload) != {
                    "version", "ledger_count", "ledger_head", "state", "evaluation_mac"}
                    or payload["version"] != 1 or payload["ledger_count"] != count
                    or payload["ledger_head"] != head):
                raise ValueError("stale rollback override")
            evaluation = self._read_signed(self.evaluation_path)
            if (payload["evaluation_mac"] != self._mac(evaluation)
                    or evaluation.get("report", {}).get("status") != "DEGRADED"):
                raise ValueError("rollback evaluation mismatch")
            state = DecisionLearningState(**payload["state"])
            if not DecisionLearner.valid(state):
                raise ValueError("invalid rollback state")
            return state

    def observe(self, event_id, option, *, successful, verified=False):
        with self._guard():
            if self.override_path.exists():
                raise ValueError("learning frozen while rollback override active")
            if verified is not True:
                return False
            with self._readonly() as db:
                state, count, head = self._ledger_identity(db)
                anchor, _ = self._load()
            if count != anchor['count']:
                self._publish(state, count, head)
            # Bypass HardenedLearningStore.observe to avoid acquiring flock twice.
            return SecureLearningStore.observe(self, event_id, option,
                                               successful=successful, verified=True)
