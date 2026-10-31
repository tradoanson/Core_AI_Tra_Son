"""Opt-in authenticated external checkpoint and bounded incremental replay.

A caller-owned secret key and separate checkpoint are required. This does not
authenticate the caller's verified=True attestation or execute host actions.
"""
import hashlib
import hmac
import json
import os
import sqlite3
import tempfile
from dataclasses import asdict
from pathlib import Path

from .decision_learning import DecisionLearningState
from .learning_store import LearningStore, _ID, _MAX_EVENTS


class SecureLearningStore(LearningStore):
    def __init__(self, db_path, checkpoint_path, key):
        super().__init__(db_path)
        self.checkpoint_path = Path(checkpoint_path)
        if self.checkpoint_path.resolve() == self.path.resolve():
            raise ValueError("checkpoint must be separate from ledger")
        if type(key) is not bytes or len(key) < 32:
            raise ValueError("independent secret key of at least 32 bytes required")
        self._key = key

    def _seal(self, payload):
        return hmac.new(self._key, json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()

    def _load(self):
        if not self.checkpoint_path.is_file():
            raise FileNotFoundError("checkpoint absent; explicitly bootstrap from verified ledger")
        raw = self.checkpoint_path.read_bytes()
        if len(raw) > 2048:
            raise ValueError("checkpoint too large")
        doc = json.loads(raw)
        if type(doc) is not dict or set(doc) != {"payload", "mac"} or type(doc["payload"]) is not dict:
            raise ValueError("invalid checkpoint")
        payload = doc["payload"]
        if not hmac.compare_digest(self._seal(payload), doc["mac"]):
            raise ValueError("checkpoint authentication failed")
        if set(payload) != {"version", "count", "head", "state"} or payload["version"] != 1:
            raise ValueError("invalid checkpoint version")
        if type(payload["count"]) is not int or not 0 <= payload["count"] <= _MAX_EVENTS:
            raise ValueError("invalid checkpoint count")
        if type(payload["head"]) is not str or len(payload["head"]) != 64:
            raise ValueError("invalid checkpoint head")
        state = DecisionLearningState(**payload["state"])
        if not self.learner.valid(state):
            raise ValueError("invalid checkpoint state")
        if state.gather_samples + state.return_samples != payload["count"]:
            raise ValueError("inconsistent checkpoint count")
        return payload, state

    def _publish(self, state, count, head):
        payload = {"version": 1, "count": count, "head": head, "state": asdict(state)}
        data = json.dumps({"payload": payload, "mac": self._seal(payload)}, sort_keys=True).encode()
        if not self.checkpoint_path.parent.is_dir():
            raise FileNotFoundError("checkpoint directory absent")
        fd, name = tempfile.mkstemp(prefix=".learning-checkpoint-", dir=self.checkpoint_path.parent)
        try:
            with os.fdopen(fd, "wb") as output:
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
            os.replace(name, self.checkpoint_path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def bootstrap(self):
        """One-time explicit trust ceremony: fully verify ledger before anchoring.

        Never call bootstrap as an automatic recovery from a missing/bad anchor.
        """
        if self.checkpoint_path.exists():
            raise FileExistsError("refusing to replace existing checkpoint during bootstrap")
        with self._readonly() as db:
            state, count, head = self._replay(db)
        self._publish(state, count, head)
        return state

    def _incremental(self, db):
        self._schema_check(db)
        anchor, state = self._load()
        count, head = anchor["count"], anchor["head"]
        if count:
            row = db.execute("SELECT event_hash FROM learning_events WHERE seq=?", (count,)).fetchone()
            if row is None or row[0] != head:
                raise ValueError("anchored history missing or modified")
        elif head != "0" * 64:
            raise ValueError("invalid genesis checkpoint")
        actual = db.execute("SELECT COUNT(*),COALESCE(MAX(seq),0) FROM learning_events").fetchone()
        if actual[0] != actual[1] or actual[1] < count:
            raise ValueError("history gap or rollback")
        for seq, event_id, option, successful, previous, digest in db.execute(
                "SELECT seq,event_id,option,successful,prev_hash,event_hash FROM learning_events WHERE seq>? ORDER BY seq", (count,)):
            if (seq != count + 1 or type(event_id) is not str or not _ID.fullmatch(event_id)
                    or option not in ("REVIEW_GATHER", "REVIEW_RETURN")
                    or successful not in (0, 1) or previous != head
                    or digest != self._digest(event_id, option, successful, head)):
                raise ValueError("invalid unanchored history")
            state = self.learner.observe(state, option, successful=bool(successful), verified=True)
            count, head = seq, digest
        return state, count, head

    def state(self):
        with self._readonly() as db:
            return self._incremental(db)[0]

    def reconcile(self):
        """Explicit crash recovery: authenticate anchor and replay only valid suffix."""
        with self._readonly() as db:
            state, count, head = self._incremental(db)
        self._publish(state, count, head)
        return state

    def observe(self, event_id, option, *, successful, verified=False):
        if verified is not True:
            return False
        if type(event_id) is not str or not _ID.fullmatch(event_id):
            raise ValueError("invalid opaque event ID")
        if type(successful) is not bool or option not in ("REVIEW_GATHER", "REVIEW_RETURN"):
            raise ValueError("invalid verified outcome")
        with sqlite3.connect(self.path, timeout=30) as db:
            db.execute("BEGIN IMMEDIATE")
            state, count, head = self._incremental(db)
            prior = db.execute("SELECT option,successful FROM learning_events WHERE event_id=?", (event_id,)).fetchone()
            if prior is not None:
                if prior != (option, int(successful)):
                    raise ValueError("conflicting duplicate")
                return False
            if count >= _MAX_EVENTS:
                raise ValueError("event limit")
            updated = self.learner.observe(state, option, successful=successful, verified=True)
            if updated == state:
                return False
            digest = self._digest(event_id, option, successful, head)
            db.execute("INSERT INTO learning_events VALUES(?,?,?,?,?,?)",
                       (count + 1, event_id, option, int(successful), head, digest))
        # A crash here leaves an authenticated older checkpoint. reconcile()
        # validates the suffix before advancing the independent anchor.
        self._publish(updated, count + 1, digest)
        return True
