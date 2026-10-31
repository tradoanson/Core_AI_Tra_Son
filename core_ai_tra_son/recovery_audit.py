"""Signed, deterministic, caller-persisted recovery audit chain; SHADOW only."""
import hashlib
import hmac
import json
from dataclasses import dataclass, asdict

from .recovery_governance import RecoveryGovernance

def _blob(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

@dataclass(frozen=True)
class AuditEntry:
    sequence: int
    from_phase: str
    to_phase: str
    reviewer: str
    evidence_digest: str
    previous_hash: str
    signature: str

class RecoveryAudit:
    def __init__(self, key):
        if type(key) is not bytes or len(key) < 32:
            raise ValueError("audit signing key required")
        self._key = key

    def _signature(self, payload):
        return hmac.new(self._key, _blob(payload), hashlib.sha256).hexdigest()

    def verify(self, entries):
        if type(entries) not in (tuple, list):
            raise ValueError("invalid audit")
        phase, prev = "PROPOSED", "0"*64
        for index, entry in enumerate(entries, 1):
            if (type(entry) is not AuditEntry or entry.sequence != index
                    or entry.from_phase != phase or entry.previous_hash != prev
                    or type(entry.reviewer) is not str or not 1 <= len(entry.reviewer) <= 64
                    or not all(c.isalnum() or c in "_-" for c in entry.reviewer)
                    or type(entry.evidence_digest) is not str or len(entry.evidence_digest) != 64
                    or any(c not in "0123456789abcdef" for c in entry.evidence_digest)):
                raise ValueError("invalid audit chain")
            payload = {k:v for k,v in asdict(entry).items() if k != "signature"}
            if not hmac.compare_digest(self._signature(payload), entry.signature):
                raise ValueError("audit signature mismatch")
            if entry.to_phase != {"PROPOSED":"REVIEWED", "REVIEWED":"APPROVED",
                                  "APPROVED":"ACTIVE", "ACTIVE":"CLOSED"}.get(phase):
                raise ValueError("invalid audit transition")
            prev = hashlib.sha256(_blob(asdict(entry))).hexdigest()
            phase = entry.to_phase
        return phase

    def append(self, entries, *, target, reviewer, evidence,
               evidence_valid=False, independent_reviewer=False,
               independent_approver=False, override_valid=False, closure_reviewed=False):
        phase = self.verify(entries)
        decision = RecoveryGovernance.transition(phase, target, evidence_valid=evidence_valid,
                 independent_reviewer=independent_reviewer,
                 independent_approver=independent_approver,
                 override_valid=override_valid, closure_reviewed=closure_reviewed)
        if not decision.eligible:
            raise ValueError(decision.reason)
        if type(evidence) is not bytes or not evidence or len(evidence) > 65536:
            raise ValueError("bounded evidence bytes required")
        if type(reviewer) is not str or not 1 <= len(reviewer) <= 64 or not all(c.isalnum() or c in "_-" for c in reviewer):
            raise ValueError("invalid reviewer")
        prev = hashlib.sha256(_blob(asdict(entries[-1]))).hexdigest() if entries else "0"*64
        payload = {"sequence":len(entries)+1,"from_phase":phase,"to_phase":target,
                   "reviewer":reviewer,"evidence_digest":hashlib.sha256(evidence).hexdigest(),
                   "previous_hash":prev}
        entry = AuditEntry(**payload, signature=self._signature(payload))
        return tuple(entries)+(entry,)
