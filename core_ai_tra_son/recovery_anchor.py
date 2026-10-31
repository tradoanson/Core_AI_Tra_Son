"""Independent caller-held signed audit-head anchor; no host actions."""
import hashlib
import hmac
import json
from dataclasses import dataclass, asdict
from .recovery_audit import RecoveryAudit

@dataclass(frozen=True)
class AuditAnchor:
    count: int
    head_sha256: str
    mac: str

def _head(entries):
    if not entries:
        return "0"*64
    return hashlib.sha256(json.dumps(asdict(entries[-1]),sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _seal(key,count,head):
    return hmac.new(key,(str(count)+":"+head).encode(),hashlib.sha256).hexdigest()

def issue_anchor(audit, entries, *, anchor_key):
    if type(audit) is not RecoveryAudit or type(anchor_key) is not bytes or len(anchor_key) < 32:
        raise ValueError("independent audit anchor key required")
    audit.verify(entries)
    return AuditAnchor(len(entries),_head(entries),_seal(anchor_key,len(entries),_head(entries)))

def verify_anchor(audit, entries, anchor, *, anchor_key):
    if type(anchor) is not AuditAnchor or type(anchor_key) is not bytes or len(anchor_key) < 32:
        raise ValueError("invalid anchor")
    audit.verify(entries)
    if len(entries) != anchor.count or _head(entries) != anchor.head_sha256:
        raise ValueError("audit truncation or divergent head")
    if not hmac.compare_digest(_seal(anchor_key,anchor.count,anchor.head_sha256),anchor.mac):
        raise ValueError("audit anchor authentication failed")
    return True
