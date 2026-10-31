"""Opt-in trusted holdout provenance and ledger-replayed rollback approval.

Independent issuer key signs holdout identity, and a distinct approver key
authorizes a bounded historical rollback. No deletion or host actions.
"""
import hashlib
import hmac
import json
import re
from dataclasses import asdict

from .decision_learning import DecisionLearningState
from .decision_quality import DecisionCase
from .evaluation_integrity import EvaluationIntegrityStore, _canonical

_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _sign(key, payload):
    if type(key) is not bytes or len(key) < 32:
        raise ValueError("independent key must be at least 32 bytes")
    return hmac.new(key, _canonical(payload), hashlib.sha256).hexdigest()


def holdout_digest(cases):
    if type(cases) not in (list, tuple) or not 8 <= len(cases) <= 512:
        raise ValueError("invalid holdout")
    if any(type(c) is not DecisionCase for c in cases):
        raise ValueError("invalid holdout case")
    return hashlib.sha256(_canonical([{
        "case_id": c.case_id, "signals": c.signals,
        "expected_option": c.expected_option, "verified": c.verified,
        "options": c.options} for c in cases])).hexdigest()


def issue_provenance(cases, *, issuer_id, issuer_key):
    """External issuer must independently verify source and train/holdout split.

    Signing is not itself evidence that the issuer performed that verification.
    """
    if type(issuer_id) is not str or not _ID.fullmatch(issuer_id):
        raise ValueError("invalid issuer")
    payload = {"version": 1, "issuer": issuer_id, "holdout_sha256": holdout_digest(cases),
               "case_ids": [c.case_id for c in cases]}
    return {"payload": payload, "signature": _sign(issuer_key, payload)}


def approve_rollback(request, *, approver_id, approver_key):
    """External approval ceremony; never embed approver key in repository."""
    if type(approver_id) is not str or not _ID.fullmatch(approver_id):
        raise ValueError("invalid approver")
    if type(request) is not dict or set(request) != {"version", "count", "head", "evaluation_mac"}:
        raise ValueError("invalid rollback request")
    payload = {"version": 1, "approver": approver_id, "request": request}
    return {"payload": payload, "signature": _sign(approver_key, payload)}


class TrustedEvaluationStore(EvaluationIntegrityStore):
    def __init__(self, db_path, checkpoint_path, key, evaluation_path, override_path,
                 *, issuer_key, approver_key):
        super().__init__(db_path, checkpoint_path, key, evaluation_path, override_path)
        if issuer_key == self._key or approver_key == self._key or issuer_key == approver_key:
            raise ValueError("issuer, approver and ledger keys must be independent")
        _sign(issuer_key, {})
        _sign(approver_key, {})
        self._issuer_key = issuer_key
        self._approver_key = approver_key

    def evaluate_trusted(self, cases, provenance, *, max_regressions=0, min_delta=0.0):
        if type(provenance) is not dict or set(provenance) != {"payload", "signature"}:
            raise ValueError("missing provenance")
        payload = provenance["payload"]
        if (type(payload) is not dict or set(payload) != {
                "version", "issuer", "holdout_sha256", "case_ids"}
                or payload["version"] != 1
                or type(payload["issuer"]) is not str or not _ID.fullmatch(payload["issuer"])
                or payload["case_ids"] != [c.case_id for c in cases]
                or payload["holdout_sha256"] != holdout_digest(cases)
                or type(provenance["signature"]) is not str
                or not hmac.compare_digest(provenance["signature"], _sign(self._issuer_key, payload))):
            raise ValueError("untrusted or altered provenance")
        return EvaluationIntegrityStore.evaluate_holdout(self, cases, max_regressions=max_regressions,
                                        min_delta=min_delta)

    def evaluate_holdout(self, cases, *, max_regressions=0, min_delta=0.0):
        raise ValueError('trusted provenance required')

    def _historical_state(self, db, count):
        """Replay and validate the entire hash chain, returning exact prefix state."""
        if type(count) is not int or count < 0:
            raise ValueError("invalid historical position")
        self._schema_check(db)
        state = DecisionLearningState()
        previous = "0" * 64
        expected = 1
        for seq, event_id, option, successful, prev, digest in db.execute(
                "SELECT seq,event_id,option,successful,prev_hash,event_hash FROM learning_events ORDER BY seq"):
            if (seq != expected or seq > 1000000 or prev != previous
                    or digest != self._digest(event_id, option, successful, prev)
                    or option not in ("REVIEW_GATHER", "REVIEW_RETURN")
                    or successful not in (0, 1)):
                raise ValueError("corrupted historical chain")
            if seq <= count:
                state = self.learner.observe(state, option, successful=bool(successful), verified=True)
            previous = digest
            expected += 1
        if count >= expected:
            raise ValueError("historical target beyond ledger")
        return state

    def rollback_request(self, target_count):
        with self._guard():
            evaluation = self._read_signed(self.evaluation_path)
            with self._readonly() as db:
                current, count, head = self._ledger_identity(db)
                if type(target_count) is not int or not 0 <= target_count < count:
                    raise ValueError("target must precede current ledger")
                if (evaluation.get("ledger_count") != count
                        or evaluation.get("ledger_head") != head
                        or evaluation.get("state") != asdict(current)
                        or evaluation.get("report", {}).get("status") != "DEGRADED"):
                    raise ValueError("current authenticated degradation required")
                self._historical_state(db, target_count)
            return {"version": 1, "count": target_count, "head": head,
                    "evaluation_mac": self._mac(evaluation)}

    def activate_trusted_rollback(self, request, approval):
        if type(approval) is not dict or set(approval) != {"payload", "signature"}:
            raise ValueError("missing approval")
        payload = approval["payload"]
        if (type(payload) is not dict or set(payload) != {"version", "approver", "request"}
                or payload["version"] != 1
                or type(payload["approver"]) is not str or not _ID.fullmatch(payload["approver"])
                or payload["request"] != request
                or type(approval["signature"]) is not str
                or not hmac.compare_digest(approval["signature"], _sign(self._approver_key, payload))):
            raise ValueError("invalid independent approval")
        with self._guard():
            evaluation = self._read_signed(self.evaluation_path)
            with self._readonly() as db:
                current, count, head = self._ledger_identity(db)
                if (request.get("head") != head or request.get("evaluation_mac") != self._mac(evaluation)
                        or evaluation.get("ledger_count") != count
                        or evaluation.get("report", {}).get("status") != "DEGRADED"):
                    raise ValueError("stale rollback request")
                previous = self._historical_state(db, request["count"])
            # Call original non-destructive override writer without nested flock.
            override = {"version": 1, "ledger_count": count, "ledger_head": head,
                        "state": asdict(previous), "evaluation_mac": self._mac(evaluation)}
            self._write_signed_new(self.override_path, override)
            return previous

    def activate_rollback(self, previous_state):
        raise ValueError("untrusted caller-supplied rollback forbidden; use approved replay")
